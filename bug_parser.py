import ply.yacc as yacc
from bug_ast import *
from bug_lexer import find_column, tokens


# Parsing rules
def p_program(p):
    "program : decls"
    p[0] = ModuleAST(p[1])


def p_decls(p):
    """decls : decl
    | decls decl"""
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[2]]


def p_decl(p):
    """decl : fn_decl
    | var_decl
    | struct_decl
    | enum_decl
    | SEMI"""
    if p[1] != ";":
        p[0] = p[1]


def p_fn_decl(p):
    """fn_decl : FN IDENT LPAREN params RPAREN ARROW type LBRACE body RBRACE
    | FN IDENT LPAREN RPAREN ARROW type LBRACE body RBRACE
    | FN IDENT LPAREN params RPAREN LBRACE body RBRACE
    | FN IDENT LPAREN RPAREN LBRACE body RBRACE"""
    con = None
    if len(p) == 10:
        con = {
            "name": p[2],
            "params": [],
            "ret_type": p[6],
            "body": p[8],
        }
    elif len(p) == 11:
        con = {
            "name": p[2],
            "params": p[4],
            "ret_type": p[7],
            "body": p[9],
        }
    elif len(p) == 9:
        con = {
            "name": p[2],
            "params": p[4],
            "ret_type": None,
            "body": p[7],
        }
    else:
        con = {
            "name": p[2],
            "params": [],
            "ret_type": None,
            "body": p[6],
        }

    p[0] = FnDeclAST(**con)


def p_var_decl(p):
    "var_decl : LET IDENT COLON type EQ expr SEMI"
    p[0] = VarDeclAST(p[2], p[4], p[6])


def p_struct_decl(p):
    "struct_decl : STRUCT IDENT LBRACE fields RBRACE"
    p[0] = StructDeclAST(p[2], p[4])


def p_enum_decl(p):
    "enum_decl : ENUM IDENT LBRACE variants RBRACE"
    p[0] = EnumDeclAST(p[2], p[4])


def p_params(p):
    """params : param
    | params COMMA param"""
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[3]]


def p_param(p):
    "param : IDENT COLON type"
    p[0] = ParamAST(p[1], p[3])


def p_fields(p):
    """fields : field
    | fields COMMA field"""
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[3]]


def p_field(p):
    "field : IDENT COLON type"
    p[0] = FieldAST(p[1], p[3])


def p_variants(p):
    """variants : variant
    | variants COMMA variant"""
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[3]]


def p_variant(p):
    "variant : IDENT EQ expr"
    p[0] = VariantAST(p[1], p[3])


def p_type(p):
    """type : I32
    | I64
    | F32
    | F64
    | BOOL
    | CHAR
    | STRING
    | IDENT
    | array_type
    | ptr_type"""
    if isinstance(p[1], TypeAST):
        p[0] = p[1]
    else:
        p[0] = TypeAST(p[1])


def p_array_type(p):
    """array_type : LBRACKET type SEMI INT RBRACKET
    | LBRACKET type RBRACKET"""
    _type = p[2]
    if len(p) == 6:
        size = p[4]
        p[0] = TypeAST("array", _type, size)
    else:
        p[0] = TypeAST("array", _type)


def p_ptr_type(p):
    "ptr_type : STAR type"
    p[0] = TypeAST("ptr", p[2])


def p_body(p):
    """body : stmt
    | body stmt"""
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[2]]


def p_stmt(p):
    """stmt : expr_stmt
    | if_stmt
    | loop_stmt
    | assign_stmt
    | var_decl
    | return_stmt
    | SEMI"""
    p[0] = p[1]


def p_return_stmt(p):
    "return_stmt : RETURN expr SEMI"
    p[0] = ReturnStmtAST(p[2])


def p_expr_stmt(p):
    "expr_stmt : expr SEMI"
    p[0] = ExprStmtAST(p[1])


def p_if_stmt(p):
    """if_stmt : IF expr LBRACE body RBRACE ELSE LBRACE body RBRACE
    | IF expr LBRACE body RBRACE
    | IF expr LBRACE body RBRACE ELSE if_stmt"""
    if len(p) == 6:
        con = {"cond": p[2], "then_body": p[4]}
    elif len(p) == 10:
        con = {
            "cond": p[2],
            "then_body": p[4],
            "else_body": p[8],
        }
    elif len(p) == 8:
        con = {
            "cond": p[2],
            "then_body": p[4],
            "elseif_body": p[7],
        }

    p[0] = IfStmtAST(**con)


