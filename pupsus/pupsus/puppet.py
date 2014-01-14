'''
Created on Nov 28, 2013

@author: yasn77
'''

from nexus import Nexus
import tarfile
import os
import semantic_version
import sys
import re
import StringIO
import ConfigParser
from shutil import rmtree
import subprocess
import yaml

class Puppet(object):

    '''
    classdocs
    '''

    def __init__(self, **kwargs):
        '''
        Constructor
        '''
        yaml.add_multi_constructor(u"!ruby/object:", self.__construct_ruby_object)
        yaml.add_constructor(u"!ruby/sym", self.__construct_ruby_sym)
        if not 'config' in kwargs:
            raise KeyError('config object is required by Puppet Class')
        else:
            self.__config = kwargs['config']
        self.puppetconf = self.__config.get('puppet')
        self.nex = Nexus(url=self.__config.get('nexus_url'),
                         cache_dir=self.__config.get('cache_dir'))
        
        self.defaultModulePath = '%s/modules' % os.path.dirname(self.puppetconf['config'])
        try:
            c = ConfigParser.ConfigParser()
            if 'config' in self.puppetconf:
                if sys.version_info[0] < 3:
                    # ConfigParser in versions < 3 don't like leading white space, most default
                    # Puppet config use leading white space :/
                    no_leading_whitespace = re.sub('\ +|\t+', '', open(self.puppetconf['config'], 'r').read())
                    pcf = StringIO.StringIO(no_leading_whitespace)
                    c.readfp(pcf)
                else:
                    c.readfp(self.puppetconf['config'])   
        except:
            raise
        self.puppetconf['environments'] = {}
        for section in c.sections():
            if section not in ['main', 'agent', 'master', 'user', 'puppetmasterd']:
                self.puppetconf['environments'][section] = c.get(section, 'modulepath')
        self.puppetconf['environments']['production'] = self.defaultModulePath
    
    def __construct_ruby_object(self, loader, suffix, node):
        return loader.construct_yaml_map(node)

    def __construct_ruby_sym(self, loader, node):
        return loader.construct_yaml_str(node)

    def __extract(self, tarball=None, modulename=None, force=False):
        exctractedPath = '%s/%s' % (os.path.dirname(tarball), modulename)
        try:
            if not os.path.isdir(exctractedPath):
                tf = tarfile.open(tarball, mode='r:gz')
                tf.extractall(os.path.dirname(tarball))
                tf.close()
        except:
            raise
        return exctractedPath

    def __getmodule(self, m, **kwargs):
            modulename = m.split('/')[1]
            artifact_id = "%s-%s" % (m.split('/')[0], modulename)
            artifact_group = self.__config.get('artifact_group')
            version = kwargs.get('version', 'LATEST')
            repository = self.__config.get('nexus_repository')
            if not 'artifact_group' in kwargs:
                kwargs['artifact_group'] = self.__config.get('artifact_group')
            if not 'repository' in kwargs:
                kwargs['repository'] = self.__config.get('nexus_repository')
            return self.nex.getartifact(
                                        artifact_group=artifact_group,
                                        artifact_id=artifact_id,
                                        repository=repository,
                                        version=version
                                        )

    def __bestVersion(self, *args, **kwargs):
        availableVersions = self.nex.getversions(**kwargs)
        versions = (semantic_version.Version('%s' % i) for i in availableVersions)
        s = semantic_version.Spec(args[0])
        bv = s.select(versions)
        return bv.__str__()
    
    def isinstalled(self, module, environment=None):
        moduleInstalled = [False, None]
        modulepath = self.getmodulepath(environment)
        CMD = [self.puppetconf['command'], 'module', 'list', '--render', 'yaml', '--modulepath', modulepath]
        try:
            p = subprocess.Popen(CMD, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            output = p.communicate()
        finally:
            pass
        y = yaml.load(output[0])
        for m in y[modulepath]:
            if m['forge_name'] == module:
                moduleInstalled[0] = True
                moduleInstalled[1] = m['version']
        return tuple(moduleInstalled)

    def currentversion(self, modulefile):
        moduleversion = '0'
        if os.path.isfile(modulefile):
            try:
                mf = open(modulefile, 'r')
                for line in mf.readlines():
                    if 'version' == line.split(' ')[0]:
                        moduleversion = line.split(' ')[1].strip("'\n")
            except:
                raise
            finally:
                mf.close()
        return moduleversion
    
    def search(self, m, environment=None, **kwargs):
        # Does not support fuzzy search yet
        result = {}
        result[m] = []
        installed = self.isinstalled(m, environment=environment)
        artifact_id = "%s-%s" % tuple(m.split('/'))
        artifact_group = kwargs.get('artifact_group', self.__config.get('artifact_group'))
        version = kwargs.get('version', 'LATEST')
        repository = kwargs.get('repository', self.__config.get('nexus_repository'))
        nex_result = list( self.nex.getversions(
                                            artifact_group=artifact_group,
                                            artifact_id=artifact_id,
                                            repository=repository,
                                            version=version
                                            ) )
        nex_result.sort()
        for i in range(len(nex_result)):
            if installed[1] == nex_result[i]:
                nex_result[i] = "(%s)" % installed[1]
            result[m].append(nex_result[i])
        result[m] = tuple(result[m])

        if len(result[m]) == 0:
            result[m] = (None,) 
        return result     
    
    def getmodulepath(self, environment):
        return self.puppetconf['environments'][environment].split(':')[0]

    def getdeplist(self, m, **kwargs):
        dep = {}
        res = self.__getmodule(m, **kwargs)
        if res[0] != 'item not found':
            tf = tarfile.open(res[0], mode='r:gz')
            try:
                mf = tf.extractfile("%s/Modulefile" % (res[2]))
                for line in mf.readlines():
                    if 'dependency' == line.split(' ')[0]:
                        depMod = line.split(' ')[1].strip(",'")
                        depVer = ''.join(line.split(' ')[2:]).strip()
                        depVer = depVer.strip("'")
                        v = self.__bestVersion(depVer, **kwargs)
                        dep[depMod] = v
            finally:
                tf.close()
            return frozenset(dep.items())
        else:
            return res

    def installmodule(self, m, **kwargs):
        modulename = m.split('/')[1]
        modulepath = kwargs.get('modulepath', self.defaultModulePath)
        version = kwargs.get('version', 'LATEST')
        force = kwargs.get('force', False) if version != 'LATEST' else True
        currentver = self.currentversion("%s/%s/Modulefile" % (modulepath, modulename))
        depList = self.getdeplist(m, **kwargs)
        if not os.path.isdir("%s/%s" % (modulepath, modulename)) or force == True or ( currentver != version and version != 'LATEST' ):
            if not os.access(modulepath, os.W_OK):
                raise IOError
            res = self.__getmodule(m, version=version)
            if len(res) > 1:
                try:
                    e = self.__extract(tarball=res[0], modulename=res[2])
                    try:
                        rmtree("%s/%s" % (modulepath, modulename))
                    except:
                        pass
                    os.rename(e, "%s/%s" % (modulepath, modulename))
                except:
                    raise
            else:
                return(res[0])
            for d in depList:
                if d[0] != 'item not found':
                    self.installmodule(d[0], modulepath=modulepath)
                    
        return (modulename, "%s/%s" % (modulepath, modulename), depList)
