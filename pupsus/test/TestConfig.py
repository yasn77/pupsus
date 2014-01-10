import unittest
from pupsus.pupsusconfig import PupsusConfig
import re
from os import environ

testConfigFile = environ['PUPSUS_CONFIG']


def instantiateClass():
    return PupsusConfig(configfile=testConfigFile)


def getNexusUrl():
    config = PupsusConfig(configfile=testConfigFile)
    return config.get('nexus_url')


def getArtifactGroup():
    config = PupsusConfig(configfile=testConfigFile)
    return config.get('artifact_group')


def getCacheDir():
    config = PupsusConfig(configfile=testConfigFile)
    return config.get('cache_dir')


def updateConfig():
    config = PupsusConfig(configfile=testConfigFile)
    config.update('foo', 'bar')
    return config.get('foo')


class ConfigTest(unittest.TestCase):

    def testConfigObject(self):
        self.failUnless(instantiateClass())

    def test_NexusUrl(self):
        nexus_host = getNexusUrl()
        self.assertTrue(re.search('^(http|https)://.*', nexus_host))

    def test_ArtifactGroup(self):
        artifact_group = getArtifactGroup()
        self.assertTrue(isinstance(artifact_group, basestring))

    def test_CacheDir(self):
        cache_dir = getCacheDir()
        self.assertTrue(isinstance(cache_dir, basestring))

    def test_UpdateConfig(self):
        res = updateConfig()
        self.assertEqual(res, 'bar')


def main():
        unittest.main()

if __name__ == '__main__':
    main()
