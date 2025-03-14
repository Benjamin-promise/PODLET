import tkinter as tk
from tkinter import filedialog
import ast


def select_files():
    """Opens a file dialog for selecting backend files."""
    root = tk.Tk()
    root.withdraw()  # Hide the root window
    file_paths = filedialog.askopenfilenames(title="Select Backend Files",
                                             filetypes=[("Python Files", "*.py"), ("All Files", "*.*")])
    return file_paths


def analyze_python_code(file_path):
    """Parses a Python file and extracts functions, classes, API routes, and database interactions."""
    with open(file_path, "r", encoding="utf-8") as file:
        code = file.read()

    tree = ast.parse(code)

    extracted_data = {
        "file": file_path,
        "functions": [],
        "classes": [],
        "api_routes": [],
        "database_queries": [],
        "orm_usage": []
    }

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            extracted_data["functions"].append(node.name)

        elif isinstance(node, ast.ClassDef):
            extracted_data["classes"].append(node.name)

        elif isinstance(node, ast.Expr) and isinstance(node.value, ast.Call):
            if isinstance(node.value.func, ast.Attribute) and hasattr(node.value.func, "attr"):
                if node.value.func.attr in ["get", "post", "put", "delete"]:
                    extracted_data["api_routes"].append(ast.unparse(node.value.args[0]))

        elif isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            # Detect raw SQL queries (cursor.execute)
            if node.func.attr == "execute" and isinstance(node.func.value, ast.Name):
                extracted_data["database_queries"].append(ast.unparse(node.args[0]))

            # Detect ORM queries (e.g., SQLAlchemy, Django ORM)
            elif node.func.attr in ["filter", "all", "first", "update", "delete", "commit"]:
                extracted_data["orm_usage"].append(ast.unparse(node))

    return extracted_data


def main():
    selected_files = select_files()
    if not selected_files:
        print("No files selected.")
        return

    analyzed_data = []
    for file in selected_files:
        result = analyze_python_code(file)
        analyzed_data.append(result)

    # Display the results
    print("\nExtracted Backend Structure:")
    for data in analyzed_data:
        print(f"\nFile: {data['file']}")
        for key, value in data.items():
            if key != "file":
                print(f"{key}: {value}")


if __name__ == "__main__":
    main()
