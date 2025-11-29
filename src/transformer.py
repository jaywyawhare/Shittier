import ast
import random
from src.utils import (
    select_random_unused_libraries,
    generate_random_variable_name,
    add_random_spacing_to_code,
    insert_dummy_variable_assignments,
    generate_random_import_statements,
)

try:
    from src.transformer_libcst import obfuscate_code_with_libcst
    LIBCST_AVAILABLE = True
except ImportError:
    LIBCST_AVAILABLE = False


try:
    if isinstance(__builtins__, dict):
        builtin_identifiers = set(__builtins__.keys())
    else:
        builtin_identifiers = set(dir(__builtins__))
except:
    builtin_identifiers = set(dir(__builtins__))
builtin_identifiers.update(['print', 'len', 'range', 'str', 'int', 'float', 'list', 'dict', 'tuple', 'set', 'bool', 'type', 'isinstance', 'hasattr', 'getattr', 'setattr', 'delattr', 'callable', 'iter', 'next', 'enumerate', 'zip', 'map', 'filter', 'sorted', 'reversed', 'sum', 'max', 'min', 'abs', 'round', 'divmod', 'pow', 'all', 'any', 'bin', 'hex', 'oct', 'ord', 'chr', 'ascii', 'repr', 'eval', 'exec', 'compile', 'open', 'input', 'exit', 'quit'])


