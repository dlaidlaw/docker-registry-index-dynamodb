Docker-Registry-Index-DynamoDB
==============================

A DynamoDB index for the [docker-registry](https://github.com/docker/docker-registry). By default, docker-registry stores its index using [sqlalchemy](http://www.sqlalchemy.org/) in a relational database. This project provides a module that allows you to store the index in [Amazon AWS DynamoDB](http://aws.amazon.com/dynamodb/). This is particularly useful if you are using docker-registry's Amazon S3 driver for your Image Store. With DynamoDB you will have a high-availability index to match the high-availability image store.

# Table of Contents

- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [Manual install](#manual-install)
- [Implementation Details](#implementation-details)

# Quick start

The easiest way to run this is to install docker, then run the docker image:

    docker pull dlaidlaw/docker-registry-index-dynamodb

Then run the docker image, specifying your settings as environment variables:

	docker run -d \
         -e SEARCH_BACKEND=docker_registry_index.dynamodb \
         -e SETTINGS_FLAVOR=prod \
         -e AWS_REGION=us-east-1 \
         -e AWS_BUCKET=mybucket \
         -e STORAGE_PATH=/registry \
         -e AWS_KEY=myawskey \
         -e AWS_SECRET=myawssecret \
         -p 5000:5000 \
         docker_registry_dynamodb

This will pull the image from the docker hub.

# Configuration

See the [docker-registry](https://github.com/docker/docker-registry) project for details on configuring the docker-registry. This project uses the same configuration mechanism, an you may add the configuration to the same configuration file used by docker-registry. The configuration used by this code is stored in the docker-registry config in the extensions section: For example:

	common: &common
	    # add the following
	    search_backend: docker_registry_index.dynamodb
    
	extensions:
	    dynamodb_index:
	        database: _env:DYNAMODB_DATABASE:docker-registry
	        repository_table: _env:DYNAMODB_REPOSITORY_TABLE
	        version_table: _env:DYNAMODB_VERSION_TABLE
	        region: _env:DYNAMODB_REGION
	        access_key: _env:DYNAMODB_ACCESS_KEY
	        secret_access_key: _env:DYNAMODB_SECRET_ACCESS_KEY

If you do not specify a `repository_table`, then the table name will be formed by adding `-repository` to the end of the `database` name. If you do not specify a `version_table`, then `-version` is added to the `database` name. Note that there is no concept of a database in DynamoDB, the `database` name here is simply used as a prefix for calculating the table names when no table names are specified in the configuration.

The `region` will default to the `s3_region`, which in turn defaults to 'us-east-1'.

The `access_key` and `secret_access_key` default to the value of the `s3_access_key` and `s3_secret_access_key` respectively. If not specified then you must configure these by other means. This code uses [boto Python interface to Amazon Web Services](https://github.com/boto/boto) to access the DynamoDB. Therefore, you can use a boto configuration file in your home directory, or in /etc. For details see the [boto configuration](http://docs.pythonboto.org/en/latest/) documentation.

So if you use the DynamoDB with no configuration specified it will default to using 'docker-registry-repository' as the `respository_table` name, and 'docker-registry-version' as the `version_table` name. The region, access_key and secret_access_key will default to the S3 values or whatever is found in boto configuration. But remember, you must still set the search_backend to docker_registry_index.dynamodb.

# Manual Install

Simply install and run the docker-registry as normal, but first ensure that this python package (docker-registry-index-dynamodb) is installed and set the docker-registry configuration to use it.

* Install docker-registry as normal.
* Install this python package. 
  * Available at PYPI: `pip install docker-registry-index-dynamodb`
* Make sure the docker-registry configuration has the `search_backend` set to `docker_registry_index.dynamodb`.
* Optionaly set other configuration as specified above and in the docker-registry project.
* Run the docker-registry.
  * Installing the docker-registry also installs a `docker-registry` command.

# Implementation details

## Startup

At startup the Index class (the one that does all the work) checks to see if the configured DynamoDB table names exist, and if not, create them. 

If the tables were created, then the repositories already located in the data store (which is presumably the s3 data store) will be loaded into the repository table. This means that you can delete the DynamoDB tables, and they will be reloaded when the docker-registry is started. You should probably not delete the tables while the docker-registry is running, although they are only used for query.

A simple lock is used in the Index constructor to prevent multiple threads attempting to create and/or load the database at the same time.
