import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import openai
import ast
import json
import shutil
import os
import re


class BackendCodeGeneratorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("AI-Powered Backend Code Generator")
        self.root.geometry("900x600")
        self.root.configure(bg="#2C2F33")

        self.selected_files = []
        self.backup_dir = "backup_files"
        os.makedirs(self.backup_dir, exist_ok=True)

        # File Selection
        self.file_label = tk.Label(root, text="Selected Files:", fg="white", bg="#2C2F33", font=("Arial", 12, "bold"))
        self.file_label.pack()
        self.file_listbox = tk.Listbox(root, width=100, height=5, bg="#23272A", fg="white")
        self.file_listbox.pack()
        self.browse_button = tk.Button(root, text="Browse Files", command=self.select_files, bg="#7289DA", fg="white")
        self.browse_button.pack(pady=5)

        # AI Suggestions
        self.analysis_label = tk.Label(root, text="AI Suggestions / Code Generation:", fg="white", bg="#2C2F33",
                                       font=("Arial", 12, "bold"))
        self.analysis_label.pack()
        self.analysis_text = scrolledtext.ScrolledText(root, height=10, width=100, bg="#23272A", fg="white")
        self.analysis_text.pack()

        # User Input for Code Generation
        self.user_input_label = tk.Label(root, text="Enter backend logic you want to generate:", fg="white",
                                         bg="#2C2F33", font=("Arial", 12, "bold"))
        self.user_input_label.pack()
        self.user_input = tk.Entry(root, width=100, bg="#23272A", fg="white")
        self.user_input.pack()

        # Buttons
        self.analyze_button = tk.Button(root, text="Analyze & Generate", command=self.analyze_code, bg="#43B581",
                                        fg="white")
        self.analyze_button.pack(pady=5)

        self.modify_button = tk.Button(root, text="Apply Modifications", command=self.apply_modifications, bg="#FAA61A",
                                       fg="white")
        self.modify_button.pack(pady=5)

        self.rollback_button = tk.Button(root, text="Rollback Changes", command=self.rollback_changes, bg="#F04747",
                                         fg="white")
        self.rollback_button.pack(pady=5)

    def select_files(self):
        self.selected_files = filedialog.askopenfilenames(title="Select Backend Files",
                                                          filetypes=[("Python Files", "*.py")])
        self.file_listbox.delete(0, tk.END)
        for file in self.selected_files:
            self.file_listbox.insert(tk.END, file)

    def analyze_code(self):
        if not self.selected_files:
            messagebox.showerror("Error", "No files selected!")
            return

        extracted_data = []
        for file in self.selected_files:
            self.create_backup(file)
            result = self.extract_backend_logic(file)
            extracted_data.append(result)

        user_request = self.user_input.get().strip()
        ai_response = self.get_ai_suggestions(extracted_data, user_request)

        self.analysis_text.delete("1.0", tk.END)
        self.analysis_text.insert(tk.END, ai_response)

    def extract_backend_logic(self, file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                code = file.read()
            tree = ast.parse(code)
            functions = [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
            return {"file": file_path, "functions": functions}
        except Exception as e:
            return {"error": str(e)}

    def get_ai_suggestions(self, extracted_data, user_request):
        prompt = f"Analyze and improve the backend logic: {json.dumps(extracted_data, indent=2)}"
        if user_request:
            prompt += f"\nGenerate code for: {user_request}"
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4-turbo",
                messages=[{"role": "user", "content": prompt}],
                api_key="sk-proj-W14HY7xp3zAwzWEIh7fiT3BlbkFJq6shGu3r7makPD87FIp2"
            )
            return response["choices"][0]["message"]["content"]
        except Exception as e:
            return f"Error: {e}"

    def apply_modifications(self):
        if not self.selected_files:
            messagebox.showerror("Error", "No files selected!")
            return

        for file in self.selected_files:
            self.create_backup(file)
            self.modify_code(file)

        messagebox.showinfo("Success", "Code modifications applied successfully!")

    def modify_code(self, file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                original_code = file.read()

            ai_suggestions = self.analysis_text.get("1.0", tk.END)
            extracted_code = self.extract_code_blocks(ai_suggestions)

            modified_code = original_code + '\n' + '\n'.join(extracted_code)

            with open(file_path, "w", encoding="utf-8") as file:
                file.write(modified_code)
        except Exception as e:
            messagebox.showerror("Error", f"Modification failed: {e}")

    def extract_code_blocks(self, text):
        code_blocks = re.findall(r'```python\n(.*?)\n```', text, re.DOTALL)
        return code_blocks if code_blocks else [text]

    def rollback_changes(self):
        if not self.selected_files:
            messagebox.showerror("Error", "No files selected!")
            return
        for file in self.selected_files:
            backup_path = os.path.join(self.backup_dir, os.path.basename(file))
            if os.path.exists(backup_path):
                shutil.copy(backup_path, file)
                messagebox.showinfo("Rollback Success", f"Restored original file: {file}")
            else:
                messagebox.showerror("Error", f"No backup found for: {file}")

    def create_backup(self, file_path):
        backup_path = os.path.join(self.backup_dir, os.path.basename(file_path))
        shutil.copy(file_path, backup_path)


if __name__ == "__main__":
    root = tk.Tk()
    app = BackendCodeGeneratorGUI(root)
    root.mainloop()