class CodeObfuscatorAST(ast.NodeTransformer):

    def __init__(self):
        """
        Initialize the AST obfuscator with empty identifier map and imported modules set.
        
        @return: None
        """
        super().__init__()
        self.identifier_map = {}
        self.imported_modules = set()

    def create_random_identifier(self, original_name: str) -> str:
        """
        Create or retrieve a random identifier for the given original name.
        
        @param original_name: Original identifier name
        @return: Random identifier string
        """
        if original_name not in self.identifier_map:
            noise = generate_random_variable_name()
            random_name = f"{noise}{hash(original_name) % 1000}"
            self.identifier_map[original_name] = random_name
        return self.identifier_map[original_name]

    def visit_Name(self, node: ast.Name) -> ast.Name:
        """
        Visit Name nodes and rename non-builtin identifiers.
        
        @param node: AST Name node
        @return: Modified or original Name node
        """
        if node.id in builtin_identifiers or node.id.startswith("__") or node.id in self.imported_modules:
            return node
        new_id = self.create_random_identifier(node.id)
        return ast.copy_location(ast.Name(id=new_id, ctx=node.ctx), node)

    def visit_Attribute(self, node: ast.Attribute) -> ast.Attribute:
        """
        Visit Attribute nodes and rename attributes while preserving builtin methods.
        
        @param node: AST Attribute node
        @return: Modified or original Attribute node
        """
        self.generic_visit(node)
        if node.attr.startswith("__") or node.attr in builtin_identifiers:
            return node
        
        if isinstance(node.value, ast.Name):
            if node.value.id in ['math', 'os', 'sys', 'random', 'time', 'collections', 'functools', 
                                 'string', 'json', 're', 'datetime', 'itertools', 'operator', 
                                 'functools', 'collections', 'heapq', 'bisect', 'array', 'copy',
                                 'pickle', 'sqlite3', 'csv', 'xml', 'html', 'urllib', 'http',
                                 'socket', 'ssl', 'email', 'base64', 'hashlib', 'hmac', 'secrets',
                                 'zlib', 'gzip', 'bz2', 'lzma', 'shutil', 'glob', 'fnmatch',
                                 'linecache', 'shlex', 'configparser', 'argparse', 'getopt',
                                 'logging', 'warnings', 'traceback', 'pdb', 'profile', 'pstats',
                                 'timeit', 'doctest', 'unittest', 'test', 'lib2to3', 'typing',
                                 'dataclasses', 'enum', 'numbers', 'decimal', 'fractions', 'statistics',
                                 'cmath', 'array', 'collections', 'collections.abc', 'heapq',
                                 'bisect', 'weakref', 'types', 'copy', 'pprint', 'reprlib',
                                 'enum', 'numbers', 'math', 'cmath', 'decimal', 'fractions',
                                 'statistics', 'unicodedata', 'stringprep', 'readline', 'rlcompleter']:
                return node
        
        builtin_methods = {'append', 'extend', 'insert', 'remove', 'pop', 'clear', 'index', 
                          'count', 'sort', 'reverse', 'copy', 'keys', 'values', 'items',
                          'get', 'setdefault', 'popitem', 'update', 'join', 'split', 'strip',
                          'replace', 'find', 'index', 'count', 'startswith', 'endswith',
                          'upper', 'lower', 'capitalize', 'title', 'swapcase', 'isalnum',
                          'isalpha', 'isdigit', 'islower', 'isupper', 'isspace', 'istitle',
                          'ljust', 'rjust', 'center', 'zfill', 'expandtabs', 'translate',
                          'partition', 'rpartition', 'rsplit', 'splitlines', 'format', 'format_map'}
        if node.attr in builtin_methods:
            return node
        
        new_attr = self.create_random_identifier(node.attr)
        return ast.copy_location(
            ast.Attribute(
                value=node.value,
                attr=new_attr,
                ctx=node.ctx,
                lineno=node.lineno,
                col_offset=node.col_offset,
            ),
            node,
        )

    def visit_FunctionDef(self, node: ast.FunctionDef) -> ast.FunctionDef:
        """
        Visit FunctionDef nodes and rename function names.
        
        @param node: AST FunctionDef node
        @return: Modified or original FunctionDef node
        """
        self.generic_visit(node)
        if node.name not in builtin_identifiers and not node.name.startswith("__"):
            new_name = self.create_random_identifier(node.name)
            return ast.copy_location(
                ast.FunctionDef(
                    name=new_name,
                    args=node.args,
                    body=node.body,
                    decorator_list=node.decorator_list,
                    returns=node.returns,
                    lineno=node.lineno,
                    col_offset=node.col_offset,
                ),
                node,
            )
        return node

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> ast.AsyncFunctionDef:
        """
        Visit AsyncFunctionDef nodes and rename async function names.
        
        @param node: AST AsyncFunctionDef node
        @return: Modified or original AsyncFunctionDef node
        """
        self.generic_visit(node)
        if node.name not in builtin_identifiers and not node.name.startswith("__"):
            new_name = self.create_random_identifier(node.name)
            return ast.copy_location(
                ast.AsyncFunctionDef(
                    name=new_name,
                    args=node.args,
                    body=node.body,
                    decorator_list=node.decorator_list,
                    returns=node.returns,
                    lineno=node.lineno,
                    col_offset=node.col_offset,
                ),
                node,
            )
        return node

    def visit_ClassDef(self, node: ast.ClassDef) -> ast.ClassDef:
        """
        Visit ClassDef nodes and rename class names.
        
        @param node: AST ClassDef node
        @return: Modified or original ClassDef node
        """
        self.generic_visit(node)
        if node.name not in builtin_identifiers and not node.name.startswith("__"):
            new_name = self.create_random_identifier(node.name)
            return ast.copy_location(
                ast.ClassDef(
                    name=new_name,
                    bases=node.bases,
                    keywords=node.keywords,
                    body=node.body,
                    decorator_list=node.decorator_list,
                    lineno=node.lineno,
                    col_offset=node.col_offset,
                ),
                node,
            )
        return node

    def visit_arg(self, node: ast.arg) -> ast.arg:
        """
        Visit arg nodes and rename function arguments.
        
        @param node: AST arg node
        @return: Modified or original arg node
        """
        self.generic_visit(node)
        if node.arg not in builtin_identifiers and not node.arg.startswith("__"):
            new_arg = self.create_random_identifier(node.arg)
            return ast.copy_location(
                ast.arg(
                    arg=new_arg,
                    annotation=node.annotation,
                    lineno=node.lineno,
                    col_offset=node.col_offset,
                ),
                node,
            )
        return node

    def visit_BinOp(self, node: ast.BinOp) -> ast.BinOp:
        """
        Visit BinOp nodes and wrap numeric operations with dummy additions.
        
        @param node: AST BinOp node
        @return: Modified or original BinOp node
        """
        self.generic_visit(node)
        if isinstance(node.op, (ast.Sub, ast.Mult, ast.Div, ast.Mod, ast.FloorDiv, ast.Pow)):
            new_node = ast.BinOp(
                left=node,
                op=ast.Add(),
                right=ast.Constant(value=0),
            )
            return ast.copy_location(new_node, node)
        elif isinstance(node.op, ast.Add):
            def is_numeric_constant(n):
                if isinstance(n, ast.Constant):
                    return isinstance(n.value, (int, float))
                if hasattr(ast, 'Num') and isinstance(n, ast.Num):
                    return isinstance(n.n, (int, float))
                return False
            left_is_num = is_numeric_constant(node.left)
            right_is_num = is_numeric_constant(node.right)
            if left_is_num and right_is_num:
                new_node = ast.BinOp(
                    left=node,
                    op=ast.Add(),
                    right=ast.Constant(value=0),
                )
                return ast.copy_location(new_node, node)
        return node

    def visit_If(self, node: ast.If) -> ast.If:
        """
        Visit If nodes and insert a fake branch at the beginning.
        
        @param node: AST If node
        @return: Modified If node with fake branch
        """
        self.generic_visit(node)
        fake_branch = ast.If(
            test=ast.Constant(value=False),
            body=[ast.Pass()],
            orelse=[],
        )
        new_body = [fake_branch] + node.body
        return ast.copy_location(
            ast.If(
                test=node.test,
                body=new_body,
                orelse=node.orelse,
            ),
            node,
        )

    def visit_Import(self, node: ast.Import) -> ast.Import:
        """
        Visit Import nodes, track imported modules, and add extra unused imports.
        
        @param node: AST Import node
        @return: Modified Import node with extra imports
        """
        for alias in node.names:
            module_name = alias.asname if alias.asname else alias.name
            self.imported_modules.add(module_name)
            if alias.asname and alias.name != alias.asname:
                self.imported_modules.add(alias.name)
        self.generic_visit(node)
        existing = {alias.name for alias in node.names} if node.names else set()
        extra_aliases = [
            ast.alias(name=module, asname=None)
            for module in select_random_unused_libraries()
            if module not in existing
        ]
        new_names = node.names + extra_aliases if node.names else extra_aliases
        return ast.copy_location(ast.Import(names=new_names), node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> ast.ImportFrom:
        """
        Visit ImportFrom nodes and track imported module names.
        
        @param node: AST ImportFrom node
        @return: Original ImportFrom node
        """
        if node.module:
            self.imported_modules.add(node.module)
        self.generic_visit(node)
        return node

    def visit_Module(self, node: ast.Module) -> ast.Module:
        """
        Visit Module nodes and ensure structure remains intact.
        
        @param node: AST Module node
        @return: Modified Module node
        """
        self.generic_visit(node)
        return node


def _obfuscate_code_with_ast_fallback(source_code: str) -> str:
    """
    Fallback AST-based obfuscation when libcst is not available.
    
    @param source_code: Python source code as a string
    @return: Obfuscated Python source code as a string
    """
    if not source_code or not source_code.strip():
        raise ValueError("Source code cannot be empty")
    
    try:
        tree = ast.parse(source_code)
    except SyntaxError as e:
        raise SyntaxError(f"Invalid Python syntax: {e}") from e
    except Exception as e:
        raise RuntimeError(f"Failed to parse source code: {e}") from e

    transformer = CodeObfuscatorAST()
    transformed_tree = transformer.visit(tree)
    
    try:
        final_code = ast.unparse(transformed_tree)
    except AttributeError:
        raise RuntimeError(
            "ast.unparse requires Python 3.9+. "
            "Please upgrade Python or install libcst: pip install libcst"
        )

    final_code = insert_dummy_variable_assignments(final_code)
    final_code += "\n" + generate_random_import_statements()
    final_code = add_random_spacing_to_code(final_code)

    try:
        ast.parse(final_code)
    except SyntaxError as e:
        raise SyntaxError(f"Obfuscation introduced invalid syntax: {e}") from e

    return final_code


def obfuscate_code_with_ast(source_code: str) -> str:
    """
    Main obfuscation function using libcst if available, otherwise AST fallback.
    
    @param source_code: Python source code as a string
    @return: Obfuscated Python source code as a string
    """
    if LIBCST_AVAILABLE:
        return obfuscate_code_with_libcst(source_code)
    else:
        return _obfuscate_code_with_ast_fallback(source_code)


shittify_code = obfuscate_code_with_ast
