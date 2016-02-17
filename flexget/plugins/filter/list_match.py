import logging

from flexget import plugin
from flexget.event import event

log = logging.getLogger('list_match')

LISTS_SCHEMA = {'type': 'array',
                'items':
                    {'allOf': [
                        {'$ref': '/schema/plugins?group=list'},
                        {
                            'maxProperties': 1,
                            'error_maxProperties': 'Plugin options within list_queue plugin must be indented 2 more spaces '
                                                   'than the first letter of the plugin name.',
                            'minProperties': 1
                        }
                    ]
                    }
                }


class ListMatch(object):
    schema = {'oneOf':
                  [LISTS_SCHEMA,
                   {'type': 'object',
                    'properties': {
                        'lists': LISTS_SCHEMA,
                        'remove_on_match': {'type': 'boolean'}
                    }}
                   ]
              }

    def prepare_config(self, config):
        if isinstance(config, list):
            config = {'items': config}
            config.setdefault('remove_on_match', True)

    def on_task_filter(self, task, config):
        config = self.prepare_config(config)
        for item in config.get('items'):
            for plugin_name, plugin_config in item.iteritems():
                thelist = plugin.get_plugin_by_name(plugin_name).instance.get_list(plugin_config)
                for entry in task.all_entries:
                    if entry in thelist:
                        entry.accept()

    def on_task_learn(self, task, config):
        config = self.prepare_config(config)
        if not config.get('remove_on_match'):
            return
        for item in config.get('items'):
            for plugin_name, plugin_config in item.iteritems():
                thelist = plugin.get_plugin_by_name(plugin_name).instance.get_list(plugin_config)
                thelist -= task.accepted


@event('plugin.register')
def register_plugin():
    plugin.register(ListMatch, 'list_match', api_ver=2)