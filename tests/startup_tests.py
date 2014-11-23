'''
Created on Nov 22, 2014

@author: dlaidlaw
'''
from docker_registry_index.dynamodb import Index
import json
import unittest


class Test(unittest.TestCase):


    def setUp(self):
        self.index = Index()



    def tearDown(self):
        pass


    def testVersionIs1(self):
        assert self.index.version == 1
    
    def testContainsRepositoryDojoBase(self):
        results = self.index.results('dojo_base')
        assert len(results) > 0
    
    def testPrintFullRepositoryList(self):
        results = self.index.results()
        print json.dumps(results, indent=4)


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()