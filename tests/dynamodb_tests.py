from docker_registry_index.dynamodb import Index
import json
import unittest

#
# Unfortunately, this is an integration test and must actually communicate with
# the Amazon AWS DynamoDB service. 
#
#

class DynamoDBIndexTests(unittest.TestCase):
    """Test the DynamoDB Index
    Don't forget to set up the boto config with your security credentials.
    See http://boto.readthedocs.org/en/latest/boto_config_tut.html
    """
    
    def setUp(self):
        self.index = Index()
    
    def tearDown(self):
        repo = self.index._repositoryTable
        results = repo.scan()
        keys = [row['name'] for row in results]
        with repo.batch_write() as batch:
            for name in keys:
                batch.delete_item(name=name)
        self.index = None
        
    
    #aws_access_key_id='see ~/.boto'
    #aws_secret_access_key='see ~/.boto'

    def test_schema_version(self):
        assert self.index.version == 1
    
    def test_create_repository(self):
        self.index._handle_repository_created(None, 'library', 'my-repo', None)
        repos = self.index.results()
        assert repos is not None
        assert len(repos) == 1
        assert repos[0]['name'] == 'library/my-repo'
        assert repos[0]['description'] is None
        
        self.index._handle_repository_deleted(None, 'library', 'my-repo')
        repos = self.index.results(search_term = None)
        assert repos is not None
        assert len(repos) == 0

    def test_query_repos(self):
        index = self.index        
        allRepos = [{'namespace': 'library', 'name': 'repo1'},
                     {'namespace': 'library', 'name': 'repo2'},
                     {'namespace': 'dlaidlaw', 'name': 'repo1'},
                     {'namespace': 'dlaidlaw', 'name': 'repo2'},
                     {'namespace': 'arthur', 'name': 'dent1'},
                     {'namespace': 'arthur', 'name': 'dent2'},
                     ]
        
        for repo in allRepos:
            index._handle_repository_created(None, repo['namespace'], repo['name'], None)
        
        repos = index.results()
        assert repos is not None
        assert len(repos) == len(allRepos)
        
        index._handle_repository_updated(None, 'dlaidlaw', 'repo2', 'Second repo')
        
        repos = index.results(search_term='repo')
        assert repos is not None
        assert len(repos) == 4
        
        repos = index.results(search_term='dlaidlaw')
        assert repos is not None
        assert len(repos) == 2
        
        repos = index.results(search_term='dlaidlaw/repo2')
        assert repos is not None
        assert len(repos) == 1
        assert repos[0]['description'] is None


if __name__ == '__main__':
    unittest.main()