import re
import random
from src.utils import generate_random_variable_name


def shittify_c_cpp(code: str) -> str:
    """
    Obfuscate C/C++ code by renaming identifiers, adding dummy code, and inserting includes.
    
    @param code: C/C++ source code as a string
    @return: Obfuscated C/C++ source code as a string
    """
    lines = code.splitlines()
    identifier_map = {}
    included_headers = set()
    std_namespace_used = False
    
    builtin_keywords = {
        'int', 'char', 'float', 'double', 'void', 'return', 'if', 'else', 'for', 'while',
        'do', 'switch', 'case', 'break', 'continue', 'default', 'sizeof', 'typedef',
        'struct', 'union', 'enum', 'const', 'static', 'extern', 'volatile', 'register',
        'auto', 'signed', 'unsigned', 'short', 'long', 'include', 'define', 'ifdef',
        'ifndef', 'endif', 'pragma', 'main', 'printf', 'scanf', 'malloc', 'free',
        'NULL', 'true', 'false', 'bool'
    }
    
    for line in lines:
        stripped = line.strip()
        if stripped.startswith('#include'):
            include_match = re.search(r'#include\s*[<"]([^>"]+)[>"]', stripped)
            if include_match:
                header = include_match.group(1)
                included_headers.add(header)
                if not header.startswith('.'):
                    std_namespace_used = True
        elif 'std::' in line or 'using namespace std' in line:
            std_namespace_used = True
    
    def get_random_name(original: str) -> str:
        """
        Get or create a random name for an identifier, preserving keywords and std namespace.
        
        @param original: Original identifier name
        @return: Random name or original if preserved
        """
        if (original in builtin_keywords or 
            original.startswith('__') or 
            original.startswith('std::') or
            original == 'std' or
            (std_namespace_used and original in ['cout', 'cin', 'endl', 'string', 'vector', 'map', 'set'])):
            return original
        if original not in identifier_map:
            identifier_map[original] = generate_random_variable_name()
        return identifier_map[original]
    
    identifier_pattern = r'\b[a-zA-Z_][a-zA-Z0-9_]*\b'
    
    result_lines = []
    
    for line in lines:
        original_line = line
        stripped = line.strip()
        
        if stripped.startswith('#') or stripped.startswith('//') or stripped.startswith('/*'):
            result_lines.append(line)
            continue
        
        string_pattern = r'"[^"]*"|\'[^\']*\''
        strings = {}
        string_counter = 0
        for match in re.finditer(string_pattern, line):
            placeholder = f"__STRING_{string_counter}__"
            strings[placeholder] = match.group(0)
            line = line[:match.start()] + placeholder + line[match.end():]
            string_counter += 1
        
        words = re.findall(identifier_pattern, line)
        for word in words:
            if word not in builtin_keywords and not word.startswith('__') and word not in strings.values():
                new_name = get_random_name(word)
                line = re.sub(r'\b' + re.escape(word) + r'\b', new_name, line)
        
        for placeholder, string_literal in strings.items():
            line = line.replace(placeholder, string_literal)
        
        result_lines.append(line)
        
        if '=' in line and '==' not in line and '!=' not in line and '<=' not in line and '>=' not in line:
            if not stripped.startswith(('//', '/*', '#')):
                indent = len(original_line) - len(original_line.lstrip())
                dummy_vars = [
                    f"{' ' * indent}int {generate_random_variable_name()} = 0;",
                    f"{' ' * indent}int {generate_random_variable_name()} = 42;",
                    f"{' ' * indent}void* {generate_random_variable_name()} = NULL;"
                ]
                result_lines.append(random.choice(dummy_vars))
    
    random_includes = [
        "#include <cstdio>",
        "#include <cstdlib>",
        "#include <cstring>",
        "#include <cmath>",
        "#include <ctime>",
        "#include <iostream>",
        "#include <vector>",
        "#include <map>",
        "#include <algorithm>"
    ]
    
    insert_pos = 0
    for i, line in enumerate(result_lines):
        if line.strip().startswith('#include'):
            insert_pos = i + 1
        elif line.strip() and not line.strip().startswith('//') and not line.strip().startswith('/*'):
            break
    
    for _ in range(random.randint(2, 3)):
        include = random.choice(random_includes)
        if include not in result_lines[:insert_pos]:
            result_lines.insert(insert_pos, include)
            insert_pos += 1
    
    final_lines = []
    for line in result_lines:
        final_lines.append(line)
        if random.random() < 0.15 and line.strip() and not line.strip().startswith('//'):
            indent = len(line) - len(line.lstrip())
            comments = [
                f"{' ' * indent}// {generate_random_variable_name()}",
                f"{' ' * indent}// TODO: {generate_random_variable_name()}",
                f"{' ' * indent}/* {generate_random_variable_name()} */"
            ]
            final_lines.append(random.choice(comments))
    
    return '\n'.join(final_lines)


