import unittest

from context import temptation
from temptation import Template, Matcher, default_resolvers

# Test class
class TestTemplate(unittest.TestCase):

    def test_static_text(self):
        template = "Hello world"
        expected = "Hello world"
        self.assertEqual(Template(template).resolve(), expected)

    def test_map_resolution_simple(self):
        template = "${greeting} ${name}"
        data = {"greeting": "Hello", "name": "world"}
        expected = "Hello world"
        self.assertEqual(Template(template).resolve(data), expected)

    def test_map_resolution_non_string_value(self):
        template = "${item1} ${item2}"
        data = {
            "item1": {"greeting": "Hello", "name": "world"},
            "item2": {"greeting": "Hello", "name": "Donald Truck"}}
        expected = "{'greeting': 'Hello', 'name': 'world'} {'greeting': 'Hello', 'name': 'Donald Truck'}"
        self.assertEqual(Template(template).resolve(data), expected)

    def test_map_escaped_expression(self):
        template = r"Hello \${name}"
        data = {"name": "world"}
        expected = 'Hello ${name}'
        self.assertEqual(Template(template).resolve(data), expected)

    def test_escaped_backslash(self):
        template = r"\\Hello \\${name} \\"
        data = {"name": "world"}
        expected = r'\Hello \world ' + '\\'
        self.assertEqual(Template(template).resolve(data), expected)

    def test_path_singlematch(self):
        template = "@{$.items[0].greeting} @{$.items[0].name} and @{$.items[1].greeting} @{$.items[1].name}"
        data = {"items": [
            {"greeting": "Hello", "name": "world"},
            {"greeting": "hello", "name": "Donald Truck"}]}
        expected = "Hello world and hello Donald Truck"
        self.assertEqual(Template(template).resolve(data), expected)

    def test_path_singlematch_non_string_value(self):
        template = "@{$.items[0].*} and @{$.items[1].*}"
        data = {"items": [
            {"greeting": "Hello", "name": "world"},
            {"greeting": "hello", "name": "Donald Truck"}]}
        expected = "['Hello', 'world'] and ['hello', 'Donald Truck']"
        self.assertEqual(Template(template).resolve(data), expected)

    def test_path_muiltimatch(self):
        template = "@*{$.items[0].*} and @*{$.items[1].*}"
        data = {"items": [
            {"greeting": "Hello", "name": "world"},
            {"greeting": "hello", "name": "Donald Truck"}]}
        expected = "['Hello', 'world'] and ['hello', 'Donald Truck']"
        self.assertEqual(Template(template).resolve(data), expected)

    def test_eval(self):
        template = "Hello !{7 + 5}"
        expected = "Hello 12"
        self.assertEqual(Template(template).resolve(), expected)

    def test_eval_with_data(self):
        template = "Hello !{context['values'][2] + context['values'][3]}"
        data = {"values": [1, 3, 5, 7]}
        expected = "Hello 12"
        self.assertEqual(Template(template).resolve(data), expected)

    def test_add_matchers(self):
        def resolve_foo(expression, match, context):
            return "foo-{0}".format(expression)
        template = "Hello $foo{something} and $bar{something_else}"
        expected = "Hello foo-something and something_else-bar"
        self.assertEqual(
            Template(template).add_matcher(
                Matcher("foomatcher", tag=r"\$foo", samples=["$foo{}"], processor=resolve_foo)).add_matcher(
                Matcher("barmatcher", tag=r"\$bar", samples=["$bar{}"], processor=lambda expression, match, context: "{0}-bar".format(expression)))
            .resolve(), expected)

    def test_set_matchers(self):
        def resolve_foo(expression, match, context):
            return "foo-{0}".format(expression)
        template = "Hello $foo{something} and $bar{something_else}"
        expected = "Hello foo-something and something_else-bar"
        self.assertEqual(
            Template(template, matchers=None).add_matcher(
                Matcher("normalmatcher", tag=r"\$", samples=["${bla}"],   processor=default_resolvers.resolve_dict)).add_matcher(
                Matcher("foomatcher", tag=r"\$foo", samples=["$foo{}"], processor=resolve_foo)).add_matcher(
                Matcher("barmatcher", tag=r"\$bar", samples=["$bar{}"], processor=lambda expression, match, context: "{0}-bar".format(expression)))
            .resolve(), expected)

    def test_set_matchers_conflicting(self):
        foomatcher = Matcher("foomatcher", tag=r"\$x", samples=["$x{whatever}"])
        barmatcher = Matcher("barmatcher", tag=r"\$xx*", samples=["$xxx{whatever}"])
        template = Template("", matchers=None)
        template.add_matcher(foomatcher)
        with self.assertRaises(Exception) as exception_context:
            template.add_matcher(barmatcher)

    #TODO: Add unit tests for conflicting custom matcher


if __name__ == "__main__":
    unittest.main()
