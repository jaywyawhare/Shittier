import libcst as cst
import random
import string
import math
import os
import time

# List of unused imports for extra obfuscation features.
unused_imports = ["math", "os", "sys", "random", "time", "collections", "functools"]
builtin_functions = dir(__builtins__)


def get_random_unused_imports(num=3):
    """Return a random sample of unused imports."""
    return random.sample(unused_imports, num)


def generate_random_string():
    """Generate a random string with noise appended."""
    length = random.randint(7, 10)
    first_char = random.choice(string.ascii_lowercase)
    rest = "".join(random.choices(string.ascii_letters + string.digits, k=length - 1))
    return f"{first_char}{rest}_{random.randint(100, 999)}"


def add_random_spaces(code):
    """
    Insert random extra spaces (3 to 8 spaces) between every original space
    and append random dummy comments on some lines.
    """
    new_lines = []
    for line in code.splitlines():
        # Optionally append a dummy comment.
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
    """
    Generate code that calls functions from random unused imports so that they appear used.
    """
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


def generate_dead_code():
    """Generate several lines of dummy assignment code (dead code)."""
    lines = []
    for _ in range(random.randint(3, 13)):
        line = f"{generate_random_string()} = {random.randint(1, 100)}"
        lines.append(line)
    return "\n".join(lines)


def insert_dead_code(function_body):
    """
    Insert two random lines of dead code into the given function body.
    """
    dead_lines = generate_dead_code().splitlines()
    selected = random.sample(dead_lines, 2)
    return function_body + "\n" + "\n".join(selected)


def insert_opaque_predicate(if_statement):
    """
    Prepend an opaque predicate (a fake branch that never executes) to an if statement.
    """
    fake_branch = "if False:\n    pass  # Dummy branch"
    return f"{fake_branch}\n{if_statement}"


def insert_dummy_assignments(code):
    """
    After every assignment (a line containing '=' but not '=='), insert a dummy assignment.
    """
    dummy_assignments = ["dummy_var = 0", "temp = 12345", "unused_var = None"]
    new_lines = []
    for line in code.splitlines():
        new_lines.append(line)
        if "=" in line and "==" not in line:
            new_lines.append(random.choice(dummy_assignments))
    return "\n".join(new_lines)


def insert_dummy_function(module_code):
    """
    Append a dummy function to the module code if one doesn't already exist.
    """
    if "def dummy_function" not in module_code:
        dummy_function = """
def dummy_function():
    pass  # Dummy function for obfuscation
"""
        return module_code + dummy_function
    return module_code


def insert_random_dead_code_and_emojis():
    """
    Return a list of random dead code lines decorated with emojis.
    """
    emojis = ["😀", "🔥", "💀", "🚀", "🐍", "🎉", "🤖", "🛠️"]
    return [
        f"# {random.choice(emojis)}",
        f"# {random.choice(emojis)}",
        f"# {random.choice(emojis)}",
        f"# {random.choice(string.ascii_lowercase)}{generate_random_string()}_{random.randint(100, 999)} = {random.randint(1, 100)}",
        f"# {random.choice(emojis)} {random.choice(['a + b', 'x * y', 'z / w'])} = {random.randint(1, 100)}",
        f"# {random.choice(emojis)} {random.choice(['def', 'class'])} {generate_random_string()}",
        f"# {random.choice(emojis)} {random.choice(['return', 'yield'])} {generate_random_string()}",
    ]


class Shittifier(cst.CSTTransformer):
    """
    LibCST transformer that obfuscates code by renaming identifiers,
    wrapping binary expressions, and inserting opaque predicates.
    """
    def __init__(self):
        self.name_map = {}

    def get_random_name(self, original_name):
        if original_name not in self.name_map:
            noise = generate_random_string()
            random_name = f"{noise}{hash(original_name) % 1000}"
            self.name_map[original_name] = random_name
        return self.name_map[original_name]

    def leave_Name(self, original_node: cst.Name, updated_node: cst.Name) -> cst.Name:
        # Do not obfuscate built-in or special (dunder) names.
        if original_node.value in builtin_functions or original_node.value.startswith("__"):
            return updated_node
        new_name = self.get_random_name(original_node.value)
        return updated_node.with_changes(value=new_name)

    def leave_Expr(self, original_node: cst.Expr, updated_node: cst.Expr) -> cst.Expr:
        # For binary operations, wrap them with a parenthesized addition of zero.
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
        # For function calls (non-built-in), wrap them in a parenthesized expression.
        if isinstance(updated_node.value, cst.Call):
            if (
                isinstance(updated_node.value.func, cst.Name)
                and updated_node.value.func.value not in builtin_functions
            ):
                return updated_node.with_changes(value=cst.ParenthesizedExpression(value=updated_node.value))
        return updated_node

    def leave_If(self, original_node: cst.If, updated_node: cst.If) -> cst.If:
        # Insert an opaque predicate branch before the if statement.
        opaque_code = insert_opaque_predicate(updated_node.code)
        return cst.parse_statement(opaque_code)

    def leave_Import(self, original_node: cst.Import, updated_node: cst.Import) -> cst.Import:
        existing_imports = [alias.name.value for alias in updated_node.names]
        extra_imports = [
            cst.ImportAlias(name=cst.Name(value=module))
            for module in get_random_unused_imports()
            if module not in existing_imports
        ]
        return updated_node.with_changes(
            names=updated_node.names + tuple(extra_imports)
        )

    def leave_Module(self, original_node: cst.Module, updated_node: cst.Module) -> cst.Module:
        # Insert a dummy function into the module if not present.
        module_code = updated_node.code
        module_code = insert_dummy_function(module_code)
        return cst.parse_module(module_code)


def shittify_code(code: str) -> str:
    """
    Shittify the input code by applying LibCST transformations and then
    additional string-based obfuscations.
    """
    # Separate import lines and non-import lines.
    import_lines = [line for line in code.splitlines() if line.strip().startswith(("import", "from"))]
    non_import_lines = [line for line in code.splitlines() if not line.strip().startswith(("import", "from"))]

    # Apply LibCST transformations to non-import code.
    tree = cst.parse_module("\n".join(non_import_lines))
    transformer = Shittifier()
    transformed_tree = tree.visit(transformer)
    final_code = transformed_tree.code

    # Prepend original import lines.
    if import_lines:
        final_code = "\n".join(import_lines) + "\n" + final_code

    # Append random calls from unused imports.
    final_code += "\n" + call_random_import_functions()

    # Insert dummy assignments after assignment lines.
    final_code = insert_dummy_assignments(final_code)

    # Insert random dead code lines before some lines (avoiding exponential growth).
    final_lines = []
    dead_code_lines = insert_random_dead_code_and_emojis()
    for line in final_code.splitlines():
        if random.random() < 0.7:
            final_lines.append(random.choice(dead_code_lines))
        final_lines.append(line)
    final_code = "\n".join(final_lines)

    # Optionally, add random extra spaces and dummy comments.
    final_code = add_random_spaces(final_code)
    return final_code


if __name__ == "__main__":
    original_code = """
import math
def example_function(x, y):
    return x + y

a = 5
b = 10
c = 10 + 1
z = example_function(a, b)
print(z)
"""
    shittified_code = shittify_code(original_code)
    print(shittified_code)
