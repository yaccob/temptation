# Temptation

Temptation is a simple and straightforward template engine with an extensible grammar.

# Objectives

## Regular-expression-based

Substitution in _temptation_ templates is based on regular expressions.

Apart from the obvious limitations regarding nested substitution-expressions (they may be supported to a certain extent)
this comes with two advantages:

+ Extensibility
+ Efficient regular-expression scanning rather than complex parsing.

## Semantic expression substitution

Rather than always expecting key-value pairs as input _temptation_ provides the ability to apply different substitution algorithms on different template-expressions.

## Extensibility

The regular-expression based grammar can easily be extended or customized by adding custom matchers.

## MVC-based templating

Template languages are a way to separate the view (presentation) from the data model.

Many (if not most) template languages support control structures like conditions or loops. So their templates combine presentation with control.

_temptation_ intentionally doesn't.

This comes with limitations and with advantages.
An obvious limitation is that with using _temptation_ on its own you can't process data in a non-linear way. There is only one path from the beginning to the end of the template.

Advantages are:

+ The linear approach keeps templates simple and very well readable.
+ Templates are easy to test.
+ _temptation_ templates can easily be be used by external controllers that care about more complex transformation-related issues like conditional processing or iteration.

  _ynot_ is a transformator making use of the _temptation_ grammar and this reference-implementation. See [ynot overview on  github](https://github.com/yaccob/ynot/blob/master/README.md).

## Limited support for nested template expressions

This is not implemented yet because I didn't find a reasonable use-case. But it could be added quite easily if it turns out that it makes sense.

# Setup

```bash
$ pip install temptation

```

By installing _temptation_ via `pip` you automatically get the command line interface of _temptation_ installed as well.

# Command-Line-Interface (CLI)

The purpose of the command line interface is to support processing data-files (`yaml` or `json`) against a single template-file.

To get help on the (currently quite limited) command-line options just enter

`temtation -h`

and you'll see an output like this:

```
Usage: scripts/temptation [OPTION] -t template datafile...

Resolve template for datafiles. Datafiles can be yaml or json

Options:
  --version             show program version number and exit
  -h, --help            show this help message and exit
  -t TEMPLATEFILENAME, --template=TEMPLATEFILENAME
                        Template to be resoved
```

In the current version if you use multiple data-files as input they need to be in `yaml` format and every file must begin with a document-separator (`---`).

This limitation may be removed in future versions so that it will also be possible to process multiple 'json' data-files which is currently not possible because json doesn't support multiple documents.

## Command-line Expample

Let's say we have this text file ...

`temlate.txt`:

```
${greeting} ${name}!
```

... and the following data-files:

`data1.yaml`:

```yaml
---
greeting: Hello
name: world
```

`data2.yaml`:

```yaml
---
greeting: Good morning
name: Donald Duck
```

Now let's see how _temptation_ applies the template to the data-files:

```
$ temptation -t template.text data*.yaml
Hello world!
Good morning Donald Duck!
```

Quite simple, right?

# Imports

The following samples assume that you have imported the `Template` class like this:

```python
>>> from temptation import Template

```

# Samples

## Just static text

Any text that's not a _temptation_ expression is left unchanged.

```python
>>> Template("Hello world").resolve()
u'Hello world'

```

There are some pre-defined _temptation_ expressions:

+ `${key}`: Map resolution
+ `@{jsonpath}`: Jsonpath resolution for single match
+ `@*{jsonpath}`: Jsonpath resolution for multiple match
+ `!{python expression}`: Python evaluation expression

If you need to use a literal that matches those expressions you need to escape it with a backslash `\` like this:

`\${whatever}`

In the expanded template the backslash will be removed but the expression won't be evaluated.

Literal baskslashes can be escaped by a backslash as well. So `\\` in the template will be presented as `\` in the output. You will see samples for this further down.

Let's now see samples for the pre-defined _temptation_ expressions and how they are expanded.

## Map resolution: `${key}`

One of the pre-defined _temptation_ expressions is a simple key-value substitution.

The expression's value is interpreted as a key that will be substituted by the corresponding value of the input data.

```python
>>> Template("${greeting} ${name}").resolve({"greeting": "Hello", "name": "world"})
u'Hello world'

```

## Escaping tags: `\${key}`

Any pre-defined (or custom) _temptation_ expression can be escaped by preceding it with a backslash. A backslash itself can be escaped by another backslash.

```python
>>> Template(r"Hello \${name}").resolve({"name": "world"})
u'Hello ${name}'

>>> Template(r"Hello \\${name}").resolve({"name": "world"})
u'Hello \\world'

```

## Jsonpath resolution for single match: `@{jsonpath-espression}`

The jsonpath expansion is based on the [jsonpath-ng](https://pypi.python.org/pypi/jsonpath-ng/1.4.3) implementation, so the syntax is predetermined by this implementation. Please read the linked documentation for details.

A jsonpath result always returns an array of matches. This array may contain 0..n items. To represent a result that matches multiple items _temptation_ is enclosing the matches in brackets: `[item1, item2, ...]`.

In a template you're often interested in a single match and don't want this to be enclosed in brackets. That's why _temptation_ supports the _single match_ resolution. It will omit the enclosing brackets if there is a single match. In case of multiple matches it will log a warning and enclose the result in brackets.

```python
>>> context = {"items": [{"item": "first item"}, {"item": "second item"}]}
>>> Template("Hello @{$.items[0].item} and @{$.items[1].item}").resolve(context)
u'Hello first item and second item'

>>> Template(u"Hello @{$..item}").resolve(context)
u"Hello ['first item', 'second item']"

```

## Jsonpath resolution for multiple matches: `@*{jsonpath expression}`

Whenever you don't expect a single match but want to consistently present the result as a list, you can use this _temptation_ expression.

```python
>>> context = {"items": [{"item": "first item"}, {"item": "second item"}]}
>>> Template("Hello @*{$.items[0].item} and @*{$.items[1].item}").resolve(context)
u"Hello ['first item'] and ['second item']"

>>> Template(u"Hello @*{$..item}").resolve(context)
u"Hello ['first item', 'second item']"

```

## Evaluation resolution: `!{python expression}`

The python-evaluation resolution allows to expand a _temptation_ expression to the result of any python expression.

Currently the pre-defined evaluation expression is limited to the use of modules that are imported in the `template.default_resolvers` module. It's planned to provide a more flexible solution for importing additional modules to be accessible from evaluation expressions.

```python
>>> Template(u"Hello !{7 + 5}").resolve()
u'Hello 12'

>>> context = {"values": [1, 3, 5, 7]}
>>> Template(u"Hello !{context['values'][2] + context['values'][3]}").resolve(context)
u'Hello 12'

>>> template = """${greeting} ${name}
... This is a very personal letter. To emphasize how well I know you
... I add best regards to your !{len(context['children'])} children !{", ".join([child for child in context["children"]])}.
... """
>>> context = [{"name": "Mr. Template", "greeting": "Hello", "children": ["Jeff", "Henriette", "Mark"]}, {"name": "Mrs. Temptation", "greeting": "Dear", "children": []}]
>>> for item in context:
...     Template(template).resolve(item)
u'Hello Mr. Template\nThis is a very personal letter. To emphasize how well I know you\nI add best regards to your 3 children Jeff, Henriette, Mark.\n'
u'Dear Mrs. Temptation\nThis is a very personal letter. To emphasize how well I know you\nI add best regards to your 0 children .\n'

```

# Adding your own matchers

You can extend _temptation_'s capabilities by implementing your own matchers.

To do so you must first import the `Resolvers` class:

## Import Matcher

```python
>>> from temptation import Matcher

```

## Custom matcher sample

```python
>>> def resolve_foo(expression, match, context):
...     return "foo-{0}".format(expression)

>>> foomatcher = Matcher("foomatcher", tag=r"\$foo", samples=["$foo{}"], processor=resolve_foo)
>>> barmatcher = Matcher("barmatcher", tag=r"\$bar", samples=["$bar{}"], processor=lambda expression, match, context: "{0}-bar".format(expression))

>>> template = "Hello $foo{something} and $bar{something_else}"
>>> Template(template).add_matcher(foomatcher).add_matcher(barmatcher).resolve()
u'Hello foo-something and something_else-bar'

```

## Resolvers are validated against samples

It is also ensured that samples don't match with other matchers. This is an attempt to help avoiding ambiguities (but obviously doesn't guarantee that there is no intersection between regular expressions of different matchers).

```python
>>> foomatcher = Matcher("foomatcher", tag=r"\$x", samples=["$x{whatever}"])
>>> barmatcher = Matcher("barmatcher", tag=r"\$xx*", samples=["$xxx{whatever}"])

>>> template = Template("").add_matcher(foomatcher)
>>> template.add_matcher(barmatcher)
Traceback (most recent call last):
 ...
Exception: sample '$x{whatever}' for matcher 'foomatcher' also matches matcher 'barmatcher'

```
