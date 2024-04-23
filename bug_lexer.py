import ply.lex as lex

reserved = {
    'fn': 'FN',
    'let': 'LET',
    'struct': 'STRUCT',
    'enum': 'ENUM',
    'if': 'IF',
    'else': 'ELSE',
    'loop': 'LOOP',
    'while': 'WHILE',
    # 'until': 'UNTIL',
    'return': 'RETURN',
    'match': 'MATCH',
    'i32': 'I32',
    'i64': 'I64',
    'f32': 'F32',
    'f64': 'F64',
    'bool': 'BOOL',
    'char': 'CHAR',
    'true': 'BOOLEAN',
    'false': 'BOOLEAN',
    'new': 'NEW',
}
# Tokens
tokens = (
    'IDENT', 'LPAREN', 'RPAREN', 'LBRACE', 'RBRACE', 'COMMA', 'COLON', 'EQ',
    'PLUS', 'MINUS', 'STAR', 'SLASH', 'PERCENT', 'NOT', 'AND', 'OR',
    'LT', 'GT', 'LE', 'GE', 'EQEQ', 'NEQ',
    'DOT', 'LBRACKET', 'RBRACKET', 'ARROW', 'FAT_ARROW',
    'SEMI', 'INT', 'FLOAT', 'STRING',
) + tuple(set(reserved.values()))

# Literals
literals = ['=', ';', '{', '}', '[', ']', '(', ')', ',', '.', ':']

# Token definitions
def t_IDENT(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    t.type = reserved.get(t.value,'IDENT')    # Check for reserved words
    return t

def t_INT(t):
    r'[0-9]+'
    t.value = int(t.value)
    return t

def t_FLOAT(t):
    r'[0-9]+\.[0-9]+'
    t.value = float(t.value)
    return t

def t_STRING(t):
    r'\'[^\']*\'|\"[^\"]*\"'
    t.value = str(t.value[1:-1])
    return t


t_PLUS = r'\+'
t_MINUS = r'-'
t_STAR = r'\*'
t_SLASH = r'/'
t_PERCENT = r'%'
t_NOT = r'!'
t_AND = r'&&'
t_OR = r'\|\|'

t_LT = r'<'
t_GT = r'>'
t_LE = r'<='
t_GE = r'>='
t_EQEQ = r'=='
t_NEQ = r'!='

t_DOT = r'\.'
t_LBRACKET = r'\['
t_RBRACKET = r'\]'
t_ARROW = r'->'
t_FAT_ARROW = r'=>'
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_COLON = r':'
t_SEMI = r';'
t_COMMA = r','
t_EQ = r'='
t_LBRACE = r'\{'
t_RBRACE = r'\}'


def t_NEWLINE(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

# Ignored characters
t_ignore ='\t\r'

# Whitespace
def t_WHITESPACE(t):
    # skip whitespace
    r'\s+'
    pass

def t_COMMENT(t):
    r'\//.*'
    pass
    # No return value. Token discarded

def find_column(input, token):
    line_start = input.rfind('\n', 0, token.lexpos) + 1
    return (token.lexpos - line_start) + 1

# Error handling
def t_error(t):
    print(f"Illegal character '{t.value[0]}' at line {t.lineno} position {find_column(t.lexer.lexdata, t)}")
    t.lexer.skip(1)

# Build the lexer
lexer = lex.lex()

# # Test the lexer
# if __name__ == "__main__":
#     with open('example.bug', 'r') as file:
#         data = file.read()
#     lexer.input(data)
#     for tok in lexer:
#         print(tok)