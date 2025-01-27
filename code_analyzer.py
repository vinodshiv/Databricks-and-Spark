import ast
import argparse
import os
import textwrap
from tabulate import tabulate

class CodeAnalyzer(ast.NodeVisitor):
    def __init__(self):
        self.imports = set()
        self.function_calls = set()

    def visit_Import(self, node):
        for alias in node.names:
            self.imports.add(alias.name)

    def visit_ImportFrom(self, node):
        if node.module:
            self.imports.add(node.module)

    def visit_Call(self, node):
        if isinstance(node.func, ast.Name):
            self.function_calls.add(node.func.id)
        elif isinstance(node.func, ast.Attribute):
            self.function_calls.add(node.func.attr)

        self.generic_visit(node)

def wrap_text(text, width=30):
    """Wraps text for better terminal display."""
    return textwrap.fill(text, width=width) if text else "None"

def analyze_code(file_path):
    try:
        with open(file_path, "r") as f:
            tree = ast.parse(f.read())
    except Exception as e:
        print(f"Error reading/parsing {file_path}: {e}")
        return None

    analyzer = CodeAnalyzer()
    analyzer.visit(tree)

    return {
        "File": os.path.basename(file_path),
        "Imports": wrap_text(", ".join(sorted(analyzer.imports)), 30),
        "Function Calls": wrap_text(", ".join(sorted(analyzer.function_calls)), 30),
    }

def analyze_folder(folder_path):
    py_files = sorted(
        [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.endswith(".py")]
    )  # Sorts files alphabetically

    if not py_files:
        print("No Python files found in the folder.")
        return

    results = [analyze_code(file) for file in py_files]
    
    # Filter out any None results (in case of errors)
    results = [r for r in results if r]

    print("\n📌 Analysis Results (Sorted by File Name):")
    print(tabulate(results, headers="keys", tablefmt="grid"))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Analyze Python scripts in a folder for imports and function calls.")
    parser.add_argument("folder", help="Path to the folder containing Python files.")
    args = parser.parse_args()

    if os.path.isdir(args.folder):
        analyze_folder(args.folder)
    else:
        print("Invalid folder path. Please provide a valid directory.")
