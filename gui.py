import tkinter as tk
from tkinter import ttk, messagebox
import records
import algorithms


class GradeEvaluationApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Student Grade Evaluation & Ranking System")
        self.geometry("1040x680")
        self.minsize(960, 580)

        records.load_from_files()

        self.setup_ui()

    def setup_ui(self):
        notebook = ttk.Notebook(self)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.tab_entry = ttk.Frame(notebook)
        self.tab_input_grades = ttk.Frame(notebook)
        self.tab_students = ttk.Frame(notebook)
        self.tab_grades = ttk.Frame(notebook)
        self.tab_rankings = ttk.Frame(notebook)

        notebook.add(self.tab_entry, text="Register Student")
        notebook.add(self.tab_input_grades, text="Input Grades")
        notebook.add(self.tab_students, text="Student Directory")
        notebook.add(self.tab_grades, text="Grades Overview")
        notebook.add(self.tab_rankings, text="Class Rankings")

        self.build_register_tab()
        self.build_input_grades_tab()
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

        table_frame = ttk.Frame(self.tab_grades)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(5, 10))

        cols = ("Student No.", "Name", "Section", "Subject", "Prelim", "Midterm", "Prefinal", "Final", "Subject Final", "Remarks", "Final Avg")
        self.grades_tree = ttk.Treeview(table_frame, columns=cols, show="headings", height=18)

        col_configs = {
            "Student No.": (100, tk.CENTER),
            "Name": (190, tk.W),
            "Section": (95, tk.CENTER),
            "Subject": (120, tk.W),
            "Prelim": (70, tk.CENTER),
            "Midterm": (70, tk.CENTER),
            "Prefinal": (70, tk.CENTER),
            "Final": (70, tk.CENTER),
            "Subject Final": (95, tk.CENTER),
            "Remarks": (80, tk.CENTER),
            "Final Avg": (85, tk.CENTER)
        }

        for col in cols:
            w, anch = col_configs.get(col, (85, tk.CENTER))
            self.grades_tree.heading(col, text=col)
            self.grades_tree.column(col, width=w, minwidth=w, anchor=anch)

        v_scroll = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.grades_tree.yview)
        h_scroll = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL, command=self.grades_tree.xview)
        self.grades_tree.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)

        self.grades_tree.grid(row=0, column=0, sticky="nsew")
        v_scroll.grid(row=0, column=1, sticky="ns")
        h_scroll.grid(row=1, column=0, sticky="ew")

        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)

        self.load_grades_view()

    def load_grades_view(self):
        sec = self.grades_sec_cb.get().strip()
        for row in self.grades_tree.get_children():
            self.grades_tree.delete(row)

        current_student = None
        student_idx = 0

        self.grades_tree.tag_configure("even_student", background="#ffffff")
        self.grades_tree.tag_configure("odd_student", background="#f7f9fa")

        for row in records.grades_dataset:
            s_num, name, section, subj, prelim, midterm, prefinal, final, sub_final, remarks, final_avg = row
            if sec == "ALL" or section == sec:
                p_str = f"{float(prelim):.1f}" if prelim != "" and prelim is not None else ""
                m_str = f"{float(midterm):.1f}" if midterm != "" and midterm is not None else ""
                pf_str = f"{float(prefinal):.1f}" if prefinal != "" and prefinal is not None else ""
                f_str = f"{float(final):.1f}" if final != "" and final is not None else ""
                sf_str = f"{float(sub_final):.2f}" if sub_final != "" and sub_final is not None else ""
                fa_str = f"{float(final_avg):.2f}" if final_avg != "" and final_avg is not None else ""

                if s_num != current_student:
                    current_student = s_num
                    student_idx += 1
                    tag = "even_student" if student_idx % 2 == 0 else "odd_student"
                    self.grades_tree.insert("", tk.END, values=(
                        s_num, name, section, subj, p_str, m_str, pf_str, f_str, sf_str, remarks, fa_str
                    ), tags=(tag,))
                else:
                    tag = "even_student" if student_idx % 2 == 0 else "odd_student"
                    self.grades_tree.insert("", tk.END, values=(
                        "", "", "", subj, p_str, m_str, pf_str, f_str, sf_str, remarks, ""
                    ), tags=(tag,))

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

    def _validate_student_num_input(self, text):
        return text == "" or (text.isdigit() and len(text) <= 6)

    def _validate_name_input(self, text):
        return len(text) <= 50

    def _validate_sec_input(self, text):
        return len(text) <= 9

    def build_register_tab(self):
        container = ttk.Frame(self.tab_entry, padding=20)
        container.pack(anchor=tk.NW, fill=tk.BOTH, expand=True)

        card = ttk.LabelFrame(container, text=" Register New Student ", padding=20)
        card.pack(anchor=tk.NW, fill=tk.X, padx=10, pady=10)

        title_lbl = ttk.Label(card, text="Student Information", font=("Arial", 12, "bold"))
        title_lbl.grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=(0, 5))

        sub_lbl = ttk.Label(card, text="Fill in all fields below. Names and sections will be automatically formatted.", font=("Arial", 9), foreground="gray")
        sub_lbl.grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=(0, 15))

        vcmd_num = (self.register(self._validate_student_num_input), "%P")
        vcmd_name = (self.register(self._validate_name_input), "%P")
        vcmd_sec = (self.register(self._validate_sec_input), "%P")

        # Student Number
        ttk.Label(card, text="Student Number:", font=("Arial", 10, "bold")).grid(row=2, column=0, sticky=tk.W, pady=8)
        self.reg_num_ent = ttk.Entry(card, width=36, font=("Arial", 10), validate="key", validatecommand=vcmd_num)
        self.reg_num_ent.grid(row=2, column=1, sticky=tk.W, padx=(10, 0), pady=8)

        # Full Name
        ttk.Label(card, text="Name (SURNAME, FIRSTNAME M.I.):", font=("Arial", 10, "bold")).grid(row=3, column=0, sticky=tk.W, pady=8)
        self.reg_name_ent = ttk.Entry(card, width=36, font=("Arial", 10), validate="key", validatecommand=vcmd_name)
        self.reg_name_ent.grid(row=3, column=1, sticky=tk.W, padx=(10, 0), pady=8)

        # Section
        ttk.Label(card, text="Section (e.g. BSCS-12M1):", font=("Arial", 10, "bold")).grid(row=4, column=0, sticky=tk.W, pady=8)
        self.reg_sec_ent = ttk.Entry(card, width=36, font=("Arial", 10), validate="key", validatecommand=vcmd_sec)
        self.reg_sec_ent.grid(row=4, column=1, sticky=tk.W, padx=(10, 0), pady=8)

        btn_frame = ttk.Frame(card)
        btn_frame.grid(row=5, column=1, sticky=tk.W, padx=(10, 0), pady=(15, 5))

        btn_save = ttk.Button(btn_frame, text="Save Student", command=self.save_new_student)
        btn_save.pack(side=tk.LEFT, padx=(0, 10))

        btn_clear = ttk.Button(btn_frame, text="Clear / Reset", command=self.clear_register_form)
        btn_clear.pack(side=tk.LEFT)

    def clear_register_form(self):
        self.reg_num_ent.delete(0, tk.END)
        self.reg_name_ent.delete(0, tk.END)
        self.reg_sec_ent.delete(0, tk.END)

    def save_new_student(self):
        s_num = self.reg_num_ent.get().strip()
        name = self.reg_name_ent.get().strip().upper()
        sec = self.reg_sec_ent.get().strip().upper()

        if not s_num or not name or not sec:
            messagebox.showerror("Error", "All fields are required.")
            return

        is_valid_num, num_err = records.validate_student_number(s_num)
        if not is_valid_num:
            messagebox.showerror("Error", num_err)
            return

        if s_num in records.dict_student:
            messagebox.showerror("Error", f"Student number '{s_num}' is already registered.")
            return

        is_valid_name, err_msg = records.validate_name_format(name)
        if not is_valid_name:
            messagebox.showerror("Error", err_msg)
            return

        if not records.validate_section(sec):
            messagebox.showerror("Error", "Invalid section format.\nSection must be exactly 9 characters (e.g., BSCS-12M1).")
            return

        records.store_student(name, s_num, sec)
        messagebox.showinfo("Success", f"Student {name} registered successfully!")

        self.clear_register_form()
        self.refresh_sections()
        self.load_students_view()
        self.refresh_grade_students()

    def refresh_sections(self):
        sections = self.get_sections()
        self.rank_sec_cb['values'] = sections
        if sections and not self.rank_sec_cb.get():
            self.rank_sec_cb.current(0)
        self.grades_sec_cb['values'] = ["ALL"] + sections

    def build_input_grades_tab(self):
        container = ttk.Frame(self.tab_input_grades, padding=15)
        container.pack(fill=tk.BOTH, expand=True)

        # 1. Student selection
        sel_frame = ttk.LabelFrame(container, text=" 1. Select Student ", padding=10)
        sel_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(sel_frame, text="Student:", font=("Arial", 10, "bold")).pack(side=tk.LEFT, padx=(5, 5))
        self.grade_student_cb = ttk.Combobox(sel_frame, state="readonly", width=42, font=("Arial", 10))
        self.grade_student_cb.pack(side=tk.LEFT, padx=(0, 10))
        self.grade_student_cb.bind("<<ComboboxSelected>>", self.on_student_selected)

        btn_refresh_st = ttk.Button(sel_frame, text="Refresh List", command=self.refresh_grade_students)
        btn_refresh_st.pack(side=tk.LEFT, padx=5)

        self.student_info_lbl = ttk.Label(sel_frame, text="No student selected", font=("Arial", 9, "italic"), foreground="gray")
        self.student_info_lbl.pack(side=tk.LEFT, padx=(15, 5))

        # 2. Grade Entry Matrix
        matrix_card = ttk.LabelFrame(container, text=" 2. Grade Entry Matrix (0.00 - 100.00) ", padding=15)
        matrix_card.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        headers = [
            ("Subject", tk.W),
            ("Prelim (20%)", tk.CENTER),
            ("Midterm (25%)", tk.CENTER),
            ("Prefinal (25%)", tk.CENTER),
            ("Final (30%)", tk.CENTER),
            ("Subject Final", tk.CENTER),
            ("Remarks", tk.CENTER)
        ]

        for col_idx, (hdr_text, anchor) in enumerate(headers):
            hdr_lbl = ttk.Label(matrix_card, text=hdr_text, font=("Arial", 9, "bold"), anchor=anchor)
            hdr_lbl.grid(row=0, column=col_idx, padx=8, pady=(0, 8), sticky="w" if anchor == tk.W else "ew")

        self.grade_entries = {}
        self.grade_labels = {}
        terms = ['prelim', 'midterm', 'prefinal', 'final']

        for row_idx, subj in enumerate(records.subjects, start=1):
            subj_lbl = ttk.Label(matrix_card, text=subj, font=("Arial", 9, "bold"))
            subj_lbl.grid(row=row_idx, column=0, padx=8, pady=6, sticky=tk.W)

            self.grade_entries[subj] = {}
            for t_idx, term in enumerate(terms, start=1):
                ent = ttk.Entry(matrix_card, width=10, justify=tk.CENTER, font=("Arial", 10))
                ent.grid(row=row_idx, column=t_idx, padx=8, pady=6)
                ent.bind("<KeyRelease>", self.calculate_live_preview)
                self.grade_entries[subj][term] = ent

            lbl_sub_final = ttk.Label(matrix_card, text="--", font=("Arial", 10, "bold"), anchor=tk.CENTER)
            lbl_sub_final.grid(row=row_idx, column=5, padx=8, pady=6)

            lbl_sub_rem = ttk.Label(matrix_card, text="--", font=("Arial", 9, "bold"), anchor=tk.CENTER)
            lbl_sub_rem.grid(row=row_idx, column=6, padx=8, pady=6)

            self.grade_labels[subj] = {
                'final': lbl_sub_final,
                'remarks': lbl_sub_rem
            }

        # 3. Overall Summary
        summary_card = ttk.LabelFrame(container, text=" 3. Overall Summary ", padding=12)
        summary_card.pack(fill=tk.X)

        stat_frame = ttk.Frame(summary_card)
        stat_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10)

        ttk.Label(stat_frame, text="Overall Final Average:", font=("Arial", 10, "bold")).grid(row=0, column=0, sticky=tk.W, pady=2)
        self.overall_avg_val = ttk.Label(stat_frame, text="--", font=("Arial", 11, "bold"), foreground="blue")
        self.overall_avg_val.grid(row=0, column=1, sticky=tk.W, padx=10, pady=2)

        ttk.Label(stat_frame, text="Overall Status / Remarks:", font=("Arial", 10, "bold")).grid(row=1, column=0, sticky=tk.W, pady=2)
        self.overall_rem_val = ttk.Label(stat_frame, text="--", font=("Arial", 11, "bold"), foreground="gray")
        self.overall_rem_val.grid(row=1, column=1, sticky=tk.W, padx=10, pady=2)

        act_frame = ttk.Frame(summary_card)
        act_frame.pack(side=tk.RIGHT, padx=10)

        btn_calc = ttk.Button(act_frame, text="Recalculate", command=self.calculate_live_preview)
        btn_calc.pack(side=tk.LEFT, padx=5)

        btn_save = ttk.Button(act_frame, text="Save Grades", command=self.save_grades_action)
        btn_save.pack(side=tk.LEFT, padx=5)

        btn_clear_g = ttk.Button(act_frame, text="Clear Form", command=self.clear_grades_form)
        btn_clear_g.pack(side=tk.LEFT, padx=5)

        self.refresh_grade_students()

    def refresh_grade_students(self):
        items = []
        for s_num, info in records.dict_student.items():
            items.append(f"{s_num} - {info.get('name', '')} ({info.get('section', '')})")
        self.grade_student_cb['values'] = items
        current_sel = self.grade_student_cb.get()
        if items and not current_sel:
            self.grade_student_cb.current(0)
            self.on_student_selected()
        elif current_sel and current_sel in items:
            self.on_student_selected()

    def get_selected_student_number(self):
        val = self.grade_student_cb.get().strip()
        if not val or " - " not in val:
            return None
        return val.split(" - ")[0].strip()

    def on_student_selected(self, event=None):
        s_num = self.get_selected_student_number()
        if not s_num or s_num not in records.dict_student:
            self.student_info_lbl.config(text="No student selected", foreground="gray")
            return

        s_info = records.dict_student[s_num]
        self.student_info_lbl.config(
            text=f"Student: {s_info.get('name', '')} [{s_info.get('section', '')}]",
            foreground="darkgreen"
        )

        terms = ['prelim', 'midterm', 'prefinal', 'final']
        if s_num in records.dict_grades:
            g_data = records.dict_grades[s_num]
            for subj in records.subjects:
                subj_data = g_data.get(subj, {})
                for term in terms:
                    val = subj_data.get(term, "")
                    ent = self.grade_entries[subj][term]
                    ent.delete(0, tk.END)
                    if val != "" and val is not None:
                        ent.insert(0, str(val))
        else:
            self.clear_grades_entries()

        self.calculate_live_preview()

    def clear_grades_entries(self):
        terms = ['prelim', 'midterm', 'prefinal', 'final']
        for subj in records.subjects:
            for term in terms:
                self.grade_entries[subj][term].delete(0, tk.END)
            self.grade_labels[subj]['final'].config(text="--")
            self.grade_labels[subj]['remarks'].config(text="--", foreground="black")
        self.overall_avg_val.config(text="--", foreground="blue")
        self.overall_rem_val.config(text="--", foreground="gray")

    def clear_grades_form(self):
        self.clear_grades_entries()

    def calculate_live_preview(self, event=None):
        terms = ['prelim', 'midterm', 'prefinal', 'final']
        subject_final_grades = []

        for subj in records.subjects:
            vals = {}
            all_valid = True
            for term in terms:
                raw = self.grade_entries[subj][term].get().strip()
                if not raw:
                    all_valid = False
                    break
                try:
                    num = float(raw)
                    if 0.0 <= num <= 100.0:
                        vals[term] = num
                    else:
                        all_valid = False
                        break
                except ValueError:
                    all_valid = False
                    break

            if all_valid and len(vals) == 4:
                sub_final = round(vals['prelim'] * 0.20 + vals['midterm'] * 0.25 + vals['prefinal'] * 0.25 + vals['final'] * 0.30, 2)
                sub_rem = "PASSED" if sub_final >= 75 else "FAILED"
                color = "green" if sub_final >= 75 else "red"

                self.grade_labels[subj]['final'].config(text=f"{sub_final:.2f}")
                self.grade_labels[subj]['remarks'].config(text=sub_rem, foreground=color)
                subject_final_grades.append(sub_final)
            else:
                self.grade_labels[subj]['final'].config(text="--")
                self.grade_labels[subj]['remarks'].config(text="--", foreground="black")

        if len(subject_final_grades) == len(records.subjects):
            overall_avg = round(sum(subject_final_grades) / len(subject_final_grades), 2)
            overall_rem = "PASSED" if overall_avg >= 75 else "FAILED"
            color = "green" if overall_avg >= 75 else "red"
            self.overall_avg_val.config(text=f"{overall_avg:.2f}", foreground="blue")
            self.overall_rem_val.config(text=overall_rem, foreground=color)
        elif subject_final_grades:
            overall_avg = round(sum(subject_final_grades) / len(subject_final_grades), 2)
            self.overall_avg_val.config(text=f"{overall_avg:.2f} (partial)", foreground="blue")
            self.overall_rem_val.config(text="Incomplete", foreground="orange")
        else:
            self.overall_avg_val.config(text="--", foreground="blue")
            self.overall_rem_val.config(text="--", foreground="gray")

    def save_grades_action(self):
        s_num = self.get_selected_student_number()
        if not s_num:
            messagebox.showerror("Error", "Please select a student first.")
            return

        terms = ['prelim', 'midterm', 'prefinal', 'final']
        subject_scores = {}

        for subj in records.subjects:
            subject_scores[subj] = {}
            for term in terms:
                raw = self.grade_entries[subj][term].get().strip()
                if not raw:
                    messagebox.showerror("Error", f"Please enter a grade for {subj} - {term.capitalize()}.")
                    return
                ok, res = records.validate_grade(raw)
                if not ok:
                    messagebox.showerror("Validation Error", f"Invalid grade for {subj} - {term.capitalize()}:\n{res}")
                    return
                subject_scores[subj][term] = res

        success, msg = records.save_student_grades(s_num, subject_scores)
        if success:
            messagebox.showinfo("Success", msg)
            self.calculate_live_preview()
            self.load_grades_view()
            self.refresh_sections()
        else:
            messagebox.showerror("Error", msg)


def main():
    app = GradeEvaluationApp()
    app.mainloop()


if __name__ == "__main__":
    main()
