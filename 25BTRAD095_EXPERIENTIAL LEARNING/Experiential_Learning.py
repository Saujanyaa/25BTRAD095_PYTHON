import json
import os
import tkinter as tk
from tkinter import messagebox, ttk

class SalaryApp:
    def __init__(self, root, filename="salary_data.json"):
        self.root = root
        self.root.title("Salary Management System")
        self.root.geometry("850x520")
        self.root.minsize(750, 480)
        
        self.filename = filename
        self.data = self.load_data()

        # Styling
        self.style = ttk.Style()
        self.style.theme_use("clam")

        # Build UI layout
        self.create_widgets()
        self.refresh_table()

    def load_data(self):
        """Loads data from the JSON file if it exists."""
        if os.path.exists(self.filename):
            try:
                with open(self.filename, "r") as file:
                    return json.load(file)
            except json.JSONDecodeError:
                messagebox.showwarning("Warning", "Corrupted JSON file detected. Starting with fresh data.")
                return {}
        return {}

    def save_data(self):
        """Saves current data to the JSON file."""
        with open(self.filename, "w") as file:
            json.dump(self.data, file, indent=4)

    def create_widgets(self):
        # App Title Header
        title_lbl = tk.Label(self.root, text="Employee Salary Management", font=("Arial", 16, "bold"), fg="#2c3e50")
        title_lbl.pack(pady=10)

        # Main Layout Container
        content_frame = tk.Frame(self.root)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)

        # --- Left Side: Input Form Frame ---
        form_frame = ttk.LabelFrame(content_frame, text=" Employee Details ")
        form_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 15), ipadx=10, ipady=10)

        fields = [
            ("Employee ID:", "emp_id_entry"),
            ("Full Name:", "name_entry"),
            ("Base Salary ($):", "base_entry"),
            ("Bonus ($):", "bonus_entry"),
            ("Deductions ($):", "deduct_entry")
        ]

        self.entries = {}
        for idx, (label_text, attr_name) in enumerate(fields):
            lbl = tk.Label(form_frame, text=label_text, font=("Arial", 10, "bold"), fg="#34495e")
            lbl.grid(row=idx*2, column=0, sticky="w", pady=(8, 2))
            
            entry = ttk.Entry(form_frame, width=25, font=("Arial", 10))
            entry.grid(row=idx*2+1, column=0, sticky="ew", pady=(0, 5))
            self.entries[attr_name] = entry

        # Action Buttons Frame
        btn_frame = tk.Frame(form_frame)
        btn_frame.grid(row=10, column=0, pady=(20, 0), sticky="ew")

        save_btn = tk.Button(btn_frame, text="Save / Update", bg="#27ae60", fg="white", font=("Arial", 10, "bold"), relief="flat", command=self.save_employee)
        save_btn.pack(fill=tk.X, pady=3)

        del_btn = tk.Button(btn_frame, text="Delete Selected", bg="#c0392b", fg="white", font=("Arial", 10, "bold"), relief="flat", command=self.delete_employee)
        del_btn.pack(fill=tk.X, pady=3)

        clear_btn = tk.Button(btn_frame, text="Clear Form", bg="#7f8c8d", fg="white", font=("Arial", 10, "bold"), relief="flat", command=self.clear_form)
        clear_btn.pack(fill=tk.X, pady=3)

        # --- Right Side: Table View Frame ---
        table_frame = ttk.LabelFrame(content_frame, text=" Records List ")
        table_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Scrollbar for table
        tree_scroll = ttk.Scrollbar(table_frame)
        tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.tree = ttk.Treeview(
            table_frame, 
            columns=("id", "name", "base", "bonus", "deduct", "net"), 
            show="headings",
            yscrollcommand=tree_scroll.set
        )
        tree_scroll.config(command=self.tree.yview)

        columns_info = [
            ("id", "ID", 65),
            ("name", "Name", 110),
            ("base", "Base", 75),
            ("bonus", "Bonus", 70),
            ("deduct", "Deduct", 70),
            ("net", "Net ($)", 75)
        ]

        for col_id, heading, width in columns_info:
            self.tree.heading(col_id, text=heading)
            self.tree.column(col_id, width=width, anchor=tk.CENTER if col_id != "name" else tk.W)

        self.tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.tree.bind("<<TreeviewSelect>>", self.on_row_select)

    def refresh_table(self):
        """Clears and re-populates the table view from current data."""
        for row in self.tree.get_children():
            self.tree.delete(row)
        
        for emp_id, details in self.data.items():
            base = details["base_salary"]
            bonus = details["bonus"]
            deduct = details["deductions"]
            net = base + bonus - deduct
            self.tree.insert("", tk.END, values=(emp_id, details["name"], f"{base:.2f}", f"{bonus:.2f}", f"{deduct:.2f}", f"{net:.2f}"))

    def save_employee(self):
        """Adds a new record or updates an existing record based on Employee ID."""
        emp_id = self.entries["emp_id_entry"].get().strip()
        name = self.entries["name_entry"].get().strip()
        base_str = self.entries["base_entry"].get().strip()
        bonus_str = self.entries["bonus_entry"].get().strip()
        deduct_str = self.entries["deduct_entry"].get().strip()

        if not emp_id or not name or not base_str:
            messagebox.showerror("Error", "Employee ID, Name, and Base Salary are required fields.")
            return

        try:
            base = float(base_str)
            bonus = float(bonus_str) if bonus_str else 0.0
            deduct = float(deduct_str) if deduct_str else 0.0
        except ValueError:
            messagebox.showerror("Error", "Salary fields must contain valid numeric values.")
            return

        # Store in dictionary
        self.data[emp_id] = {
            "name": name,
            "base_salary": base,
            "bonus": bonus,
            "deductions": deduct
        }
        
        self.save_data()
        self.refresh_table()
        self.clear_form()
        messagebox.showinfo("Success", f"Employee record for '{name}' saved successfully!")

    def delete_employee(self):
        """Deletes the selected employee record."""
        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showwarning("Warning", "Please select an employee row from the table to delete.")
            return

        if messagebox.askyesno("Confirm Deletion", "Are you sure you want to delete this employee record?"):
            for item in selected_items:
                values = self.tree.item(item, "values")
                emp_id = values[0]
                if emp_id in self.data:
                    del self.data[emp_id]
            
            self.save_data()
            self.refresh_table()
            self.clear_form()
            messagebox.showinfo("Success", "Selected record has been deleted.")

    def clear_form(self):
        """Clears all input boxes."""
        for entry in self.entries.values():
            entry.delete(0, tk.END)

    def on_row_select(self, event):
        """Fills input fields automatically when a row in the table is clicked (useful for quick updates)."""
        selected_items = self.tree.selection()
        if selected_items:
            item = selected_items[0]
            values = self.tree.item(item, "values")
            emp_id, name, base, bonus, deduct, _ = values
            
            self.clear_form()
            self.entries["emp_id_entry"].insert(0, emp_id)
            self.entries["name_entry"].insert(0, name)
            self.entries["base_entry"].insert(0, base)
            self.entries["bonus_entry"].insert(0, bonus)
            self.entries["deduct_entry"].insert(0, deduct)

if __name__ == "__main__":
    root = tk.Tk()
    app = SalaryApp(root)
    root.mainloop()
