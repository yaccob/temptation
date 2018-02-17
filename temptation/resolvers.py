import logging
import jsonpath_ng as jsonpath

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

jsonpath.auto_id_field = '_jsonpath_id'

def dont_resolve(expression, match, context):
    return match.group(0)

def _convert_if_non_string(result):
    if not isinstance(result, basestring):
        logger.warn("Converting resolution-result to string: %s" % (result))
        return unicode(result)
    return result

def resolve_dict(expression, match, context):
    return _convert_if_non_string(context.get(expression))

def resolve_eval(expression, match, context):
    return _convert_if_non_string(eval(expression))

def resolve_path_singlematch(expression, match, context):
    pathmatches = jsonpath.parse(expression).find(context)
    result = match.group(0)
    if pathmatches:
        result = pathmatches[0].value
        if len(pathmatches) > 0:
            if len(pathmatches) > 1:
                result = unicode([m.value if pathmatches else match.group(0) for m in pathmatches])
                logger.warn("More than 1 match!\n\ttemplate-expression: %s\n\tcontext: %s\n\treturning: %s" % (match.group(0), context, result))
            result = result if isinstance(result, basestring) else unicode(result)
    return result

def resolve_path_multimatch(expression, match, context):
    pathmatches = jsonpath.parse(expression).find(context)
    if pathmatches:
        return unicode([m.value for m in pathmatches])
    return match.group(0)
