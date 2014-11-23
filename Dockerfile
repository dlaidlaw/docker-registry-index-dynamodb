#
# A docker-registry image with DynamoDB as the Index store.
#
# TO_BUILD:       docker build --rm -t docker-registry-dynamodb .
# TO_RUN:         docker run -p 5000:5000 docker-registry-dynamodb
#

# Latest docker-registry
FROM registry:latest

MAINTAINER https://github.com/dlaidlaw/docker-registry-index-dynamodb

COPY . /docker-registry-index-dynamodb

# Install dynamodb index
RUN pip install file:///docker-registry-index-dynamodb#egg=docker-registry-index-dynamodb

ENV DOCKER_REGISTRY_CONFIG /docker-registry/config/config_sample.yml
ENV SEARCH_BACKEND docker_registry_index.dynamodb
ENV SETTINGS_FLAVOR dev

EXPOSE 5000

CMD ["docker-registry"]