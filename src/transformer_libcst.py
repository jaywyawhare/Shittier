import libcst as cst
import random
from src.utils import (
    select_random_unused_libraries,
    generate_random_variable_name,
    add_random_spacing_to_code,
    insert_dummy_variable_assignments,
    generate_random_import_statements,
)


try:
    if isinstance(__builtins__, dict):
        builtin_identifiers = set(__builtins__.keys())
    else:
        builtin_identifiers = set(dir(__builtins__))
except:
    builtin_identifiers = set(dir(__builtins__))
builtin_identifiers.update([
    'print', 'len', 'range', 'str', 'int', 'float', 'list', 'dict', 'tuple', 'set',
    'bool', 'type', 'isinstance', 'hasattr', 'getattr', 'setattr', 'delattr',
    'callable', 'iter', 'next', 'enumerate', 'zip', 'map', 'filter', 'sorted',
    'reversed', 'sum', 'max', 'min', 'abs', 'round', 'divmod', 'pow', 'all', 'any',
    'bin', 'hex', 'oct', 'ord', 'chr', 'ascii', 'repr', 'eval', 'exec', 'compile',
    'open', 'input', 'exit', 'quit'
])


class CodeObfuscatorCST(cst.CSTTransformer):

    def __init__(self):
        """
        Initialize the LibCST obfuscator with empty maps and sets.
        
        @return: None
        """
        super().__init__()
        self.identifier_map = {}
        self.imported_modules = set()
        self.function_params = {}

    def get_random_identifier(self, original_name: str) -> str:
        """
        Get or create a random identifier for the given original name.
        
        @param original_name: Original identifier name
        @return: Random identifier string
        """
        if original_name not in self.identifier_map:
            noise = generate_random_variable_name()
            random_name = f"{noise}{hash(original_name) % 1000}"
            self.identifier_map[original_name] = random_name
        return self.identifier_map[original_name]

    def leave_Name(self, original_node: cst.Name, updated_node: cst.Name) -> cst.Name:
        """
        Rename identifiers while preserving builtins and dunder names.
        
        @param original_node: Original LibCST Name node
        @param updated_node: Updated LibCST Name node
        @return: Modified or original Name node
        """
        if (original_node.value in builtin_identifiers or
            original_node.value.startswith("__") or
            original_node.value in self.imported_modules):
            return updated_node
        
        if updated_node.value in self.identifier_map.values():
            return updated_node
        
        original_name = original_node.value
        new_name = self.get_random_identifier(original_name)
        return updated_node.with_changes(value=new_name)

    def leave_Attribute(self, original_node: cst.Attribute, updated_node: cst.Attribute) -> cst.Attribute:
        """
        Rename attribute names but preserve builtin methods and module attributes.
        
        @param original_node: Original LibCST Attribute node
        @param updated_node: Updated LibCST Attribute node
        @return: Modified or original Attribute node
        """
        module_name = None
        if isinstance(original_node.value, cst.Name):
            module_name = original_node.value.value
        elif isinstance(updated_node.value, cst.Name):
            updated_module_name = updated_node.value.value
            for orig, renamed in self.identifier_map.items():
                if renamed == updated_module_name and orig in self.imported_modules:
                    module_name = orig
                    break
            if not module_name:
                module_name = updated_module_name
        elif isinstance(original_node.value, cst.Attribute):
            base_attr = original_node.value
            while isinstance(base_attr.value, cst.Attribute):
                base_attr = base_attr.value
            if isinstance(base_attr.value, cst.Name):
                base_module = base_attr.value.value
                if base_module in self.imported_modules:
                    if updated_node.attr.value != original_node.attr.value:
                        return updated_node.with_changes(attr=updated_node.attr.with_changes(value=original_node.attr.value))
                    return updated_node
        
        if module_name:
            if module_name in self.imported_modules:
                if updated_node.attr.value != original_node.attr.value:
                    return updated_node.with_changes(attr=updated_node.attr.with_changes(value=original_node.attr.value))
                return updated_node

        builtin_methods = {
            'append', 'extend', 'insert', 'remove', 'pop', 'clear', 'index', 'count',
            'sort', 'reverse', 'copy', 'keys', 'values', 'items', 'get', 'setdefault',
            'popitem', 'update', 'join', 'split', 'strip', 'replace', 'find',
            'startswith', 'endswith', 'upper', 'lower', 'capitalize', 'title'
        }
        if updated_node.attr.value in builtin_methods:
            return updated_node

        if updated_node.attr.value.startswith("__"):
            return updated_node

        original_attr_name = original_node.attr.value
        if original_attr_name in self.identifier_map:
            new_attr = self.identifier_map[original_attr_name]
        else:
            new_attr = self.get_random_identifier(original_attr_name)
        
        return updated_node.with_changes(attr=updated_node.attr.with_changes(value=new_attr))

    def visit_FunctionDef(self, original_node: cst.FunctionDef) -> bool:
        """
        Track function parameters before visiting the body.
        
        @param original_node: Original LibCST FunctionDef node
        @return: True to continue visiting
        """
        for param in original_node.params.params:
            param_name = param.name.value
            if param_name not in builtin_identifiers and not param_name.startswith("__"):
                self.get_random_identifier(param_name)
        return True
    
    def leave_FunctionDef(self, original_node: cst.FunctionDef, updated_node: cst.FunctionDef) -> cst.FunctionDef:
        """
        Rename function names while preserving builtins.
        
        @param original_node: Original LibCST FunctionDef node
        @param updated_node: Updated LibCST FunctionDef node
        @return: Modified or original FunctionDef node
        """
        if (original_node.name.value not in builtin_identifiers and
            not original_node.name.value.startswith("__")):
            new_name = self.get_random_identifier(original_node.name.value)
            return updated_node.with_changes(name=updated_node.name.with_changes(value=new_name))
        return updated_node

    def visit_ClassDef(self, original_node: cst.ClassDef) -> bool:
        """
        Pre-create mappings for class methods before visiting.
        
        @param original_node: Original LibCST ClassDef node
        @return: True to continue visiting
        """
        body = original_node.body
        if isinstance(body, cst.IndentedBlock):
            for stmt in body.body:
                if isinstance(stmt, cst.FunctionDef):
                    method_name = stmt.name.value
                    if method_name not in builtin_identifiers and not method_name.startswith("__"):
                        self.get_random_identifier(method_name)
        return True
    
    def leave_ClassDef(self, original_node: cst.ClassDef, updated_node: cst.ClassDef) -> cst.ClassDef:
        """
        Rename class names while preserving builtins.
        
        @param original_node: Original LibCST ClassDef node
        @param updated_node: Updated LibCST ClassDef node
        @return: Modified or original ClassDef node
        """
        if (original_node.name.value not in builtin_identifiers and
            not original_node.name.value.startswith("__")):
            new_name = self.get_random_identifier(original_node.name.value)
            return updated_node.with_changes(name=updated_node.name.with_changes(value=new_name))
        return updated_node

    def leave_Param(self, original_node: cst.Param, updated_node: cst.Param) -> cst.Param:
        """
        Rename function parameters using pre-created mappings.
        
        @param original_node: Original LibCST Param node
        @param updated_node: Updated LibCST Param node
        @return: Modified or original Param node
        """
        param_name = original_node.name.value
        if (param_name not in builtin_identifiers and
            not param_name.startswith("__")):
            new_name = self.get_random_identifier(param_name)
            return updated_node.with_changes(name=updated_node.name.with_changes(value=new_name))
        return updated_node

    def visit_Import(self, original_node: cst.Import) -> bool:
        """
        Track imported modules before visiting.
        
        @param original_node: Original LibCST Import node
        @return: True to continue visiting
        """
        for alias in original_node.names:
            module_name = alias.asname.name.value if alias.asname else alias.name.value
            self.imported_modules.add(module_name)
            if alias.asname and alias.name.value != alias.asname.name.value:
                self.imported_modules.add(alias.name.value)
        return True
    
    def leave_Import(self, original_node: cst.Import, updated_node: cst.Import) -> cst.Import:
        """
        Add extra unused imports to the import statement.
        
        @param original_node: Original LibCST Import node
        @param updated_node: Updated LibCST Import node
        @return: Modified Import node with extra imports
        """
        existing = {alias.name.value for alias in updated_node.names}
        extra_modules = [
            module for module in select_random_unused_libraries()
            if module not in existing
        ]
        
        if extra_modules:
            new_names = list(updated_node.names)
            for module in extra_modules:
                new_names.append(cst.ImportAlias(name=cst.Name(value=module)))
            return updated_node.with_changes(names=tuple(new_names))

        return updated_node

    def visit_ImportFrom(self, original_node: cst.ImportFrom) -> bool:
        """
        Track imported modules from 'from X import Y' statements before visiting.
        
        @param original_node: Original LibCST ImportFrom node
        @return: True to continue visiting
        """
        if original_node.module:
            self.imported_modules.add(original_node.module.value)
        return True
    
    def leave_ImportFrom(self, original_node: cst.ImportFrom, updated_node: cst.ImportFrom) -> cst.ImportFrom:
        """
        Return the import statement unchanged.
        
        @param original_node: Original LibCST ImportFrom node
        @param updated_node: Updated LibCST ImportFrom node
        @return: Original ImportFrom node
        """
        return updated_node

    def leave_If(self, original_node: cst.If, updated_node: cst.If) -> cst.If:
        """
        Insert a fake branch at the beginning of if-statements.
        
        @param original_node: Original LibCST If node
        @param updated_node: Updated LibCST If node
        @return: Original If node (fake branch insertion skipped)
        """
        return updated_node

    def leave_BinaryOperation(self, original_node: cst.BinaryOperation, updated_node: cst.BinaryOperation) -> cst.BinaryOperation:
        """
        Wrap binary operations with dummy additions.
        
        @param original_node: Original LibCST BinaryOperation node
        @param updated_node: Updated LibCST BinaryOperation node
        @return: Original BinaryOperation node (wrapping skipped)
        """
        return updated_node


def obfuscate_code_with_libcst(source_code: str) -> str:
    """
    Parse source code using LibCST, transform it, then apply string-based obfuscation.
    
    @param source_code: Python source code as a string
    @return: Obfuscated Python source code as a string
    """
    if not source_code or not source_code.strip():
        raise ValueError("Source code cannot be empty")

    try:
        tree = cst.parse_module(source_code)
    except cst.ParserSyntaxError as e:
        raise SyntaxError(f"Invalid Python syntax: {e}") from e
    except Exception as e:
        raise RuntimeError(f"Failed to parse source code: {e}") from e

    transformer = CodeObfuscatorCST()
    transformed_tree = tree.visit(transformer)
    final_code = transformed_tree.code

    final_code = insert_dummy_variable_assignments(final_code)
    final_code += "\n" + generate_random_import_statements()
    final_code = add_random_spacing_to_code(final_code)

    try:
        cst.parse_module(final_code)
    except cst.ParserSyntaxError as e:
        raise SyntaxError(f"Obfuscation introduced invalid syntax: {e}") from e

    return final_code
