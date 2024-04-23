from sys import argv

from bug_ast import TypeAST
from bug_parser import parser


class Visitor:
    def visit(self, node):
        method_name = "visit_" + type(node).__name__
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        raise Exception(f"No visit_{type(node).__name__} method")

    @staticmethod
    def primitive_type(_type):
        if isinstance(_type, TypeAST):
            _type = _type.children[0]
        if _type == "i32":
            return "int"
        elif _type == "i64":
            return "long long"
        elif _type == "bool":
            return "bool"
        elif _type == "f32":
            return "float"
        elif _type == "f64":
            return "double"
        elif _type == "string":
            return "char*"
        elif _type == "char":
            return "char"
        else:
            return _type

    def visit_ModuleAST(self, node):
        code = "#include <stdio.h>\n#include \"bug.h\"\n"
        for decl in node.children:
            code += self.visit(decl)

        return code

    def visit_FnDeclAST(self, node):
        name = node.children[0]
        params = []
        for param in node.children[1]:
            params += [self.visit(param)]

        params = ", ".join(params)

        ret_type = ''.join(self.visit(node.children[2]))
        body = ""
        for stmt in node.children[3]:
            body += self.visit(stmt) + "\n"

        code = f"{ret_type} {name}({params}) {{\n"
        code += f"    {body}\n"
        code += "}\n\n"

        return code

    def visit_VarDeclAST(self, node):
        name = self.visit(node.children[0])
        _type = self.visit(node.children[1])
        value = self.visit(node.children[2])
        if len(_type) == 2:
            return f"{_type[0]} {name}{_type[1]} = {value};"
        return f"{_type} {name} = {value};"

    def visit_StructDeclAST(self, node):
        name = self.visit(node.children[0])
        fields = self.visit(node.children[1])

        code = "typedef struct {\n"
        for field in fields:
            code += f"    {field}\n"
        code += f"}} {name};\n"

        return code

    def visit_EnumDeclAST(self, node):
        name = self.visit(node.children[0])
        variants = self.visit(node.children[1])

        code = f"enum {name} {{\n"
        for variant in variants:
            code += f"    {variant},\n"
        code += "};\n"

        return code

    def visit_ParamAST(self, node):
        name = node.children[0]
        _type = self.visit(node.children[1])

        return f"{_type} {name}"

    def visit_FieldAST(self, node):
        name = node.children[0]
        _type = self.visit(node.children[1])

        return f"{_type} {name};"

    def visit_VariantAST(self, node):
        name = node.children[0]
        value = self.visit(node.children[1])

        return f"{name} = {value}"

    def visit_VarRefAST(self, node):
        return node.children[0]

    def visit_TypeAST(self, node):
        if node.children[0] == "array":
            if len(node.children) == 2:
                return f"{self.primitive_type(node.children[1])}", '[]'
            else:
                return f"{self.primitive_type(node.children[1])}", f"[{node.children[2]}]"
        elif node.children[0] == "ptr":
            return f"{self.primitive_type(node.children[1])}*"
        return self.primitive_type(node.children[0])

    def visit_ExprStmtAST(self, node):
        return self.visit(node.children[0]) + ";"

    def visit_ReturnStmtAST(self, node):
        return f"return {self.visit(node.children[0])};"

    def visit_IfStmtAST(self, node):
        condition = self.visit(node.children[0])
        body = "\n".join(self.visit(node.children[1]))
        if len(node.children) == 3:
            else_body = "\n".join(self.visit(node.children[2]))
            return f"if ({condition}) {{\n    {body}\n}} else {{\n    {else_body}\n}}"
        return f"if ({condition}) {{\n    {body}\n}}"

    def visit_LoopStmtAST(self, node):
        cond = self.visit(node.children[1])
        body = "\n".join(self.visit(node.children[0]))
        return f"while ({cond}) {{\n    {body}\n}}"

    def visit_AssignStmtAST(self, node):
        name = self.visit(node.children[0])
        value = self.visit(node.children[1])
        return f"{name} = {value};"

    def visit_GeneralExprAST(self, node):
        return self.visit(node.children[0])

    def visit_CallExprAST(self, node):
        name = self.visit(node.children[0])
        args = ', '.join(self.visit(node.children[1]))

        return f"{name}({args})"

    def visit_FieldAccessExpr(self, node):
        name = self.visit(node.children[0])
        field = self.visit(node.children[1])

        return f"{name}.{field}"

    def visit_ArrayAccessExprAST(self, node):
        name = self.visit(node.children[0])
        index = self.visit(node.children[1])

        return f"{name}[{index}]"

    def visit_MatchExprAST(self, node):
        expr = self.visit(node.children[0])
        cases = self.visit(node.children[1])

        normal_cases = []
        for case in cases:
            if not case.startswith("{"):
                normal_cases.append(f"if ({expr} == " + case)

        else_case = ""
        for case in cases:
            if case.startswith("{"):
                else_case = case
                break

        code = " else ".join(normal_cases)
        if else_case:
            code += f" else {else_case}"

        return code

    def visit_LiteralAST(self, node):
        if node.children[1] == str:
            return f'"{node.children[0]}"'
        return node.children[0]

    def visit_BinOpAST(self, node):
        left = self.visit(node.children[1])
        op = self.visit(node.children[0])
        right = self.visit(node.children[2])

        return f"{left} {op} {right}"

    def visit_UnaryOpAST(self, node):
        op = self.visit(node.children[0])
        operand = self.visit(node.children[1])

        return f"{op}{operand}"

    def visit_ListAST(self, node):
        return "{" + ", ".join([str(self.visit(child)) for child in node.children]) + "}"

    def visit_PatternCaseAST(self, node):
        cond = self.visit(node.children[0])
        body = self.visit(node.children[1]) + ";"
        if cond == "":
            return f"{{{body}}}"
        return f"{cond} ){{ {body} }}"

    def visit_WildcardPatternAST(self, node):
        return ""

    def visit_ExprPatternAST(self, node):
        return self.visit(node.children[0])

    def visit_NewStructAST(self, node):
        # name = self.visit(node.children[0])
        fields = ','.join(self.visit(node.children[1]))

        return f"{{ {fields} }}"

    def visit_FieldValueAST(self, node):
        name = self.visit(node.children[0])
        value = self.visit(node.children[1])

        return f".{name} = {value}"

    def visit_str(self, node):
        return node


    def visit_list(self, node):
        x = []
        for child in node:
            x.append(str(self.visit(child)))

        return x


def main():
    with open(argv[1], "r") as f:
        data = f.read()
    result = parser.parse(data)
    # print(result)
    root = Visitor().visit(result)
    print(root)


if __name__ == "__main__":
    main()
