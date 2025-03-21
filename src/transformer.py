import libcst as cst
import random
import string

unused_imports = ["math", "os", "sys", "random", "time", "collections", "functools"]
builtin_functions = dir(__builtins__)


def get_random_unused_imports(num=3):
    return random.sample(unused_imports, num)


def generate_random_string():
    length = random.randint(7, 10)
    first_char = random.choice(string.ascii_lowercase)
    rest = "".join(random.choices(string.ascii_letters + string.digits, k=length - 1))
    return f"{first_char}{rest}_{random.randint(100, 999)}"


def add_random_spaces(code):
    new_lines = []
    for line in code.splitlines():
        if random.random() < 0.25:
            line += f"  # {generate_random_string()}"
        modified_line = []
        for char in line:
            if char == " ":
                modified_line.append(" " * random.randint(3, 8))
            else:
                modified_line.append(char)
        new_lines.append("".join(modified_line))
    return "\n".join(new_lines)


def call_random_import_functions():
    calls = []
    if "math" in unused_imports:
        calls.append("import math")
        calls.append("math.sqrt(25)")
    if "os" in unused_imports:
        calls.append("import os")
        calls.append("os.path.exists('/some/path')")
    if "time" in unused_imports:
        calls.append("import time")
        calls.append("time.sleep(1)")
    return "\n".join(calls)


def insert_dummy_assignments(code):
    dummy_assignments = ["dummy_var = 0", "temp = 12345", "unused_var = None"]
    new_lines = []
    for line in code.splitlines():
        new_lines.append(line)
        if "=" in line and "==" not in line:
            new_lines.append(random.choice(dummy_assignments))
    return "\n".join(new_lines)


class Shittier(cst.CSTTransformer):
    def __init__(self):
        self.name_map = {}

    def get_random_name(self, original_name):
        if original_name not in self.name_map:
            noise = generate_random_string()
            random_name = f"{noise}{hash(original_name) % 1000}"
            self.name_map[original_name] = random_name
        return self.name_map[original_name]

    def leave_Name(self, original_node: cst.Name, updated_node: cst.Name) -> cst.Name:
        if original_node.value in builtin_functions or original_node.value.startswith("__"):
            return updated_node
        new_name = self.get_random_name(original_node.value)
        return updated_node.with_changes(value=new_name)

    def leave_Expr(self, original_node: cst.Expr, updated_node: cst.Expr) -> cst.Expr:
        if isinstance(updated_node.value, cst.BinaryOperation):
            new_expr = cst.BinaryOperation(
                left=cst.ParenthesizedExpression(value=updated_node.value),
                operator=cst.Add(
                    whitespace_before=cst.SimpleWhitespace(" "),
                    whitespace_after=cst.SimpleWhitespace(" "),
                ),
                right=cst.Integer("0"),
            )
            return updated_node.with_changes(value=new_expr)
        if isinstance(updated_node.value, cst.Call):
            if (
                isinstance(updated_node.value.func, cst.Name)
                and updated_node.value.func.value not in builtin_functions
            ):
                return updated_node.with_changes(value=cst.ParenthesizedExpression(value=updated_node.value))
        return updated_node

    def leave_If(self, original_node: cst.If, updated_node: cst.If) -> cst.If:
        fake_branch = "if False:\n    pass  # Dummy branch"
        opaque_code = f"{fake_branch}\n{updated_node.code}"
        return cst.parse_statement(opaque_code)

    def leave_Import(self, original_node: cst.Import, updated_node: cst.Import) -> cst.Import:
        existing_imports = [alias.name.value for alias in updated_node.names]
        extra_imports = [
            cst.ImportAlias(name=cst.Name(value=module))
            for module in get_random_unused_imports()
            if module not in existing_imports
        ]
        return updated_node.with_changes(names=updated_node.names + tuple(extra_imports))

    def leave_Module(self, original_node: cst.Module, updated_node: cst.Module) -> cst.Module:
        # For simplicity, do not modify module-level structure.
        return updated_node


def shittify_code(code: str) -> str:
    tree = cst.parse_module(code)
    transformer = Shittier()
    transformed_tree = tree.visit(transformer)
    final_code = transformed_tree.code

    final_code = insert_dummy_assignments(final_code)
    final_code += "\n" + call_random_import_functions()
    final_code = add_random_spaces(final_code)
    return final_code
