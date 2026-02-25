import json
from smart_lexer.lexer.tokenizer import Tokenizer
from smart_lexer.lexer.errors import LexError

SAMPLE = '''
// Sample code
var x = 123;
let y = 3.14;
const z = 'hello;
var 1bad = 5;
var x = 10;
num = 5.;
foo@ = 0;
/* unterminated comment
'''

def format_output(out):
    tokens = out.get('tokens', [])
    errors = out.get('errors', [])
    # convert errors to dicts
    errs = [e.to_dict() for e in errors]
    return json.dumps({
        'tokens': tokens,
        'errors': errs,
    }, indent=2)

def main():
    tok = Tokenizer()
    out = tok.analyze(SAMPLE, mode='AI')
    print(format_output(out))

if __name__ == '__main__':
    main()
