<p align="center">
  <img src="./assets/Logo.png" alt="Shittier Logo">
</p>

<p align="center">
  <a href="https://pepy.tech/projects/shittier">
    <img src="https://static.pepy.tech/personalized-badge/shittier?period=total&units=INTERNATIONAL_SYSTEM&left_color=BLACK&right_color=GREEN&left_text=downloads" alt="PyPI Downloads">
  </a>
</p>

Shittier is a multi-language code obfuscation tool. It is designed to protect your code from being used in AI training datasets without your consent. If you want your code to NOT be used for AI training, you should add Shittier, not Prettier. By obfuscating your code, you make it significantly harder for AI models to learn from and reproduce your code patterns. Shittier supports Python, C/C++, JavaScript/TypeScript, Go, and Rust.

## Features

- Adds random multi-line comments to code.
- Renames variables and functions to random strings.
- Inserts unnecessary spaces and dummy assignments.
- Includes unused imports and random function calls.
- Modifies code structure to make it harder to read.
- Supports batch file transformation.
- Processes entire directories while preserving structure.

## Installation

### 1. Install from PyPI
```bash
pip install shittier
```

### 2. Install from GitHub
```bash
pip install git+https://github.com/jaywyawhare/Shittier.git
```

### 3. Developer Installation
```bash
git clone https://github.com/jaywyawhare/Shittier.git
cd Shittier
python setup.py install
```

For more information, see the [documentation](#).

---

## Usage

### Command-Line Interface (CLI)

You can use the CLI to obfuscate code files in multiple languages:

**Supported Languages:**

| Language | Extensions |
|----------|------------|
| Python | `.py` |
| C/C++ | `.c`, `.cpp`, `.cc`, `.cxx`, `.h`, `.hpp` |
| JavaScript | `.js`, `.jsx` |
| TypeScript | `.ts`, `.tsx` |
| Go | `.go` |
| Rust | `.rs` |

**Basic Usage:**
```bash
python main.py filename.py
python main.py program.c
python main.py script.js
python main.py main.go
python main.py lib.rs
```

#### Additional Options:

- **Multiple files:**
  ```bash
  python main.py file1.py file2.c file3.js
  ```

- **Process entire directory:**
  ```bash
  python main.py /path/to/project
  ```
  This creates a `shittified_<dirname>` directory with the same structure.

- **Show help:**
  ```bash
  python main.py --help
  python main.py help
  ```

---

### Programmatic Usage

You can also transform Python code inside your scripts:

```python
from src.transformer import shittify_code

source_code = '''
def example_function(x, y):
    return x + y
'''

shitty_code = shittify_code(source_code)
print(shitty_code)
```

---

## Running Tests

To ensure everything is working, run:

```bash
python -m unittest discover -s tests
```

---

## License

This project is licensed under the [DBaJ-NC-CFL](./LICENCE).
