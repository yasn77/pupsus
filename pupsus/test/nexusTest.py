'''
Created on Nov 19, 2013

@author: yasn77
'''
import unittest
from pupsus.pupsusconfig import PupsusConfig
from pupsus.nexus import Nexus
import os
import hashlib

testConfigFile = os.environ['PUPSUS_CONFIG']
artifact_id = os.environ['PUPSUS_ARTIFACT_ID']
artifact_group = os.environ['PUPSUS_ARTIFACT_GROUP']


def instantiateClass(**kwargs):
    return Nexus(**kwargs)


def searchNexus(*args, **kwargs):
    n = args[0]
    return n.search(**kwargs)


def getArtifact(*args, **kwargs):
    n = args[0]
    return n.getartifact(**kwargs)


def getVesions(*args, **kwargs):
    n = args[0]
    return n.getversions(**kwargs)


def matchArtifactSha(artifact):
    sha1 = hashlib.sha1()
    try:
        f = open(artifact[0], 'rb')
        sha1.update(f.read())
    finally:
        f.close()
    if sha1.hexdigest() == artifact[1]:
        return True
    else:
        return False


class NexusTest(unittest.TestCase):

    def setUp(self):
        self.pupsusConfig = PupsusConfig(testConfigFile)
        self.n = instantiateClass(url=self.pupsusConfig.get('nexus_url'),
                                  cache_dir=self.pupsusConfig.get('cache_dir'))

    def tearDown(self):
        pass

    def test_searchForArtifact(self):
        hasKeys = True
        missingKey = ''
        res = searchNexus(self.n,
                          artifact_group=artifact_group,
                          artifact_id=artifact_id,
                          repository='releases')
        for k in ('groupId',
                  'artifactId',
                  'version',
                  'extension',
                  'sha1',
                  'repositoryPath',
                  'repository'):
            if not k in res:
                hasKeys = False
                missingKey = k
                break
        self.assertTrue(hasKeys,
                        "%s key is missing from search result" % missingKey)

    def test_serachForNonExistingArtifact(self):
        res = searchNexus(self.n,
                          artifact_group='some.group',
                          artifact_id='foo',
                          repository='releases')
        self.assertFalse(artifact_id in res, False)

    def test_getArtifact(self):
        res = getArtifact(self.n,
                          artifact_group=artifact_group,
                          artifact_id=artifact_id,
                          repository='releases')
        if res[0] == 'item not found':
            self.fail(res[0])
        else:
            self.assertEqual(os.path.isfile(res[0]), matchArtifactSha(res))

    def test_getVersions(self):
        res = getVesions(self.n,
                          artifact_group=artifact_group,
                          artifact_id=artifact_id,
                          repository='releases'
                          )
        if len(res) < 1:
            self.fail("No versions found")
        else:
            self.assertTrue(isinstance(res, tuple))

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
