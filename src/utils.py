import random
import string

unused_libraries = ["math", "os", "sys", "random", "time", "collections", "functools"]


def select_random_unused_libraries(count: int = 3) -> list:
    """
    Select random unused libraries from the predefined list.
    
    @param count: Number of libraries to select
    @return: List of library names
    """
    count = min(count, len(unused_libraries))
    return random.sample(unused_libraries, count)


def generate_random_variable_name() -> str:
    """
    Generate a random variable name with random length and suffix.
    
    @return: Random variable name string
    """
    variable_length = random.randint(7, 10)
    first_character = random.choice(string.ascii_lowercase)
    remaining_characters = "".join(
        random.choices(string.ascii_letters + string.digits, k=variable_length - 1)
    )
    return f"{first_character}{remaining_characters}_{random.randint(100, 999)}"


def add_random_spacing_to_code(code_snippet: str) -> str:
    """
    Add random spacing to code without breaking syntax. Currently returns unchanged.
    
    @param code_snippet: Source code string
    @return: Code with random spacing (currently unchanged)
    """
    return code_snippet


def generate_random_import_statements() -> str:
    """
    Generate random import statements with example usage calls.
    
    @return: String containing import statements and example calls
    """
    import_statements = []
    import_examples = {
        "math": ["math.sqrt(25)"],
        "os": ["os.path.exists('/some/path')"],
        "time": ["time.sleep(1)"],
        "sys": ["sys.version"],
        "random": ["random.randint(1, 10)"],
        "collections": ["collections.Counter([1, 2, 3])"],
        "functools": ["functools.reduce(lambda x, y: x + y, [1, 2, 3])"],
    }
    for library in unused_libraries:
        if library in import_examples:
            import_statements.append(f"import {library}")
            import_statements.extend(import_examples[library])
    return "\n".join(import_statements)


def insert_dummy_variable_assignments(code_snippet: str) -> str:
    """
    Insert dummy variable assignments after actual assignments, avoiding comparisons.
    
    @param code_snippet: Source code string
    @return: Code with dummy assignments inserted
    """
    dummy_variables = ["dummy_var = 0", "temp = 12345", "unused_var = None"]
    modified_lines = []
    for line in code_snippet.splitlines():
        modified_lines.append(line)
        stripped = line.strip()
        if stripped and "=" in stripped:
            if "==" not in stripped and "!=" not in stripped and "<=" not in stripped and ">=" not in stripped:
                if not stripped.startswith(("def ", "class ", "@", "import ", "from ", "if ", "elif ", "while ", "for ")):
                    parts = stripped.split("=", 1)
                    if len(parts) == 2 and parts[0].strip() and not parts[0].strip().startswith("#"):
                        indent = len(line) - len(line.lstrip())
                        dummy_line = " " * indent + random.choice(dummy_variables)
                        modified_lines.append(dummy_line)
    return "\n".join(modified_lines)
