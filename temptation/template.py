from __future__ import print_function, unicode_literals

import logging
import re
from collections import OrderedDict

import resolvers

logging.basicConfig()
logger = logging.getLogger(__name__)

_templateregex = r"""
    (?:
        (?P<escape>(?<!\\)\\)?
        (?P<unescaped>
            {tag}(?:
                (?:{bound[0]}
                    (?P<expression>{expression})
                    {bound[1]}
                )
            )
        )
    )
"""

class Resolver:
    r"""
    >>> Resolver('dictmatcher', tag=r'\$',   bound=(r'\{', r'\}'), samples=['${}', 'hello ${}'],  processor=resolvers.resolve_dict)
    {id: 'dictmatcher', tag: r'\$', bound: '(u'\\{', u'\\}')', samples: [u'${}', u'hello ${}'], processor: resolve_dict}
    """
    def __init__(self, id, **kwargs):
        # TODO: Make this cleaner by making it more verbose (no **kwargs)
        self.__dict__ = dict({"id": id, "tag": r'\$', "bound": ('{', '}'), "samples": [], "processor": resolvers.dont_resolve}, **kwargs)
        # derivates:
        self.expression = r"([^{bound[0]}{bound[1]}] | \\{bound[0]} | \\{bound[1]})*".format(bound=self.bound)
        self.regex = _templateregex.format(**self.__dict__)
        self.pattern = re.compile(self.regex, re.VERBOSE|re.DOTALL)
    def __repr__(self):
        return "{id: '%s', tag: r'%s', bound: '%s', samples: %s, processor: %s}" % (self.id, self.tag, self.bound, self.samples, self.processor.__name__)

class Resolvers:
    def __init__(self):
        self._resolvers = OrderedDict()
        self.add(Resolver('dictmatcher',      tag=r'\$',   bound=(r'\{', r'\}'), samples=['${}', 'hello ${}'],  processor=resolvers.resolve_dict))
        self.add(Resolver('evalmatcher',      tag=r'\!',   bound=(r'\{', r'\}'), samples=['!{}'],               processor=resolvers.resolve_eval))
        self.add(Resolver('pathmatcher',      tag=r'\@',   bound=(r'\{', r'\}'), samples=['@{}'],               processor=resolvers.resolve_path_singlematch))
        self.add(Resolver('pathmultimatcher', tag=r'\@\*', bound=(r'\{', r'\}'), samples=['@*{}'],              processor=resolvers.resolve_path_multimatch))
    # TODO: add methods for replacing and/or deleting resolver
    def add(self, resolver):
        # TODO: Add split samples to matching and non-matching
        # TODO: Consider initializing Template without resolvers and using default resolvers only as a choice for easily being added
        r"""
        >>> Template("${hello} ${name}").resolve({"hello": "Hello", "name": "world"})
        u'Hello world'
        """
        if self._resolvers.get("id"):
            # TODO: raise more specific exceptions
            # TODO: consider allowing to update existing resolver
            raise Exception("Attempt to overwrite existing resolver '%s': '%s'" % (resolver["id"], self._resolvers.get("id")))
        self._verify_resolver(resolver)
        self._resolvers[resolver.id] = resolver
        return self
    def remove(self, id):
        del(self._resolvers[id])
        return self
    def _verify_resolver(self, resolver):
        for id, competitor in self._resolvers.iteritems():
            for sample in resolver.samples:
                if not resolver.pattern.findall(sample):
                    raise Exception("'%s' didn't match '%s'" % (sample, resolver.regex))
                # TODO: Check for regex intersection instead. E.g. https://github.com/qntm/greenery (unfortunately python3 only)
                if competitor.pattern.findall(sample):
                    raise Exception("sample '%s' for resolver with id '%s' also matches resolver with id '%s'" % (sample, resolver.id, competitor.id))
            for sample in competitor.samples:
                if resolver.pattern.findall(sample):
                    raise Exception("sample '%s' for resolver '%s' also matches resolver '%s'" % (sample, resolver.id, competitor.id))

class Template:
    escaped_backslash_pattern = re.compile('\\\\')
    def __init__(self, template, resolvers=Resolvers()):
        self.template = template
        self.resolvers = resolvers._resolvers
    def resolve(self, context=None):
        result = self.template
        for id, resolver in self.resolvers.iteritems():
            def process(match):
                expression = match.group("expression")
                if match.group("escape"):
                    return match.group("unescaped")
                elif expression is not None:
                    return resolver.processor(expression=expression, context=context, match=match)
                else:
                    raise Exception("unexpected match result: %s" % (match.group()))
            result = resolver.pattern.sub(process, result)
        result = result.replace("\\\\", "\\")
        return result


if __name__ == "__main__":
    import doctest
    doctest.testmod()
