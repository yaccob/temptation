import setuptools
import io

from temptation import __version__

distribution = 'temptation'
version = __version__

setuptools.setup(
  name = distribution,
  packages = [distribution],
  install_requires = ['PyYaml', 'jsonpath-ng'],
  version = '%s' % version,
  description = 'Temptation is a simple and straightforward template engine supporting semantic substitution expressions.',
  long_description=io.open('README.rst', encoding='utf-8').read(),
  author = 'Jakob Stemberger',
  author_email = 'yaccob@gmx.net',
  license = 'Apache 2.0',
  url = 'https://github.com/yaccob/%s' % (distribution),
  download_url = 'https://github.com/yaccob/%s/archive/%s.tar.gz' % (distribution, version),
  keywords = ['temptation', 'template-engine', 'template', 'yaml', 'json', 'transform', 'jsonpath', 'json-path'],
  classifiers = ['Programming Language :: Python :: 2.7'],
  scripts = ['scripts/%s' % (distribution)],
)
