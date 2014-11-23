'''
Created on Nov 16, 2014

@author: dlaidlaw
'''

from docker_registry.lib import config
import os

_config = {}
        
def _get_or_set(name, value, env_name = None):
    global _config
    if name in _config:
        return _config[name]
    keys = name.split('.')
    result = _config
    for key in keys:
        if key in result:
            result = result[key]
        else:
            if env_name is None:
                env_name = name.upper()
            result = os.environ.get(env_name, value)
            _config[name] = result
            break
    
    return result
    
def load():
    global _config
    reg_config = config.load()
    dbname = _get_or_set('extensions.dynamodb_index.database', 'docker-registry', 'DYNAMODB_DATABASE')
    _get_or_set('extensions.dynamodb_index.repository_table', dbname + '-repository', 'DYNAMODB_REPOSITORY_TABLE')
    _get_or_set('extensions.dynamodb_index.version_table', dbname + '-version', 'DYNAMODB_REPOSITORY_TABLE')
    region = _get_or_set('extensions.dynamodb_index.region', reg_config.s3_region, 'DYNAMODB_REGION')
    if region is None:
        _config['extensions.dynamodb_index.region'] = 'us-east-1'
    _get_or_set('extensions.dynamodb_index.access_key', reg_config.s3_access_key, 'DYNAMODB_ACCESS_KEY')
    _get_or_set('extensions.dynamodb_index.secret_access_key', reg_config.s3_secret_access_key, 'DYNAMODB_SECRET_ACCESS_KEY')
    
    return _config
        