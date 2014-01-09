'''
Created on 18 Nov 2013

@author: yasser
'''

import os

class PupsusConfig(object):
    '''
    classdocs
    '''

    def __init__(self, configfile=None):
        if configfile != None and os.path.isfile(configfile):
            self.configfile = configfile
            self.config = self.__loadConfig(self.configfile)
        else:
            self.config = {}

    def __loadConfig(self, f):
        import ConfigParser
        try:
            c = ConfigParser.ConfigParser()
            c.readfp(open(f))
        except IOError, e:
            raise e
        try:
            config = dict(c.items('pupsus_main'))
            if c.has_section('puppet'):
                config['puppet'] = dict(c.items('puppet'))
        except:
            raise
        finally:
            del c
        return config

    def get(self, key, section=None):
        if section is None:
            return self.config[key]
        else:
            return self.config[section][key]

    def update(self, k, v, section=None):
        r = False
        try:
            if section is None:
                self.config[k] = v
                r = True if self.config[k] == v else False
            else:
                self.config[section][k] = v
                r = True if self.config[section][k] == v else False
        except:
            pass

        return r
        
    def updatesection(self, section, key, value):
        try:
            self.config[section][key] = value
        except:
            return False
        if self.config[section][key] == value:
            return True
        else:
            return False