def shittify_javascript_typescript(code: str) -> str:
    """
    Obfuscate JavaScript/TypeScript code by renaming identifiers and adding dummy code.
    
    @param code: JavaScript/TypeScript source code as a string
    @return: Obfuscated JavaScript/TypeScript source code as a string
    """
    lines = code.splitlines()
    identifier_map = {}
    imported_modules = set()
    
    builtin_keywords = {
        'let', 'const', 'var', 'function', 'class', 'return', 'if', 'else', 'for', 'while',
        'do', 'switch', 'case', 'break', 'continue', 'default', 'try', 'catch', 'finally',
        'throw', 'new', 'this', 'super', 'extends', 'implements', 'import', 'export', 'from',
        'async', 'await', 'undefined', 'null', 'true', 'false', 'typeof', 'instanceof', 'in', 'of', 'as',
        'interface', 'type', 'enum', 'namespace', 'module', 'declare', 'public', 'private',
        'protected', 'static', 'readonly', 'abstract', 'get', 'set', 'constructor',
        'string', 'number', 'boolean', 'any', 'void', 'never', 'unknown', 'object', 'symbol', 'bigint'
    }
    
    builtin_methods = {
        'log', 'error', 'warn', 'info', 'debug', 'trace', 'dir', 'table', 'assert',
        'clear', 'count', 'countReset', 'group', 'groupEnd', 'groupCollapsed', 'time', 'timeEnd',
        'timeLog', 'profile', 'profileEnd', 'timeStamp', 'memory'
    }
    
    for line in lines:
        stripped = line.strip()
        if stripped.startswith('import'):
            import_match = re.search(r'import\s+(?:\*\s+as\s+)?(\w+)|import\s*\{([^}]+)\}|const\s+(\w+)\s*=\s*require', stripped)
            if import_match:
                if import_match.group(1):
                    imported_modules.add(import_match.group(1))
                elif import_match.group(2):
                    for name in import_match.group(2).split(','):
                        imported_modules.add(name.strip().split(' as ')[0].strip())
                elif import_match.group(3):
                    imported_modules.add(import_match.group(3))
    
    def get_random_name(original: str) -> str:
        """
        Get or create a random name for an identifier, preserving keywords and imports.
        
        @param original: Original identifier name
        @return: Random name or original if preserved
        """
        if original in builtin_keywords or original.startswith('__') or original in imported_modules:
            return original
        if original not in identifier_map:
            identifier_map[original] = generate_random_variable_name()
        return identifier_map[original]
    
    identifier_pattern = r'\b[a-zA-Z_$][a-zA-Z0-9_$]*\b'
    
    result_lines = []
    
    for line in lines:
        original_line = line
        stripped = line.strip()
        
        if stripped.startswith('//') or stripped.startswith('/*') or stripped.startswith('*'):
            result_lines.append(line)
            continue
        
        template_string_pattern = r'`([^`]*)`'
        template_strings = {}
        template_counter = [0]
        
        def process_template_string(match) -> str:
            """
            Process template string and rename variables inside expressions.
            
            @param match: Regex match object for template string
            @return: Placeholder string
            """
            template_content = match.group(0)
            expr_pattern = r'\$\{([^}]+)\}'
            processed_template = template_content
            for expr_match in re.finditer(expr_pattern, template_content):
                expr = expr_match.group(1)
                expr_words = re.findall(identifier_pattern, expr)
                for word in expr_words:
                    if (word not in builtin_keywords and 
                        not word.startswith('__') and 
                        word != '$' and
                        word not in builtin_methods):
                        new_name = get_random_name(word)
                        expr = re.sub(r'\b' + re.escape(word) + r'\b', new_name, expr)
                processed_template = processed_template.replace(expr_match.group(0), f"${{{expr}}}")
            placeholder = f"__TEMPLATE_{template_counter[0]}__"
            template_strings[placeholder] = processed_template
            template_counter[0] += 1
            return placeholder
        
        line = re.sub(template_string_pattern, process_template_string, line)
        
        string_pattern = r'"[^"]*"|\'[^\']*\''
        strings = {}
        string_counter = 0
        for match in re.finditer(string_pattern, line):
            placeholder = f"__STRING_{string_counter}__"
            strings[placeholder] = match.group(0)
            line = line[:match.start()] + placeholder + line[match.end():]
            string_counter += 1
        
        method_call_pattern = r'([a-zA-Z_$][a-zA-Z0-9_$]*)\s*\.\s*([a-zA-Z_$][a-zA-Z0-9_$]*)'
        protected_attributes = set()
        protected_modules = set()
        protected_globals = set()
        for match in re.finditer(method_call_pattern, line):
            module_name = match.group(1)
            method_name = match.group(2)
            if module_name in imported_modules:
                protected_attributes.add(method_name)
                protected_modules.add(module_name)
            elif method_name in builtin_methods:
                protected_attributes.add(method_name)
                protected_globals.add(module_name)
            elif module_name in ['console', 'document', 'window', 'navigator', 'location']:
                protected_attributes.add(method_name)
                protected_globals.add(module_name)
        
        words = re.findall(identifier_pattern, line)
        for word in words:
            if (word not in builtin_keywords and 
                not word.startswith('__') and 
                word != '$' and 
                word not in strings.values() and
                word not in protected_attributes and
                word not in protected_modules and
                word not in protected_globals and
                not word.startswith('__TEMPLATE_') and
                not word.startswith('__STRING_')):
                new_name = get_random_name(word)
                line = re.sub(r'\b' + re.escape(word) + r'\b', new_name, line)
        
        for placeholder, template_string in template_strings.items():
            line = line.replace(placeholder, template_string)
        
        for placeholder, string_literal in strings.items():
            line = line.replace(placeholder, string_literal)
        
        result_lines.append(line)
        
        if '=' in line and '==' not in line and '!=' not in line and '<=' not in line and '>=' not in line:
            if not stripped.startswith(('//', '/*', '*', 'import', 'export')):
                indent = len(original_line) - len(original_line.lstrip())
                dummy_vars = [
                    f"{' ' * indent}const {generate_random_variable_name()} = 0;",
                    f"{' ' * indent}let {generate_random_variable_name()} = null;",
                    f"{' ' * indent}var {generate_random_variable_name()} = undefined;",
                    f"{' ' * indent}let {generate_random_variable_name()} = {{}};"
                ]
                result_lines.append(random.choice(dummy_vars))
    
    if not any('import' in line or 'export' in line for line in result_lines[:10]):
        random_imports = [
            "import * as _ from 'lodash';",
            "import { random } from 'math';",
            "const _ = require('underscore');"
        ]
        result_lines.insert(0, random.choice(random_imports))
    
    final_lines = []
    for line in result_lines:
        final_lines.append(line)
        if random.random() < 0.15 and line.strip() and not line.strip().startswith('//'):
            indent = len(line) - len(line.lstrip())
            comments = [
                f"{' ' * indent}// {generate_random_variable_name()}",
                f"{' ' * indent}// TODO: {generate_random_variable_name()}",
                f"{' ' * indent}/* {generate_random_variable_name()} */"
            ]
            final_lines.append(random.choice(comments))
    
    return '\n'.join(final_lines)


