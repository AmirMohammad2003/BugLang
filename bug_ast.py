class BaseAST:
    def __init__(self):
        self.parent = None
        self.children = []

    def add_child(self, child):
        self.children.append(child)
        if isinstance(child, BaseAST):
            child.parent = self

    def remove_child(self, child):
        self.children.remove(child)
        child.parent = None

    def replace_child(self, old_child, new_child):
        index = self.children.index(old_child)
        self.children[index] = new_child
        new_child.parent = self
        old_child.parent = None

    def get_root(self):
        node = self
        while node.parent is not None:
            node = node.parent
        return node

    def get_siblings(self):
        return [child for child in self.parent.children if child != self]

    def get_children(self):
        return self.children

    def get_parent(self):
        return self.parent

    def get_ancestors(self):
        ancestors = []
        node = self.parent
        while node is not None:
            ancestors.append(node)
            node = node.parent
        return ancestors

    def get_descendants(self):
        descendants = []
        for child in self.children:
            descendants.append(child)
            descendants.extend(child.get_descendants())
        return descendants

    def __str__(self):
        return self.__class__.__name__ + "(" + ", ".join(str(child) for child in self.children) + ")"

    __repr__ = __str__
    
class ModuleAST(BaseAST):
    def __init__(self, decls):
        super().__init__()
        for decl in decls:
            self.add_child(decl)

class DeclAST(BaseAST):
    def __init__(self):
        super().__init__()

class FnDeclAST(DeclAST):
    def __init__(self, name, params, ret_type, body):
        super().__init__()
        self.add_child(name)
        self.add_child(params)
        self.add_child(ret_type)
        self.add_child(body)


class VarDeclAST(DeclAST):
    def __init__(self, name, _type, value):
        super().__init__()
        self.add_child(name)
        self.add_child(_type)
        self.add_child(value)

class StructDeclAST(DeclAST):
    def __init__(self, name, fields):
        super().__init__()
        self.add_child(name)
        self.add_child(fields)

class EnumDeclAST(DeclAST):
    def __init__(self, name, variants):
        super().__init__()
        self.add_child(name)
        self.add_child(variants)

class ParamAST(BaseAST):
    def __init__(self, name, _type):
        super().__init__()
        self.add_child(name)
        self.add_child(_type)

class FieldAST(BaseAST):
    def __init__(self, name, _type):
        super().__init__()
        self.add_child(name)
        self.add_child(_type)

class VariantAST(BaseAST):
    def __init__(self, name, value):
        super().__init__()
        self.add_child(name)
        self.add_child(value)

class TypeAST(BaseAST):
    def __init__(self, _type, *args):
        super().__init__()
        self.add_child(_type)
        for arg in args:
            self.add_child(arg)

class ExprAST(BaseAST):
    def __init__(self):
        super().__init__()

class GeneralExprAST(ExprAST):
    def __init__(self, expr):
        super().__init__()
        self.add_child(expr)

class CallExprAST(ExprAST):
    def __init__(self, name, args):
        super().__init__()
        self.add_child(name)
        self.add_child(args)

class FieldAccessExprAST(ExprAST):
    def __init__(self, expr, field):
        super().__init__()
        self.add_child(expr)
        self.add_child(field)

class ArrayAccessExprAST(ExprAST):
    def __init__(self, expr, index):
        super().__init__()
        self.add_child(expr)
        self.add_child(index)

class MatchExprAST(ExprAST):
    def __init__(self, expr, patterns):
        super().__init__()
        self.add_child(expr)
        self.add_child(patterns)

class ListAST(ExprAST):
    def __init__(self, elements):
        super().__init__()
        for element in elements:
            self.add_child(element)

class NewStructAST(ExprAST):
    def __init__(self, name, fields):
        super().__init__()
        self.add_child(name)
        self.add_child(fields)

class FieldValueAST(BaseAST):
    def __init__(self, name, expr):
        super().__init__()
        self.add_child(name)
        self.add_child(expr)

class LiteralAST(ExprAST):
    def __init__(self, value, _type):
        super().__init__()
        self.add_child(value)
        self.add_child(_type)


class BinOpAST(ExprAST):
    def __init__(self, op, left, right):
        super().__init__()
        self.add_child(op)
        self.add_child(left)
        self.add_child(right)

class UnOpAST(ExprAST):
    def __init__(self, op, expr):
        super().__init__()
        self.add_child(op)
        self.add_child(expr)

class VarRefAST(ExprAST):
    def __init__(self, name):
        super().__init__()
        self.add_child(name)


class PatternAST(BaseAST):
    def __init__(self):
        super().__init__()

class WildcardPatternAST(PatternAST):
    def __init__(self):
        super().__init__()
        

class ExprPatternAST(PatternAST):
    def __init__(self, expr):
        super().__init__()
        self.add_child(expr)
    
class PatternCaseAST(BaseAST):
    def __init__(self, pattern, expr):
        super().__init__()
        self.add_child(pattern)
        self.add_child(expr)


class StatementAST(BaseAST):
    def __init__(self, *args, **kwargs):
        super().__init__()

class ExprStmtAST(StatementAST):
    def __init__(self, expr):
        super().__init__()
        self.add_child(expr)

class ReturnStmtAST(StatementAST):
    def __init__(self, expr):
        super().__init__()
        self.add_child(expr)

class IfStmtAST(StatementAST):
    def __init__(self, cond, then_body, else_body=None, elseif_body=None):
        super().__init__()
        self.add_child(cond)
        self.add_child(then_body)
        if else_body is not None:
            self.add_child(else_body)
        if elseif_body is not None:
            self.add_child(elseif_body)

class LoopStmtAST(StatementAST):
    def __init__(self, body, cond):
        super().__init__()
        self.add_child(body)
        self.add_child(cond)
    
class AssignStmtAST(StatementAST):
    def __init__(self, name, expr):
        super().__init__()
        self.add_child(name)
        self.add_child(expr)

