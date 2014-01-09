'''
Created on Nov 27, 2013

@author: yasn77
'''

# Reference: http://blog.sonatype.com/people/2008/11/searching-with-the-sonatype-nexus-rest-api-python

import requests
import requests_cache
from xml.etree import ElementTree
from xml.etree import ElementPath
import os


class Nexus(object):
    '''
    classdocs
    '''

    def __init__(self, proxies={}, cert=(), verify=True, **kwargs):
        '''
        Constructor
        '''

        if ('user' in kwargs and 'pass' in kwargs):
            auth = (kwargs['user'], kwargs['pass'])
        else:
            auth = None
        self.cacheDir = kwargs.get('cache_dir', '/var/cache/pupsus')
        useTmpCache = False
        if not os.path.isdir(self.cacheDir):
            try:
                os.mkdir(self.cacheDir)
            except:
                print "WARN: Can not create %s, using /tmp/pupsus" % (self.cacheDir)
                self.cacheDir = '/tmp/pupsus'
                useTmpCache = True
        if (not os.access(self.cacheDir, os.W_OK) and self.cacheDir != '/tmp/pupsus'):
            print "WARN: Can't write to cache directory: %s, using /tmp/pupsus" % (self.cacheDir)
            self.cacheDir = '/tmp/pupsus'
            useTmpCache = True
        if useTmpCache and not os.path.isdir(self.cacheDir):
            os.mkdir(self.cacheDir)
        cacheName = "%s/pupsus_requests_cache" % (self.cacheDir)
        requests_cache.install_cache(
                                     cache_name=cacheName,
                                     backend='sqlite',
                                     expire_after=604800,
                                     fast_save=True,
                                     extension='.cache'
                                     )
        reqS = requests.Session()
        reqS.auth = auth
        reqS.cert = kwargs.get('cert', (None, None))
        reqS.proxies = kwargs.get('proxies', dict())
        self.nexus_url = kwargs['url']
        self.nexus_host = self.nexus_url.split('/')[2]
        self.reqS = reqS
        self.downloadTopDir = '%s/%s' % (self.cacheDir, self.nexus_host)
        try:
            if not os.path.isdir(self.downloadTopDir):
                os.mkdir(self.downloadTopDir)
        except:
            self.downloadTopDir = self.cacheDir

    def __buildURI(self, **kwargs):
        if not 'mountpoint' in kwargs:
            raise KeyError('mountpoint is required option for __buildURI')
        if 'version' in kwargs and kwargs['version'] == 'any':
            return '%s%s?g=%s&a=%s&r=%s&p=%s&e=%s' % (
                                          self.nexus_url,
                                          kwargs['mountpoint'],
                                          kwargs.get('artifact_group', None),
                                          kwargs.get('artifact_id', None),
                                          kwargs.get('repository', 'releases'),
                                          kwargs.get('packaging', 'tgz'),
                                          kwargs.get('extension', 'tgz')
                                          )
        else:
            return '%s%s?g=%s&a=%s&v=%s&r=%s&p=%s&e=%s' % (
                                            self.nexus_url,
                                            kwargs['mountpoint'],
                                            kwargs.get('artifact_group', None),
                                            kwargs.get('artifact_id', None),
                                            kwargs.get('version', 'LATEST'),
                                            kwargs.get('repository', 'releases'),
                                            kwargs.get('packaging', 'tgz'),
                                            kwargs.get('extension', 'tgz')
                                            )

    def search(self, **kwargs):
        k = (
             'groupId',
             'artifactId',
             'version',
             'extension',
             'sha1',
             'repositoryPath'
             )
        doc = dict()
        req_url = self.__buildURI(mountpoint='/service/local/artifact/maven/resolve', **kwargs)
        req = self.reqS.get(req_url)
        if req.status_code == 200:
            data = req.text
        else:
            return doc
        try:
            xml = ElementTree.XML(data)
            d = ElementPath.findall(xml, './/data')[0]
            for i in k:
                doc[i] = d.find(i).text
            doc['repository'] = kwargs['repository']
        except:
            pass
        return doc

    def getartifact(self, **kwargs):
        artifactGav = self.search(**kwargs)
        if len(artifactGav.keys()) > 1:
            downloadUrl = "%s/content/repositories/%s/%s" % (
                                                             self.nexus_url,
                                                             artifactGav['repository'],
                                                             artifactGav['repositoryPath']
                                                             )
        else:
            return ['item not found']
        downloadFileName = '%s/%s' % (self.downloadTopDir, artifactGav['sha1'])
        if not os.path.isfile(downloadFileName):
            with requests_cache.disabled():
                req = self.reqS.get(downloadUrl)
            try:
                f = open(downloadFileName, 'w')
                f.write(req.content)
                f.close
            except:
                raise
        modulename = "%s-%s" % (artifactGav['artifactId'],
                                artifactGav['version'])
        return (downloadFileName, artifactGav['sha1'], modulename)

    def getversions(self, **kwargs):
        versions = ()
        kwargs['version'] = 'any'
        req_url = self.__buildURI(mountpoint='/service/local/lucene/search', **kwargs)
        with requests_cache.disabled():
            req = self.reqS.get(req_url)
        if req.status_code == 200:
            data = req.text
        else:
            return versions
        try:
            xml = ElementTree.XML(data)
            for item in ElementPath.findall(xml, './/artifact'):
                if item.find('artifactId').text == kwargs['artifact_id']:
                    versions = versions + (item.find('version').text,)
        except:
            pass
        return versions
