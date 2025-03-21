#!/usr/bin/env python3
import argparse
import os
import sys
from src.transformer import shittify_code

def process_file(filepath):
    if not filepath.endswith(".py"):
        print(f"Skipping non-Python file: {filepath}")
        return

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            original_code = f.read()
        obfuscated_code = shittify_code(original_code)
        output_path = filepath.replace(".py", ".shittier.py")
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(obfuscated_code)
        print(f"Processed: {filepath} -> {output_path}")
    except Exception as e:
        print(f"Error processing {filepath}: {e}")

def process_path(path, recursive=False):
    if os.path.isfile(path):
        process_file(path)
    elif os.path.isdir(path):
        for entry in os.listdir(path):
            full_path = os.path.join(path, entry)
            if os.path.isfile(full_path) and full_path.endswith(".py"):
                process_file(full_path)
            elif recursive and os.path.isdir(full_path):
                process_path(full_path, recursive=True)
    else:
        print(f"Path does not exist: {path}")

def main():
    parser = argparse.ArgumentParser(
        description="Obfuscate Python files using the shittier."
    )
    parser.add_argument(
        "paths",
        nargs="+",
        help="Python file(s) or directory to process (only .py files will be operated on).",
    )
    parser.add_argument(
        "-r", "--recursive", action="store_true", help="Recursively process directories."
    )
    args = parser.parse_args()

    for path in args.paths:
        process_path(path, recursive=args.recursive)

if __name__ == "__main__":
    main()