def shittify_go(code: str) -> str:
    """
    Obfuscate Go code by renaming identifiers and adding dummy code.
    
    @param code: Go source code as a string
    @return: Obfuscated Go source code as a string
    """
    lines = code.splitlines()
    identifier_map = {}
    imported_packages = set()
    
    builtin_keywords = {
        'package', 'import', 'func', 'var', 'const', 'type', 'struct', 'interface',
        'if', 'else', 'for', 'range', 'switch', 'case', 'default', 'break', 'continue',
        'return', 'go', 'defer', 'select', 'chan', 'map', 'make', 'new', 'len', 'cap',
        'append', 'copy', 'delete', 'close', 'panic', 'recover', 'true', 'false', 'nil',
        'int', 'int8', 'int16', 'int32', 'int64', 'uint', 'uint8', 'uint16', 'uint32',
        'uint64', 'float32', 'float64', 'string', 'bool', 'byte', 'rune', 'error', 'main'
    }
    
    for line in lines:
        stripped = line.strip()
        if stripped.startswith('import'):
            import_match = re.search(r'import\s+(?:\.\s+)?(?:"([^"]+)"|(\w+)\s+"[^"]+"|(\w+))', stripped)
            if import_match:
                if import_match.group(1):
                    pkg_path = import_match.group(1)
                    pkg_name = pkg_path.split('/')[-1]
                    imported_packages.add(pkg_name)
                elif import_match.group(2):
                    imported_packages.add(import_match.group(2))
                elif import_match.group(3):
                    imported_packages.add(import_match.group(3))
    
    def get_random_name(original: str) -> str:
        """
        Get or create a random name for an identifier, preserving keywords and packages.
        
        @param original: Original identifier name
        @return: Random name or original if preserved
        """
        if original in builtin_keywords or original.startswith('__') or original in imported_packages:
            return original
        if original not in identifier_map:
            identifier_map[original] = generate_random_variable_name()
        return identifier_map[original]
    
    identifier_pattern = r'\b[a-zA-Z_][a-zA-Z0-9_]*\b'
    
    result_lines = []
    
    for line in lines:
        original_line = line
        stripped = line.strip()
        
        if stripped.startswith('//') or stripped.startswith('/*'):
            result_lines.append(line)
            continue
        
        string_pattern = r'`[^`]*`|"[^"]*"|\'[^\']*\''
        strings = {}
        string_counter = 0
        for match in re.finditer(string_pattern, line):
            placeholder = f"__STRING_{string_counter}__"
            strings[placeholder] = match.group(0)
            line = line[:match.start()] + placeholder + line[match.end():]
            string_counter += 1
        
        method_call_pattern = r'([a-zA-Z_][a-zA-Z0-9_]*)\s*\.\s*([A-Z][a-zA-Z0-9_]*)'
        protected_methods = set()
        protected_packages = set()
        for match in re.finditer(method_call_pattern, line):
            pkg_name = match.group(1)
            method_name = match.group(2)
            if pkg_name in imported_packages:
                protected_methods.add(method_name)
                protected_packages.add(pkg_name)
        
        words = re.findall(identifier_pattern, line)
        for word in words:
            if (word not in builtin_keywords and 
                not word.startswith('__') and 
                word not in strings.values() and
                word not in protected_methods and
                word not in protected_packages):
                new_name = get_random_name(word)
                line = re.sub(r'\b' + re.escape(word) + r'\b', new_name, line)
        
        for placeholder, string_literal in strings.items():
            line = line.replace(placeholder, string_literal)
        
        result_lines.append(line)
        
        if ':=' in line or ('=' in line and '==' not in line and '!=' not in line):
            if not stripped.startswith(('//', '/*', 'package', 'import')):
                indent = len(original_line) - len(original_line.lstrip())
                dummy_vars = [
                    f"{' ' * indent}var {generate_random_variable_name()} = 0",
                    f"{' ' * indent}var {generate_random_variable_name()} = nil",
                    f"{' ' * indent}{generate_random_variable_name()} := 42"
                ]
                result_lines.append(random.choice(dummy_vars))
    
    insert_pos = 0
    for i, line in enumerate(result_lines):
        if line.strip().startswith('import'):
            insert_pos = i + 1
        elif line.strip() and not line.strip().startswith('//') and not line.strip().startswith('package'):
            break
    
    random_imports = [
        'import "fmt"',
        'import "os"',
        'import "time"',
        'import "math"',
        'import "strings"',
        'import "strconv"'
    ]
    
    for _ in range(random.randint(1, 2)):
        imp = random.choice(random_imports)
        if imp not in result_lines[:insert_pos]:
            result_lines.insert(insert_pos, imp)
            insert_pos += 1
    
    final_lines = []
    for line in result_lines:
        final_lines.append(line)
        if random.random() < 0.15 and line.strip() and not line.strip().startswith('//'):
            indent = len(line) - len(line.lstrip())
            comments = [
                f"{' ' * indent}// {generate_random_variable_name()}",
                f"{' ' * indent}// TODO: {generate_random_variable_name()}"
            ]
            final_lines.append(random.choice(comments))
    
    return '\n'.join(final_lines)


def handle_rust() -> str:
    """
    Return a message indicating Rust is already shittified beyond repair.
    
    @return: Message string about Rust
    """
    return """// Rust is already shittified beyond repair.
// The borrow checker has done its job.
// There's nothing more we can do here.
// 
// If you're reading this, you've already lost.
// 
// fn main() {
//     println!("Rust is already perfect chaos.");
// }
"""
