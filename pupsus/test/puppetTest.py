'''
Created on Nov 28, 2013

@author: yasn77
'''
import unittest

from pupsus.pupsusconfig import PupsusConfig
from pupsus.puppet import Puppet
import os

testConfigFile = os.environ['PUPSUS_CONFIG']
moduleToGet = os.environ['PUPSUS_MODULE_TO_GET']
moduleVersion = '0.1.0'
modulepath = "/tmp/puppetmodules"
moduleFile = "%s/ibmmq/Modulefile" % (modulepath)
puppet_env = "pupsus_test"


def instantiateClass(**kwargs):
    return Puppet(**kwargs)


def getPuppetModule(p, moduleToGet, modulepath=None):
    return p.installmodule(moduleToGet, modulepath=modulepath)


def getPuppetDepList(p, moduleToGet, modulepath=None):
    return p.getdeplist(moduleToGet, modulepath=modulepath)


def getCurrentVersion(*args, **kwargs):
    p = args[0]
    return p.currentversion(moduleFile)

def getEnvironmentModulePath(*args, **kwargs):
    p = args[0]
    return p.getmodulepath(puppet_env)

def getIsInstalled(*args, **kwargs):
    p = args[0]
    return p.isinstalled(args[1], **kwargs)

def moduleSearch(*args, **kwargs):
    p = args[0]
    return p.search(args[1], **kwargs)


class PuppetTest(unittest.TestCase):
    def setUp(self):
        self.pupsusConfig = PupsusConfig(testConfigFile)
        self.pup = instantiateClass(config=self.pupsusConfig)
        if not os.path.isdir(modulepath):
            os.mkdir(modulepath)

    def tearDown(self):
        pass

    def test_GetPuppetModule(self):
        res = getPuppetModule(self.pup, moduleToGet, modulepath=modulepath)
        self.assertTrue(os.path.isdir(res[1]))

    def test_PuppetDepList(self):
        res = getPuppetDepList(self.pup, moduleToGet, modulepath=modulepath)
        if len(res) == 0:
            print "WARN: No dependencies found for %s when running test_PuppetDepList()" % (moduleToGet)
        self.assertTrue(isinstance(res, frozenset))

    def test_CurrentVersion(self):
        v = getCurrentVersion(self.pup)
        self.assertEqual(v, moduleVersion)
    
    def test_EnvironmentModulePath(self):
        env = getEnvironmentModulePath(self.pup)
        self.assertEqual(env, modulepath)
        
    def test_isInstalled(self):
        installed = getIsInstalled(self.pup, moduleToGet, environment=puppet_env)
        self.assertTrue(installed[0] == True)
        
    def test_Search(self):
        res = moduleSearch(self.pup, moduleToGet, environment=puppet_env)
        self.assertTrue(isinstance(res, dict))
    
    def test_NonExistingPuppetModule(self):
        res = moduleSearch(self.pup, 'some/dodgymodule', environment=puppet_env)
        self.assertEqual(res['some/dodgymodule'][0], None)

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
