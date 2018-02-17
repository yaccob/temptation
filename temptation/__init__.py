import logging
import yaml
from collections import OrderedDict

logging.basicConfig()
logger = logging.getLogger(__name__)

from template import *

__version__ = '0.1.0'

def orderedDict_constructor(loader, node, deep=False):
    data = OrderedDict()
    yield data
    if isinstance(node, yaml.MappingNode):
        loader.flatten_mapping(node)
    data.update(OrderedDict(loader.construct_pairs(node, deep)))

yaml.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, orderedDict_constructor)
yaml.add_representer(OrderedDict, lambda dumper, data: dumper.represent_dict(data.iteritems()))
yaml.add_constructor(u'tag:yaml.org,2002:timestamp', yaml.constructor.SafeConstructor.construct_yaml_str)
yaml.add_representer(OrderedDict, lambda dumper, data: dumper.represent_dict(data.iteritems()), Dumper=yaml.SafeDumper)
