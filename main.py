#!/usr/bin/env python3
import argparse
import os
from src.transformer import obfuscate_code_with_ast
from src.language_transformers import (
    shittify_c_cpp,
    shittify_javascript_typescript,
    shittify_go,
    handle_rust,
)


SUPPORTED_EXTENSIONS = {
    '.py': 'python',
    '.c': 'c',
    '.cpp': 'cpp',
    '.cc': 'cpp',
    '.cxx': 'cpp',
    '.h': 'c',
    '.hpp': 'cpp',
    '.js': 'javascript',
    '.jsx': 'javascript',
    '.ts': 'typescript',
    '.tsx': 'typescript',
    '.go': 'go',
    '.rs': 'rust',
}


def get_file_language(file_path: str) -> str:
    """
    Determine the programming language based on file extension.
    
    @param file_path: Path to the file
    @return: Language name or None if unsupported
    """
    _, ext = os.path.splitext(file_path)
    ext_lower = ext.lower()
    return SUPPORTED_EXTENSIONS.get(ext_lower)


def process_single_file(file_path: str) -> None:
    """
    Read a file, obfuscate it based on language, and write output to a new file.
    
    @param file_path: Path to the input file
    @return: None
    """
    if not os.path.exists(file_path):
        print(f"Error: File not found: {file_path}")
        return
    
    if not os.path.isfile(file_path):
        print(f"Error: Path is not a file: {file_path}")
        return
    
    language = get_file_language(file_path)
    
    if not language:
        print(f"Skipping unsupported file type: {file_path}")
        return
    
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            source_code = f.read()
        
        if not source_code.strip():
            print(f"Warning: File is empty: {file_path}")
            return
        
        if language == 'rust':
            rust_message = handle_rust()
            print(f"\n🦀 Rust file detected: {file_path}")
            print(rust_message)
            print(f"Rust is already shittified beyond repair. No output file created.\n")
            return
        
        if language == 'python':
            obfuscated_code = obfuscate_code_with_ast(source_code)
            output_file_path = file_path.replace(".py", ".shittified.py")
        elif language in ('c', 'cpp'):
            obfuscated_code = shittify_c_cpp(source_code)
            ext = os.path.splitext(file_path)[1]
            output_file_path = file_path.replace(ext, f".shittified{ext}")
        elif language in ('javascript', 'typescript'):
            obfuscated_code = shittify_javascript_typescript(source_code)
            ext = os.path.splitext(file_path)[1]
            output_file_path = file_path.replace(ext, f".shittified{ext}")
        elif language == 'go':
            obfuscated_code = shittify_go(source_code)
            output_file_path = file_path.replace(".go", ".shittified.go")
        else:
            print(f"Unsupported language: {language}")
            return
        
        with open(output_file_path, "w", encoding="utf-8") as f:
            f.write(obfuscated_code)
        print(f"Processed: {file_path} -> {output_file_path}")
    except FileNotFoundError:
        print(f"Error: File not found: {file_path}")
    except PermissionError:
        print(f"Error: Permission denied: {file_path}")
    except UnicodeDecodeError as e:
        print(f"Error: Unable to decode file {file_path}: {e}")
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        import traceback
        traceback.print_exc()


def handle_directory_or_file(path_to_handle: str, recursive_mode: bool = False) -> None:
    """
    Process a given path (file or directory) and obfuscate supported files.
    
    @param path_to_handle: Path to file or directory
    @param recursive_mode: If True, recursively process subdirectories
    @return: None
    """
    if os.path.isfile(path_to_handle):
        process_single_file(path_to_handle)
    elif os.path.isdir(path_to_handle):
        for entry in os.listdir(path_to_handle):
            full_entry_path = os.path.join(path_to_handle, entry)
            if os.path.islink(full_entry_path):
                print(f"Skipping symbolic link: {full_entry_path}")
                continue
            if os.path.isfile(full_entry_path):
                if get_file_language(full_entry_path):
                    process_single_file(full_entry_path)
            elif recursive_mode and os.path.isdir(full_entry_path):
                handle_directory_or_file(full_entry_path, recursive_mode=True)
    else:
        print(f"Path not found: {path_to_handle}")


def main_program_entry() -> None:
    """
    Main entry point for the CLI. Parses arguments and processes input files.
    
    @return: None
    """
    parser = argparse.ArgumentParser(
        description="Obfuscate code files (Python, C/C++, JavaScript/TypeScript, Go). Rust is already shittified beyond repair."
    )
    parser.add_argument(
        "input_paths",
        nargs="+",
        help="File(s) or directory to process. Supported: .py, .c, .cpp, .h, .js, .ts, .go, .rs",
    )
    parser.add_argument(
        "-r",
        "--recursive",
        action="store_true",
        help="Recursively process directories.",
    )
    args = parser.parse_args()

    for input_path in args.input_paths:
        handle_directory_or_file(input_path, recursive_mode=args.recursive)


if __name__ == "__main__":
    main_program_entry()
