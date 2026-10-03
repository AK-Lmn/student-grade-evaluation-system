import tkinter as tk
from tkinter import ttk, messagebox
import records
import algorithms


class GradeEvaluationApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Student Grade Evaluation & Ranking System")
        self.geometry("950x650")
        self.minsize(850, 550)

        records.load_from_files()

        self.setup_ui()

    def setup_ui(self):
        notebook = ttk.Notebook(self)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.tab_entry = ttk.Frame(notebook)
        self.tab_students = ttk.Frame(notebook)
        self.tab_grades = ttk.Frame(notebook)
        self.tab_rankings = ttk.Frame(notebook)

        notebook.add(self.tab_entry, text="Register Student")
        notebook.add(self.tab_students, text="Student Directory")
        notebook.add(self.tab_grades, text="Grades Overview")
        notebook.add(self.tab_rankings, text="Class Rankings")

        self.build_register_tab()
        self.build_students_tab()
        self.build_grades_tab()
        self.build_rankings_tab()

    def get_sections(self):
        sections = set()
        for info in records.dict_student.values():
            if 'section' in info and info['section']:
                sections.add(info['section'])
        for info in records.dict_grades.values():
            if 'section' in info and info['section']:
                sections.add(info['section'])
        return sorted(list(sections))

    def build_rankings_tab(self):
        top_frame = ttk.Frame(self.tab_rankings, padding=10)
        top_frame.pack(fill=tk.X)

        ttk.Label(top_frame, text="Select Section:").pack(side=tk.LEFT, padx=5)

        self.rank_sec_cb = ttk.Combobox(top_frame, values=self.get_sections(), state="readonly", width=18)
        self.rank_sec_cb.pack(side=tk.LEFT, padx=5)
        if self.get_sections():
            self.rank_sec_cb.current(0)

        btn_rank = ttk.Button(top_frame, text="Rank Students", command=self.run_ranking)
        btn_rank.pack(side=tk.LEFT, padx=10)

        btn_refresh = ttk.Button(top_frame, text="Refresh Sections", command=self.refresh_sections)
        btn_refresh.pack(side=tk.LEFT, padx=5)

        cols = ("Rank", "Student No.", "Name", "Section", "Final Average", "Remarks")
        self.rank_tree = ttk.Treeview(self.tab_rankings, columns=cols, show="headings", height=18)
        
        col_widths = {"Rank": 70, "Student No.": 130, "Name": 230, "Section": 120, "Final Average": 120, "Remarks": 100}
        for col in cols:
            self.rank_tree.heading(col, text=col)
            self.rank_tree.column(col, width=col_widths.get(col, 100), anchor=tk.CENTER if col in ("Rank", "Remarks", "Final Average") else tk.W)

        scroll = ttk.Scrollbar(self.tab_rankings, orient=tk.VERTICAL, command=self.rank_tree.yview)
        self.rank_tree.configure(yscrollcommand=scroll.set)
        
        self.rank_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 0), pady=10)
        scroll.pack(side=tk.RIGHT, fill=tk.Y, padx=(0, 10), pady=10)

    def run_ranking(self):
        sec = self.rank_sec_cb.get().strip()
        if not sec:
            messagebox.showwarning("Warning", "Please select a section to rank.")
            return

        student_list = []
        for s_num, g_data in records.dict_grades.items():
            if g_data.get('section') == sec:
                student_list.append({
                    "student_number": s_num,
                    "name": g_data.get('name', ''),
                    "section": g_data.get('section', ''),
                    "final_average": g_data.get('final_average', 0.0),
                    "remarks": g_data.get('remarks', '')
                })

        for row in self.rank_tree.get_children():
            self.rank_tree.delete(row)

        if not student_list:
            messagebox.showinfo("Information", f"No grades recorded for section {sec}.")
            return

        sorted_list = algorithms.bubble_sort_students(student_list)

        for rank, s in enumerate(sorted_list, 1):
            self.rank_tree.insert("", tk.END, values=(
                rank,
                s["student_number"],
                s["name"],
                s["section"],
                f"{s['final_average']:.2f}",
                s["remarks"]
            ))

    def build_grades_tab(self):
        top_frame = ttk.Frame(self.tab_grades, padding=10)
        top_frame.pack(fill=tk.X)

        ttk.Label(top_frame, text="Filter Section:").pack(side=tk.LEFT, padx=5)
        self.grades_sec_cb = ttk.Combobox(top_frame, values=["ALL"] + self.get_sections(), state="readonly", width=18)
        self.grades_sec_cb.pack(side=tk.LEFT, padx=5)
        self.grades_sec_cb.set("ALL")

        btn_view = ttk.Button(top_frame, text="View Grades", command=self.load_grades_view)
        btn_view.pack(side=tk.LEFT, padx=10)

        cols = ("Student No.", "Name", "Section", "Subject", "Prelim", "Midterm", "Prefinal", "Final", "Subject Final", "Remarks", "Final Avg")
        self.grades_tree = ttk.Treeview(self.tab_grades, columns=cols, show="headings", height=18)

        for col in cols:
            self.grades_tree.heading(col, text=col)
            self.grades_tree.column(col, width=80, anchor=tk.CENTER)
        self.grades_tree.column("Name", width=160, anchor=tk.W)
        self.grades_tree.column("Student No.", width=110, anchor=tk.W)

        scroll = ttk.Scrollbar(self.tab_grades, orient=tk.VERTICAL, command=self.grades_tree.yview)
        self.grades_tree.configure(yscrollcommand=scroll.set)
        
        self.grades_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 0), pady=10)
        scroll.pack(side=tk.RIGHT, fill=tk.Y, padx=(0, 10), pady=10)

        self.load_grades_view()

    def load_grades_view(self):
        sec = self.grades_sec_cb.get().strip()
        for row in self.grades_tree.get_children():
            self.grades_tree.delete(row)

        for row in records.grades_dataset:
            s_num, name, section, subj, prelim, midterm, prefinal, final, sub_final, remarks, final_avg = row
            if sec == "ALL" or section == sec:
                self.grades_tree.insert("", tk.END, values=(
                    s_num, name, section, subj, prelim, midterm, prefinal, final, sub_final, remarks, final_avg
                ))

    def build_students_tab(self):
        top_frame = ttk.Frame(self.tab_students, padding=10)
        top_frame.pack(fill=tk.X)

        ttk.Label(top_frame, text="Search Student No:").pack(side=tk.LEFT, padx=5)
        self.search_entry = ttk.Entry(top_frame, width=20)
        self.search_entry.pack(side=tk.LEFT, padx=5)

        btn_search = ttk.Button(top_frame, text="Search (Linear)", command=self.search_student)
        btn_search.pack(side=tk.LEFT, padx=5)

        btn_reset = ttk.Button(top_frame, text="Show All", command=self.load_students_view)
        btn_reset.pack(side=tk.LEFT, padx=5)

        cols = ("Student No.", "Name", "Section")
        self.students_tree = ttk.Treeview(self.tab_students, columns=cols, show="headings", height=18)
        for col in cols:
            self.students_tree.heading(col, text=col)
            self.students_tree.column(col, width=150, anchor=tk.W)

        scroll = ttk.Scrollbar(self.tab_students, orient=tk.VERTICAL, command=self.students_tree.yview)
        self.students_tree.configure(yscrollcommand=scroll.set)

        self.students_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 0), pady=10)
        scroll.pack(side=tk.RIGHT, fill=tk.Y, padx=(0, 10), pady=10)

        self.load_students_view()

    def load_students_view(self):
        for row in self.students_tree.get_children():
            self.students_tree.delete(row)
        for s_num, info in records.dict_student.items():
            self.students_tree.insert("", tk.END, values=(s_num, info.get('name', ''), info.get('section', '')))

    def search_student(self):
        query = self.search_entry.get().strip()
        if not query:
            self.load_students_view()
            return

        all_students = [
            {"student_number": s_num, "name": info['name'], "section": info['section']}
            for s_num, info in records.dict_student.items()
        ]

        idx, found = algorithms.linear_search_student(all_students, query)

        for row in self.students_tree.get_children():
            self.students_tree.delete(row)

        if found:
            self.students_tree.insert("", tk.END, values=(found["student_number"], found["name"], found["section"]))
        else:
            messagebox.showinfo("Search Result", f"Student number '{query}' not found.")

    def build_register_tab(self):
        frame = ttk.Frame(self.tab_entry, padding=25)
        frame.pack(anchor=tk.NW)

        ttk.Label(frame, text="Register New Student", font=("Arial", 12, "bold")).grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=(0, 15))

        ttk.Label(frame, text="Student Number:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.reg_num_ent = ttk.Entry(frame, width=32)
        self.reg_num_ent.grid(row=1, column=1, sticky=tk.W, pady=5)

        ttk.Label(frame, text="Name (SURNAME, FIRSTNAME M.I.):").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.reg_name_ent = ttk.Entry(frame, width=32)
        self.reg_name_ent.grid(row=2, column=1, sticky=tk.W, pady=5)

        ttk.Label(frame, text="Section (e.g. BSCS-12M1):").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.reg_sec_ent = ttk.Entry(frame, width=32)
        self.reg_sec_ent.grid(row=3, column=1, sticky=tk.W, pady=5)

        btn_save = ttk.Button(frame, text="Save Student", command=self.save_new_student)
        btn_save.grid(row=4, column=1, sticky=tk.W, pady=15)

    def save_new_student(self):
        s_num = self.reg_num_ent.get().strip()
        name = self.reg_name_ent.get().strip()
        sec = self.reg_sec_ent.get().strip()

        if not s_num or not name or not sec:
            messagebox.showerror("Error", "All fields are required.")
            return

        if s_num in records.dict_student:
            messagebox.showerror("Error", "Student number already registered.")
            return

        if not records.validate_section(sec):
            messagebox.showerror("Error", "Invalid section format. Example: BSCS-12M1")
            return

        is_valid_name, err_msg = records.validate_name_format(name)
        if not is_valid_name:
            messagebox.showerror("Error", err_msg)
            return

        records.store_student(name, s_num, sec)
        messagebox.showinfo("Success", f"Student {name} registered successfully!")

        self.reg_num_ent.delete(0, tk.END)
        self.reg_name_ent.delete(0, tk.END)
        self.reg_sec_ent.delete(0, tk.END)

        self.refresh_sections()
        self.load_students_view()

    def refresh_sections(self):
        sections = self.get_sections()
        self.rank_sec_cb['values'] = sections
        if sections and not self.rank_sec_cb.get():
            self.rank_sec_cb.current(0)
        self.grades_sec_cb['values'] = ["ALL"] + sections


def main():
    app = GradeEvaluationApp()
    app.mainloop()


if __name__ == "__main__":
    main()
