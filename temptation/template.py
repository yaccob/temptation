from __future__ import print_function, unicode_literals

import logging
import re
from collections import OrderedDict

import default_resolvers

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

class Matcher:
    def __init__(self, id, **kwargs):
        # TODO: Make this cleaner by making it more verbose (no **kwargs)
        self.__dict__ = dict({"id": id, "tag": r'\$', "bound": ('{', '}'), "samples": [], "processor": default_resolvers.dont_resolve}, **kwargs)
        # derivates:
        self.expression = r"([^{bound[0]}{bound[1]}] | \\{bound[0]} | \\{bound[1]})*".format(bound=self.bound)
        self.regex = _templateregex.format(**self.__dict__)
        self.pattern = re.compile(self.regex, re.VERBOSE|re.DOTALL)
    def __repr__(self):
        return "{id: '%s', tag: r'%s', bound: '%s', samples: %s, processor: %s}" % (self.id, self.tag, self.bound, self.samples, self.processor.__name__)

class Template:
    _default_matchers = OrderedDict([
        ("dictmatcher",      Matcher('dictmatcher',      tag=r'\$',   bound=(r'\{', r'\}'), samples=['${}', 'hello ${}'],  processor=default_resolvers.resolve_dict)),
        ("evalmatcher",      Matcher('evalmatcher',      tag=r'\!',   bound=(r'\{', r'\}'), samples=['!{}'],               processor=default_resolvers.resolve_eval)),
        ("pathmatcher",      Matcher('pathmatcher',      tag=r'\@',   bound=(r'\{', r'\}'), samples=['@{}'],               processor=default_resolvers.resolve_path_singlematch)),
        ("pathmultimatcher", Matcher('pathmultimatcher', tag=r'\@\*', bound=(r'\{', r'\}'), samples=['@*{}'],              processor=default_resolvers.resolve_path_multimatch)),]
    )
    def __init__(self, template, matchers=_default_matchers):
        self.template = template
        self.matchers = matchers.copy() if matchers else OrderedDict()
    def resolve(self, context=None):
        result = self.template
        for id, matcher in self.matchers.iteritems():
            def process(match):
                expression = match.group("expression")
                if match.group("escape"):
                    return match.group("unescaped")
                elif expression is not None:
                    return matcher.processor(expression=expression, context=context, match=match)
                else:
                    raise Exception("unexpected match result: %s" % (match.group()))
            result = matcher.pattern.sub(process, result)
        result = result.replace("\\\\", "\\")
        return result
    def add_matcher(self, matcher):
        # TODO: Add split samples to matching and non-matching
        self._verify_matcher(matcher)
        if self.matchers.get(matcher.id):
            self.matchers[matcher.id].update(matcher)
        else:
            self.matchers[matcher.id] = matcher
        return self
    def _verify_matcher(self, matcher):
        # TODO: Check for regex intersection instead of sample intersection. E.g. https://github.com/qntm/greenery (unfortunately python3 only)
        for id, competitor in self.matchers.iteritems():
            for sample in matcher.samples:
                if not matcher.pattern.findall(sample):
                    raise Exception("'%s' didn't match '%s'" % (sample, matcher.regex))
                if competitor.pattern.findall(sample):
                    raise Exception("sample '%s' for matcher '%s' also matches matcher '%s'" % (sample, matcher.id, competitor.id))
            for sample in competitor.samples:
                if matcher.pattern.findall(sample):
                    raise Exception("sample '%s' for matcher '%s' also matches matcher '%s'" % (sample, competitor.id, matcher.id))

if __name__ == "__main__":
    import doctest
    doctest.testmod()
