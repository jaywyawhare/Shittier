#!/usr/bin/env python3
import argparse
import os
import shutil
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


def process_single_file(file_path: str, output_file_path: str = None) -> None:
    """
    Read a file, obfuscate it based on language, and write output to a new file.
    
    @param file_path: Path to the input file
    @param output_file_path: Optional output file path. If None, creates .shittified.* next to original
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
            if output_file_path is None:
                output_file_path = file_path.replace(".py", ".shittified.py")
        elif language in ('c', 'cpp'):
            obfuscated_code = shittify_c_cpp(source_code)
            if output_file_path is None:
                ext = os.path.splitext(file_path)[1]
                output_file_path = file_path.replace(ext, f".shittified{ext}")
        elif language in ('javascript', 'typescript'):
            obfuscated_code = shittify_javascript_typescript(source_code)
            if output_file_path is None:
                ext = os.path.splitext(file_path)[1]
                output_file_path = file_path.replace(ext, f".shittified{ext}")
        elif language == 'go':
            obfuscated_code = shittify_go(source_code)
            if output_file_path is None:
                output_file_path = file_path.replace(".go", ".shittified.go")
        else:
            print(f"Unsupported language: {language}")
            return
        
        output_dir = os.path.dirname(output_file_path)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
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


def process_directory(input_dir: str) -> None:
    """
    Process an entire directory and create shittified_<dirname> with same structure.
    
    @param input_dir: Path to the input directory
    @return: None
    """
    if not os.path.isdir(input_dir):
        print(f"Error: Path is not a directory: {input_dir}")
        return
    
    input_dir = os.path.abspath(input_dir)
    dir_name = os.path.basename(input_dir.rstrip(os.sep))
    parent_dir = os.path.dirname(input_dir)
    output_dir = os.path.join(parent_dir, f"shittified_{dir_name}")
    
    print(f"Processing directory: {input_dir}")
    print(f"Output directory: {output_dir}")
    
    def process_directory_recursive(src_dir: str, dst_dir: str) -> None:
        """
        Recursively process directory structure and obfuscate files.
        
        @param src_dir: Source directory path
        @param dst_dir: Destination directory path
        @return: None
        """
        os.makedirs(dst_dir, exist_ok=True)
        
        for entry in os.listdir(src_dir):
            src_path = os.path.join(src_dir, entry)
            dst_path = os.path.join(dst_dir, entry)
            
            if os.path.islink(src_path):
                print(f"Skipping symbolic link: {src_path}")
                continue
            
            if os.path.isfile(src_path):
                language = get_file_language(src_path)
                if language:
                    if language == 'rust':
                        rust_message = handle_rust()
                        print(f"\n🦀 Rust file detected: {src_path}")
                        print(rust_message)
                        print(f"Rust is already shittified beyond repair. Skipping.\n")
                        continue
                    
                    _, ext = os.path.splitext(entry)
                    if language == 'python':
                        dst_path = dst_path.replace(".py", ".shittified.py")
                    elif language in ('c', 'cpp'):
                        dst_path = dst_path.replace(ext, f".shittified{ext}")
                    elif language in ('javascript', 'typescript'):
                        dst_path = dst_path.replace(ext, f".shittified{ext}")
                    elif language == 'go':
                        dst_path = dst_path.replace(".go", ".shittified.go")
                    
                    process_single_file(src_path, dst_path)
                else:
                    shutil.copy2(src_path, dst_path)
            elif os.path.isdir(src_path):
                process_directory_recursive(src_path, dst_path)
    
    try:
        process_directory_recursive(input_dir, output_dir)
        print(f"\n✓ Directory processing complete: {output_dir}")
    except Exception as e:
        print(f"Error processing directory {input_dir}: {e}")
        import traceback
        traceback.print_exc()


def handle_directory_or_file(path_to_handle: str, recursive_mode: bool = False) -> None:
    """
    Process a given path (file or directory) and obfuscate supported files.
    
    @param path_to_handle: Path to file or directory
    @param recursive_mode: If True, recursively process subdirectories (for single file mode)
    @return: None
    """
    if os.path.isfile(path_to_handle):
        process_single_file(path_to_handle)
    elif os.path.isdir(path_to_handle):
        process_directory(path_to_handle)
    else:
        print(f"Path not found: {path_to_handle}")


def main_program_entry() -> None:
    """
    Main entry point for the CLI. Parses arguments and processes input files.
    
    @return: None
    """
    parser = argparse.ArgumentParser(
        description="Obfuscate code files (Python, C/C++, JavaScript/TypeScript, Go, Rust).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py file.py                    Process a single file
  python main.py /path/to/project           Process entire directory
  python main.py file1.py file2.js          Process multiple files
  python main.py --help                     Show this help message

Supported file types:
  Python:     .py
  C/C++:      .c, .cpp, .cc, .cxx, .h, .hpp
  JavaScript: .js, .jsx
  TypeScript: .ts, .tsx
  Go:         .go
  Rust:       .rs (shows message, no output file)
        """
    )
    parser.add_argument(
        "input_paths",
        nargs="*",
        help="File(s) or directory to process. Supported: .py, .c, .cpp, .h, .js, .ts, .go, .rs",
    )
    parser.add_argument(
        "-r",
        "--recursive",
        action="store_true",
        help="Recursively process directories (deprecated: directories are always processed recursively).",
    )
    
    try:
        args = parser.parse_args()
    except SystemExit:
        return

    if not args.input_paths:
        parser.print_help()
        return

    for input_path in args.input_paths:
        if input_path.lower() in ('help', '--help', '-h'):
            parser.print_help()
            return
        if not os.path.exists(input_path):
            print(f"Error: Path not found: {input_path}\n")
            parser.print_help()
            return
        handle_directory_or_file(input_path, recursive_mode=args.recursive)


if __name__ == "__main__":
    main_program_entry()