def p_loop_stmt(p):
    "loop_stmt : LOOP LBRACE body RBRACE WHILE expr SEMI"
    p[0] = LoopStmtAST(p[3], p[6])


def p_assign_stmt(p):
    "assign_stmt : IDENT EQ expr SEMI"
    p[0] = AssignStmtAST(p[1], p[3])


def p_patterns(p):
    """patterns : pattern
    | patterns COMMA pattern"""
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[3]]


def p_pattern(p):
    "pattern : pattern_guard FAT_ARROW expr"
    p[0] = PatternCaseAST(p[1], p[3])

def p_pattern_guard(p):
    """pattern_guard : expr
    | STAR"""
    if p[1] == "*":
        p[0] = WildcardPatternAST()
    else:
        p[0] = ExprPatternAST(p[1])


def p_ident(p):
    "ident : IDENT"
    p[0] = VarRefAST(p[1])


def p_args(p):
    """args : arg
    | args COMMA arg"""
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[3]]


def p_arg(p):
    "arg : expr"
    p[0] = p[1]


precedence = (
    ("left", "OR"),
    ("left", "AND"),
    ("left", "EQEQ", "NEQ"),
    ("left", "LT", "GT", "LE", "GE"),
    ("left", "PLUS", "MINUS"),
    ("left", "STAR", "SLASH", "PERCENT"),
    ("right", "UNOT"),
    ("right", "UMINUS"),
)


def p_expr(p):
    """expr : literal
    | ident
    | paren_expr
    | unary_expr
    | binary_expr
    | call_expr
    | field_access_expr
    | array_access_expr
    | match_expr
    | list
    | new_struct"""
    p[0] = p[1]


def p_paren_expr(p):
    "paren_expr : LPAREN expr RPAREN"
    p[0] = p[2]


def p_unary_expr(p):
    """unary_expr : NOT expr %prec UNOT
    | MINUS expr %prec UMINUS
    | PLUS expr %prec UMINUS"""
    p[0] = UnOpAST(p[1], p[2])


def p_binary_expr(p):
    """binary_expr : expr PLUS expr
    | expr MINUS expr
    | expr STAR expr
    | expr SLASH expr
    | expr PERCENT expr
    | expr EQEQ expr
    | expr NEQ expr
    | expr LT expr
    | expr GT expr
    | expr LE expr
    | expr GE expr
    | expr AND expr
    | expr OR expr"""
    p[0] = BinOpAST(p[2], p[1], p[3])


def p_call_expr(p):
    """call_expr : IDENT LPAREN args RPAREN
    | IDENT LPAREN RPAREN"""
    if len(p) == 5:
        con = {"name": p[1], "args": p[3]}
    else:
        con = {"name": p[1], "args": []}

    p[0] = CallExprAST(**con)


def p_field_access_expr(p):
    "field_access_expr : expr DOT IDENT"
    p[0] = FieldAccessExprAST(p[1], p[3])


def p_array_access_expr(p):
    "array_access_expr : expr LBRACKET expr RBRACKET"
    p[0] = ArrayAccessExprAST(p[1], p[3])


def p_match_expr(p):
    "match_expr : MATCH expr LBRACE patterns RBRACE"
    p[0] = MatchExprAST(p[2], p[4])


def p_list(p):
    """list : LBRACKET elements RBRACKET
    | LBRACKET RBRACKET"""
    if len(p) == 4:
        p[0] = ListAST(p[2])
    else:
        p[0] = ListAST([])


def p_elements(p):
    """elements : expr
    | elements COMMA expr"""
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[3]]


def p_new_struct(p):
    """new_struct : NEW IDENT LBRACE fields_value RBRACE"""
    p[0] = NewStructAST(p[2], p[4])


def p_fields_value(p):
    """fields_value : field_value
    | fields_value COMMA field_value"""
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[3]]


def p_field_value(p):
    "field_value : IDENT COLON expr"
    p[0] = FieldValueAST(p[1], p[3])


def p_literal(p):
    """literal : INT
    | FLOAT
    | BOOLEAN
    | STRING
    """
    _type = (p[1] in ("true", "false") and bool) or type(p[1])
    p[0] = LiteralAST(value=p[1], _type=_type)


# Error handling
def p_error(p):
    if p:
        print(
            f"Syntax error at token {p.type} ({p.value}) at line {p.lineno} column {find_column(p.lexer.lexdata, p)}"
        )
    else:
        print("Syntax error at EOF")


# Build the parser
parser = yacc.yacc()

# Test the parser
# if __name__ == "__main__":
#     with open("example.bug", "r") as f:
#         code = f.read()
#     result = parser.parse(code)
#     print(result)
