# -*- coding: utf-8 -*-

"""A DynamoDB backend for the docker-repository search endpoint
"""


from time import sleep

from boto import dynamodb2
from boto.dynamodb2.fields import HashKey, GlobalAllIndex
from boto.dynamodb2.table import Table
from boto.dynamodb2.types import STRING, NUMBER

from docker_registry.lib.index import Index as Base
from docker_registry import storage

from docker_registry_index import dynamodb_config
from docker_registry_index import dynamodb_util

import logging
from threading import Lock

logger = logging.getLogger(__name__)

class Index(Base):
    '''An Index for docker-registry that uses Amazon AWS DynamoDB as the storage engine.
    
    Boto is used to do all access to DynamoDB.
    
    Configure the following dynamodb_config variables or environment variables:
    
    dynamodb_index_database - optional, if not specified will default to 'docker-registry'
        and the repository and version table names will be constructed using the
        {dynamodb_index_database}-repository and {dynamodb_index_database}-version.
        DynamoDB does not have a database concept, just tables in the data store.
    
    dynamodb_index_repository_table - override the default table name (above) with a new name
    
    dynamodb_index_version_table - override the default table name with a new name
    
    dynamodb_region - the AWS region for the dynamodb. This will default to the s3_region and if
        that is not defined, it defaults to 'us-east-1'.
    
    dynamodb_access_key - the AWS access key to use
    
    dynamodb_secret_access_key - the AWS secret part of the access key
    '''
    
    _initLock = Lock()

    def __init__(self, database=None, dynamodb_access_key=None, dynamodb_secret_access_key=None):
        '''
        Constructor
        '''
        cfg = dynamodb_config.load()
        if database is None:
            database = cfg['extensions.dynamodb_index.database']
        if dynamodb_access_key is None:
            dynamodb_access_key = cfg['extensions.dynamodb_index.access_key']
        if dynamodb_secret_access_key is None:
            dynamodb_secret_access_key = cfg['extensions.dynamodb_index.secret_access_key']
        
        self.repositoryTableName = cfg['extensions.dynamodb_index.repository_table']
        self.versionTableName = cfg['extensions.dynamodb_index.version_table']
        
        if dynamodb_access_key is None:
            self._db = dynamodb2.connect_to_region(cfg['extensions.dynamodb_index.region'])
        else:
            self._db = dynamodb2.connect_to_region(cfg['extensions.dynamodb_index.region'],
                                                   aws_access_key_id=dynamodb_access_key,
                                                   aws_secret_access_key=dynamodb_secret_access_key)
        
        self._repositoryTable = Table(self.repositoryTableName,
                                     schema=[HashKey('name', data_type=STRING)],
                                     global_indexes=[GlobalAllIndex('Repositories-By-Description-Index',
                                                                    parts=[HashKey('description', data_type=STRING)])],
                                     connection=self._db)
        self._versionTable = Table(self.versionTableName,
                                  schema=[HashKey('version', data_type=NUMBER)],
                                  connection=self._db)

        self.version = 1
        Index._initLock.acquire()
        try:
            self._setup_database()
        finally:
            Index._initLock.release()
        super(Index, self).__init__()
    
    def _describe_or_create_tables(self):
        dynamodb_util.create_table_if_not_exists(self._repositoryTable)
        dynamodb_util.create_table_if_not_exists(self._versionTable)

            
    def _wait_for_tables(self):
        dynamodb_util.wait_for_table_active(self._repositoryTable)
        dynamodb_util.wait_for_table_active(self._versionTable)
    
    def _read_or_set_schema_version(self, default_version):
        def read_schema_version():
            v = 0
            try:
                results = self._versionTable.scan()
                row = results.next()
                v = row['version']
            except:
                v = -1
            return v

        # Read or insert the schema_version. Keep doing it until one
        # of them works. This is in case another thread is attempting the same
        # thing. Reading first will allow this thread to complete.
        schemaVersion = read_schema_version()
        while (schemaVersion <= 0):
            try:
                self._versionTable.put_item(data={'version': default_version})
                schemaVersion = default_version
            except:
                sleep(0.5)
                schemaVersion = read_schema_version()
                
        return schemaVersion
    
    
    def _setup_database(self):
        needs_index = not dynamodb_util.table_exists(self._versionTable)
        self._describe_or_create_tables()
        self._wait_for_tables()
        
        version = self._read_or_set_schema_version(self.version)
        if (version != self.version):
            raise NotImplementedError('unrecognized search index version {0}'.format(version))
        if needs_index:
            self._generate_index()
        
    def _generate_index(self):
        store = storage.load()
        with self._repositoryTable.batch_write() as batch:
            for repository in self._walk_storage(store=store):
                logger.info('Populating repository: {0}'.format(repository['name']))
                batch.put_item(data=repository)
        
    def _handle_repository_created(
            self, sender, namespace, repository, value):
        name = '{0}/{1}'.format(namespace, repository)
        description = ''  # TODO(wking): store descriptions
        logger.info('Creating new repository {0}'.format(name))
        self._repositoryTable.put_item(data={'name': name, 'description': description})

    def _handle_repository_updated(
            self, sender, namespace, repository, value):
        name = '{0}/{1}'.format(namespace, repository)
        description = ''  # TODO(wking): store descriptions
        logger.info('Updating repository {0}'.format(name))
        repo = self._repositoryTable.get_item(name=name)
        repo['description'] = description
        repo.save(overwrite=True)
        

    def _handle_repository_deleted(self, sender, namespace, repository):
        name = '{0}/{1}'.format(namespace, repository)
        logger.info('Deleting repository {0}'.format(name))
        self._repositoryTable.delete_item(name=name)

    def results(self, search_term=None):
        """Return a list of results matching search_term

        The list elements should be dictionaries:

          {'name': name, 'description': description}
        """
        if search_term is None:
            logger.info('Index query: full table scan')
            repositories = self._repositoryTable.scan()
        else:
            logger.info('Index query: {0}'.format(search_term))
            repositories = self._repositoryTable.scan(conditional_operator='OR',
                                                      name__contains=search_term,
                                                      description__contains=search_term)

        if repositories:
            return [{'name': repo['name'],
                     'description': repo['description'],
                     } for repo in repositories]
       
        return []
