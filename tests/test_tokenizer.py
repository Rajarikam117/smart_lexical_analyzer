import unittest
from smart_lexer.lexer.tokenizer import Tokenizer


class TestTokenizerErrors(unittest.TestCase):
    def setUp(self):
        self.t = Tokenizer()

    def errors_types(self, out):
        return [e.type for e in out.get('errors', [])]

    def errors_suggestions(self, out):
        return [e.suggestion for e in out.get('errors', [])]

    def test_unterminated_string(self):
        src = "var s = 'hello\n"
        out = self.t.analyze(src, mode='AI')
        types = self.errors_types(out)
        self.assertIn('Unterminated String', types)
        suggs = self.errors_suggestions(out)
        self.assertTrue(any(sug and 'closing' in sug.lower() or 'add' in sug.lower() for sug in suggs))

    def test_invalid_character(self):
        src = "foo@ = 1;"
        out = self.t.analyze(src, mode='AI')
        types = self.errors_types(out)
        self.assertIn('Invalid Character', types)
        suggs = self.errors_suggestions(out)
        self.assertTrue(any(sug and 'replace' in sug.lower() or 'remove' in sug.lower() for sug in suggs))

    def test_malformed_number(self):
        src = "x = 5.;"
        out = self.t.analyze(src, mode='AI')
        types = self.errors_types(out)
        self.assertIn('Malformed Number', types)

    def test_identifier_starting_with_digit(self):
        src = "var 1bad = 5;"
        out = self.t.analyze(src, mode='AI')
        types = self.errors_types(out)
        self.assertIn('Invalid Identifier', types)

    def test_unterminated_comment(self):
        src = "/* comment"
        out = self.t.analyze(src, mode='AI')
        types = self.errors_types(out)
        self.assertIn('Unterminated Comment', types)

    def test_duplicate_declaration(self):
        src = "var x = 1; var x = 2;"
        out = self.t.analyze(src, mode='AI')
        types = self.errors_types(out)
        self.assertIn('Duplicate Declaration', types)

    def test_valid_tokens(self):
        src = "var a = 10; let b = 2.5;"
        out = self.t.analyze(src, mode='AI')
        self.assertEqual(len(out.get('errors', [])), 0)
        tokens = out.get('tokens', [])
        self.assertTrue(any(t['type'] == 'KEYWORD' and t['value']=='var' for t in tokens))
        self.assertTrue(any(t['type'] == 'INT' and t['value']=='10' for t in tokens))


if __name__ == '__main__':
    unittest.main()
