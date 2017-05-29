from charms.reactive import when, when_not, set_state, when_any, hook
from charmhelpers.core.hookenv import (
    related_units,
    relation_ids,
    relation_get,
    log,
    status_set,
    config,
    service_name
)
from charmhelpers.core import hookenv
from charms.reactive.helpers import data_changed
from charmhelpers.core.templating import render
import json
import os


@when_not('logstash-input-elasticsearch.installed')
def install_logstash_input_elasticsearch():
    # Nothing required
    set_state('logstash-input-elasticsearch.installed')
    status_set('waiting', 'waiting for elasticsearch')


@when_any('host-system.available', 'host-system.connected')
@when('elasticsearch.connected')
def connect_to_elasticsearch(elasticsearch):
    write_config()
    status_set('active', 'Ready')
    set_state('logstash-input-elasticsearch.started')


@when('elasticsearchself.broken')
def disconnect_from_elasticsearch(elasticsearch):
    write_config()


def elasticsearch_servers():
    hosts = []
    config = hookenv.config()
    for rel_id in relation_ids('elasticsearch'):
        for unit in related_units(rel_id):
            port = relation_get('port', unit, rel_id)
            host = relation_get('private-address', unit, rel_id)
            if port:
                hosts.append("{}:{}".format(host, port))
    return hosts


@hook('config-changed')
def write_config():
    config = hookenv.config()
    hosts = elasticsearch_servers()
    if data_changed('elasticsearch_servers', hosts) or data_changed('template', config['template']):
        log("Writing config")
        if(hosts):
            from jinja2 import Template
            app_name = hookenv.service_name()
            template = Template(config['template'])
            hosts_str = "[{}]".format(', '.join(map(lambda x: "'{}'".format(x), hosts)))
            with open('/etc/logstash/conf.d/{}.conf'.format(app_name), 'w') as conf_file:
                conf_file.write(str(
                    template.render({
                        'hosts': hosts_str
                        }
                    )
                ))
        else:
            log("No elasticsearch servers connected. Removing config.")
            try:
                app_name = hookenv.service_name()
                os.remove('/etc/logstash/conf.d/{}.conf'.format(app_name))
            except FileNotFoundError:
                pass
