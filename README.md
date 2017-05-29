# Overview

Logstash input plugin that reads events from elasticsearch.

# Usage

Step by step instructions on using the charm:

juju deploy logstash-input-elasticsearch

juju add-relation logstash-input-elasticsearch:elasticsearch elasticsearch


# Configuration

The template field can be changed. Use {{ hosts }} for elasticsearch servers


  - https://github.com/tbaumann/charm-logstash-input-elasticsearch
