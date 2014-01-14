'''
Created on Nov 27, 2013

@author: yasn77
'''

from pupsusconfig import PupsusConfig
from puppet import Puppet
import argparse
import os



class Pupsus():
    
    def __init__(self):
        if 'PUPSUS_CONFIG' in os.environ:
            configfile = os.environ['PUPSUS_CONFIG']
        else:
            configfile = '/etc/pupsus/pupsus.ini'
        pupsusConfig = PupsusConfig(configfile)
        parser = argparse.ArgumentParser()
        subparsers = parser.add_subparsers(title='Commands', dest='command')
        
        parser_install = subparsers.add_parser('install', help='Install a Puppet module')
        parser_install.add_argument('modulename', help='Puppet Module name, following PuppetForge naming convention',
                                      action=self.__checkArgModuleName__())
        parser_install.add_argument('-v', '--version', default='LATEST')
        parser_install.add_argument('--force', action='store_true')
        
        parser_search = subparsers.add_parser('search', help='Search for a Puppet module')
        parser_search.add_argument('modulename', help='Puppet Module name, following PuppetForge naming convention',
                                      action=self.__checkArgModuleName__())
        
        parser_installenv = subparsers.add_parser('installenv', help='Install all modules for a Puppet environment')
        
        parser_remove = subparsers.add_parser('remove', help='Remove a module')
        parser_remove.add_argument('modulename', help='Puppet Module name, following PuppetForge naming convention',
                                  action=self.__checkArgModuleName__())
        
        parser.add_argument('-u', '--nexus-url', dest='nexus_url',
                            help='URL to Nexus', action=self.__addToConfig__(pupsusConfig))
        parser.add_argument('-g', '--artifact-group', dest='artifact_group',
                            help='Artifact group for modules', action=self.__addToConfig__(pupsusConfig))
        parser.add_argument('-d', '--cache-dir', dest='cache_dir',
                            help='Directory used to store cache information', action=self.__addToConfig__(pupsusConfig))
        parser.add_argument('-e,', '--environment', default='production',
                            help='Puppet environment queried for Modulepath')
        parser.add_argument('-m', '--modulepath', dest='puppet_modulepath', help='Puppet Module path, please note if \
                            environment is specified, then the modulepath from Puppet \
                            environment will used', default=None, action=self.__addToConfig__(pupsusConfig, section='puppet'))
        parser.add_argument('-f', '--puppet-config', dest='puppet_config',
                            help='Puppet configuration file. Note: If multiple \
                            module paths are listed, then only the first path is used', action=self.__addToConfig__(pupsusConfig, section='puppet'))
        parser.add_argument('-p', '--puppet-command', dest='puppet_command',
                            help='Path to Puppet command', action=self.__addToConfig__(pupsusConfig, section='puppet'))
        args = parser.parse_args()
        self.config = pupsusConfig
        self.puppet = Puppet(config=self.config)
        
        __COMMAND_TO_METHOD_MAP = {
                                   'install' : lambda: self.install(args.modulename, args.environment, version=args.version),
                                   'search'  : lambda: self.search(args.modulename, args.environment),
                                   'remove'  : lambda: self.remove(args.modulename, args.environment),
                                   'installenv' : lambda: self.installenv(args.environment),
                                  }

        if args.command in __COMMAND_TO_METHOD_MAP:
            __COMMAND_TO_METHOD_MAP.get(args.command)()
        else:
            parser.error('Command not yet implemented')
        
    def __checkArgModuleName__(self):
        class checkArgModuleName(argparse.Action):
            def __call__(self, parser, args, values, option_string=None):
                if not len(values.split('/')) == 2:
                    parser.error('incorrect modulename')
                else:
                    setattr(args, self.dest, values)
        return checkArgModuleName
            
        
    def __addToConfig__(self, pupsusconfig, section=None):
        class addToConfig(argparse.Action):
            def __call__(self, parser, args, values, option_string=None):
                if not section is None:
                    key = self.dest.split('_')
                    pupsusconfig.update(key[1], values, section=section)
                else:
                    pupsusconfig.update(self.dest, values)
                setattr(args, self.dest, values)
        return addToConfig
    
    def install(self, modulename, environment, version='LATEST'):
        modulepath = self.puppet.getmodulepath(environment)
        ret = self.puppet.installmodule(modulename, modulepath=modulepath, version=version)
        print('%s installed' % ret[0] if ret != 'item not found' else '%s : %s v%s' % (ret, modulename, version))
    
    def search(self, modulename, environment):
        # No support for Fuzzy search... need to fix
        search_res = self.puppet.search(modulename, environment=environment)
        print "Note: version in parenthesis indicates the version that is currently installed"
        for s in search_res:
            versions = ', '.join(search_res[s]) if search_res[s][0] != None else 'No version found'
            print "%s : %s" % (s, versions)

    def installenv(self, environment):
        import yaml
        envfile = "%s/%s.env" % (self.puppet.puppetconf['environments'][environment], environment)
        f = open(envfile, 'r')
        mods = yaml.safe_load(f)
        for m in mods:
            version = mods[m]
            if version == 'latest':
                version = version.swapcase()
            self.install(m, environment, version=version)
            
    
    def remove(self, modulename, environment, force=False):
        pass

def main():
    Pupsus()

if __name__ == '__main__':
    main()
