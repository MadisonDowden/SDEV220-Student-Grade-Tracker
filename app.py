"""Tkinter user interface for the Student Grade Tracker."""

from __future__ import annotations

import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from grade_tracker import GradeTracker


class GradeTrackerApp(tk.Tk):
    """Main graphical interface."""

    def __init__(self) -> None:
        super().__init__()
        self.title("Student Grade Tracker")
        self.geometry("1180x720")
        self.minsize(1000, 620)
        self.tracker = GradeTracker()
        self.selected_grade: tuple[str, int] | None = None
        self._configure_style()
        self._build_menu()
        self._build_ui()
        self.refresh_all()

    def _configure_style(self) -> None:
        style = ttk.Style(self)
        if "vista" in style.theme_names():
            style.theme_use("vista")
        style.configure("Title.TLabel", font=("Segoe UI", 22, "bold"))
        style.configure("Subtitle.TLabel", font=("Segoe UI", 10))
        style.configure("Summary.TLabel", font=("Segoe UI", 11, "bold"), padding=8)

    def _build_menu(self) -> None:
        menu = tk.Menu(self)
        file_menu = tk.Menu(menu, tearoff=False)
        file_menu.add_command(label="Export CSV Report", command=self.export_csv)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.destroy)
        menu.add_cascade(label="File", menu=file_menu)

        help_menu = tk.Menu(menu, tearoff=False)
        help_menu.add_command(label="About", command=self.show_about)
        menu.add_cascade(label="Help", menu=help_menu)
        self.config(menu=menu)

    def _build_ui(self) -> None:
        header = ttk.Frame(self, padding=(14, 12, 14, 4))
        header.pack(fill="x")
        title_block = ttk.Frame(header)
        title_block.pack(side="left")
        ttk.Label(title_block, text="Student Grade Tracker", style="Title.TLabel").pack(anchor="w")
        ttk.Label(
            title_block,
            text="Software Development Final Project • Madison Dowden • SDEV 220",
            style="Subtitle.TLabel",
        ).pack(anchor="w", pady=(1, 0))
        ttk.Label(
            header,
            text="Manage students, courses, assignments, and reports",
        ).pack(side="left", padx=24, pady=(18, 0))

        summary = ttk.Frame(self, padding=(14, 6, 14, 10))
        summary.pack(fill="x")
        self.summary_labels: dict[str, tk.Label] = {}
        cards = (
            ("students", "Students", "#dbeafe"),
            ("courses", "Courses", "#dcfce7"),
            ("grades", "Grades", "#fef3c7"),
            ("average", "Class Average", "#ffedd5"),
            ("honors", "Honors Students", "#f3e8ff"),
        )
        for key, label, background in cards:
            widget = tk.Label(
                summary,
                text=f"{label}: 0",
                font=("Segoe UI", 11, "bold"),
                bg=background,
                fg="#111827",
                padx=12,
                pady=9,
                relief="solid",
                borderwidth=1,
            )
            widget.pack(side="left", padx=(0, 8))
            self.summary_labels[key] = widget

        student_controls = ttk.Labelframe(self, text="Student Management", padding=10)
        student_controls.pack(fill="x", padx=14, pady=(0, 8))

        ttk.Label(student_controls, text="Student ID").grid(row=0, column=0, sticky="w")
        self.student_id_entry = ttk.Entry(student_controls, width=16)
        self.student_id_entry.grid(row=1, column=0, padx=(0, 8))
        ttk.Label(student_controls, text="Student Name").grid(row=0, column=1, sticky="w")
        self.student_name_entry = ttk.Entry(student_controls, width=28)
        self.student_name_entry.grid(row=1, column=1, padx=(0, 8))
        ttk.Button(student_controls, text="Add Student", command=self.add_student).grid(row=1, column=2, padx=4)
        ttk.Button(student_controls, text="Update Name", command=self.update_student).grid(row=1, column=3, padx=4)
        ttk.Button(student_controls, text="Delete Student", command=self.delete_student).grid(row=1, column=4, padx=4)

        ttk.Label(student_controls, text="Search ID or name").grid(row=0, column=5, sticky="w", padx=(24, 0))
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *_: self.refresh_students())
        ttk.Entry(student_controls, textvariable=self.search_var, width=24).grid(row=1, column=5, padx=(24, 4))
        ttk.Button(student_controls, text="Clear", command=lambda: self.search_var.set("")).grid(row=1, column=6, padx=4)
        ttk.Label(student_controls, text="Sort students").grid(row=0, column=7, sticky="w", padx=(18, 0))
        self.sort_var = tk.StringVar(value="Name (A-Z)")
        sort_box = ttk.Combobox(
            student_controls,
            textvariable=self.sort_var,
            values=("Name (A-Z)", "Name (Z-A)", "Highest Average", "Lowest Average", "Highest GPA"),
            state="readonly",
            width=18,
        )
        sort_box.grid(row=1, column=7, padx=(18, 0))
        sort_box.bind("<<ComboboxSelected>>", lambda _event: self.refresh_students())

        body = ttk.Panedwindow(self, orient="horizontal")
        body.pack(fill="both", expand=True, padx=14, pady=(0, 8))

        students_panel = ttk.Labelframe(body, text="Students", padding=8)
        details_panel = ttk.Labelframe(body, text="Courses and Grades", padding=8)
        body.add(students_panel, weight=1)
        body.add(details_panel, weight=3)

        self.student_tree = ttk.Treeview(students_panel, columns=("id", "name", "average", "gpa", "recognition"), show="headings")
        for column, heading, width in (
            ("id", "Student ID", 90),
            ("name", "Name", 165),
            ("average", "Average", 80),
            ("gpa", "GPA", 60),
            ("recognition", "Recognition", 135),
        ):
            self.student_tree.heading(column, text=heading)
            self.student_tree.column(column, width=width, anchor="center")
        self.student_tree.pack(fill="both", expand=True)
        self.student_tree.bind("<<TreeviewSelect>>", self.on_student_selected)

        course_controls = ttk.Frame(details_panel)
        course_controls.pack(fill="x", pady=(0, 8))
        ttk.Label(course_controls, text="Course Name").grid(row=0, column=0, sticky="w")
        self.course_entry = ttk.Entry(course_controls, width=25)
        self.course_entry.grid(row=1, column=0, padx=(0, 6))
        ttk.Button(course_controls, text="Add Course", command=self.add_course).grid(row=1, column=1, padx=4)
        ttk.Button(course_controls, text="Delete Course", command=self.delete_course).grid(row=1, column=2, padx=4)

        ttk.Label(course_controls, text="Assignment").grid(row=0, column=3, sticky="w", padx=(18, 0))
        self.assignment_entry = ttk.Entry(course_controls, width=25)
        self.assignment_entry.grid(row=1, column=3, padx=(18, 6))
        ttk.Label(course_controls, text="Score").grid(row=0, column=4, sticky="w")
        self.score_entry = ttk.Entry(course_controls, width=10)
        self.score_entry.grid(row=1, column=4, padx=(0, 6))
        ttk.Button(course_controls, text="Add Grade", command=self.add_grade).grid(row=1, column=5, padx=4)
        ttk.Button(course_controls, text="Update Grade", command=self.update_grade).grid(row=1, column=6, padx=4)
        ttk.Button(course_controls, text="Delete Grade", command=self.delete_grade).grid(row=1, column=7, padx=4)

        self.grade_tree = ttk.Treeview(
            details_panel,
            columns=("course", "assignment", "score", "letter", "course_average"),
            show="headings",
        )
        for column, heading, width in (
            ("course", "Course", 190),
            ("assignment", "Assignment", 240),
            ("score", "Score", 80),
            ("letter", "Letter", 70),
            ("course_average", "Course Avg", 100),
        ):
            self.grade_tree.heading(column, text=heading)
            self.grade_tree.column(column, width=width, anchor="center")
        self.grade_tree.pack(fill="both", expand=True)
        self.grade_tree.bind("<<TreeviewSelect>>", self.on_grade_selected)

        self.status = ttk.Label(self, text="Ready", relief="sunken", anchor="w", padding=5)
        self.status.pack(fill="x", side="bottom")

    def selected_student_id(self) -> str | None:
        selected = self.student_tree.selection()
        return str(self.student_tree.item(selected[0], "values")[0]) if selected else None

    def selected_course_name(self) -> str | None:
        selected = self.grade_tree.selection()
        if selected:
            return str(self.grade_tree.item(selected[0], "values")[0])
        entered = self.course_entry.get().strip()
        return entered or None

    def on_student_selected(self, _event=None) -> None:
        student_id = self.selected_student_id()
        if student_id:
            student = self.tracker.students[student_id]
            self.student_id_entry.delete(0, "end")
            self.student_id_entry.insert(0, student.student_id)
            self.student_name_entry.delete(0, "end")
            self.student_name_entry.insert(0, student.name)
        self.selected_grade = None
        self.refresh_grades()

    def on_grade_selected(self, _event=None) -> None:
        selected = self.grade_tree.selection()
        student_id = self.selected_student_id()
        if not selected or not student_id:
            return
        item = selected[0]
        values = self.grade_tree.item(item, "values")
        course_name = str(values[0])
        grade_index_text = self.grade_tree.item(item, "tags")
        self.course_entry.delete(0, "end")
        self.course_entry.insert(0, course_name)
        if grade_index_text and grade_index_text[0] != "empty":
            grade_index = int(grade_index_text[0])
            grade = self.tracker.students[student_id].courses[course_name].grades[grade_index]
            self.selected_grade = (course_name, grade_index)
            self.assignment_entry.delete(0, "end")
            self.assignment_entry.insert(0, grade.assignment)
            self.score_entry.delete(0, "end")
            self.score_entry.insert(0, f"{grade.score:g}")
        else:
            self.selected_grade = None

    def add_student(self) -> None:
        self._run_action(
            lambda: self.tracker.add_student(self.student_id_entry.get(), self.student_name_entry.get()),
            "Student added successfully.",
            clear_student=True,
        )

    def update_student(self) -> None:
        student_id = self.selected_student_id()
        if not student_id:
            self._info("Select a student first.")
            return
        self._run_action(
            lambda: self.tracker.update_student(student_id, self.student_name_entry.get()),
            "Student name updated successfully.",
        )

    def delete_student(self) -> None:
        student_id = self.selected_student_id()
        if not student_id:
            self._info("Select a student first.")
            return
        if messagebox.askyesno("Confirm Delete", "Delete this student and every related course and grade?"):
            self._run_action(lambda: self.tracker.delete_student(student_id), "Student deleted successfully.", clear_student=True)

    def add_course(self) -> None:
        student_id = self.selected_student_id()
        if not student_id:
            self._info("Select a student first.")
            return
        self._run_action(
            lambda: self.tracker.add_course(student_id, self.course_entry.get()),
            "Course added successfully.",
            clear_course=True,
        )

    def delete_course(self) -> None:
        student_id = self.selected_student_id()
        course_name = self.selected_course_name()
        if not student_id or not course_name:
            self._info("Select a student and course first.")
            return
        if messagebox.askyesno("Confirm Delete", f"Delete {course_name} and all of its grades?"):
            self._run_action(
                lambda: self.tracker.delete_course(student_id, course_name),
                "Course deleted successfully.",
                clear_course=True,
            )

    def add_grade(self) -> None:
        student_id = self.selected_student_id()
        course_name = self.selected_course_name()
        if not student_id or not course_name:
            self._info("Select a student and enter or select a course.")
            return
        self._run_action(
            lambda: self.tracker.add_grade(
                student_id,
                course_name,
                self.assignment_entry.get(),
                float(self.score_entry.get()),
            ),
            "Grade added successfully.",
            clear_grade=True,
        )

    def update_grade(self) -> None:
        student_id = self.selected_student_id()
        if not student_id or not self.selected_grade:
            self._info("Select an existing grade first.")
            return
        course_name, grade_index = self.selected_grade
        self._run_action(
            lambda: self.tracker.update_grade(
                student_id,
                course_name,
                grade_index,
                self.assignment_entry.get(),
                float(self.score_entry.get()),
            ),
            "Grade updated successfully.",
            clear_grade=True,
        )

    def delete_grade(self) -> None:
        student_id = self.selected_student_id()
        if not student_id or not self.selected_grade:
            self._info("Select an existing grade first.")
            return
        course_name, grade_index = self.selected_grade
        if messagebox.askyesno("Confirm Delete", "Delete the selected grade?"):
            self._run_action(
                lambda: self.tracker.delete_grade(student_id, course_name, grade_index),
                "Grade deleted successfully.",
                clear_grade=True,
            )

    def refresh_all(self) -> None:
        self.refresh_students()
        self.refresh_grades()
        self.refresh_summary()

    def refresh_students(self) -> None:
        selected_id = self.selected_student_id()
        self.student_tree.delete(*self.student_tree.get_children())
        selected_item = None
        for student in self.tracker.search_students(self.search_var.get(), self.sort_var.get()):
            item = self.student_tree.insert(
                "",
                "end",
                values=(
                    student.student_id,
                    student.name,
                    f"{student.overall_average:.1f}%",
                    f"{student.gpa:.2f}",
                    student.recognition,
                ),
            )
            if student.student_id == selected_id:
                selected_item = item
        if selected_item:
            self.student_tree.selection_set(selected_item)
            self.student_tree.focus(selected_item)

    def refresh_grades(self) -> None:
        self.grade_tree.delete(*self.grade_tree.get_children())
        student_id = self.selected_student_id()
        if not student_id:
            return
        student = self.tracker.students[student_id]
        for course in sorted(student.courses.values(), key=lambda item: item.name.lower()):
            if not course.grades:
                self.grade_tree.insert(
                    "", "end", values=(course.name, "No grades yet", "—", "—", "0.0%"), tags=("empty",)
                )
                continue
            for index, grade in enumerate(course.grades):
                self.grade_tree.insert(
                    "",
                    "end",
                    values=(course.name, grade.assignment, f"{grade.score:.1f}", grade.letter, f"{course.average:.1f}%"),
                    tags=(str(index),),
                )

    def refresh_summary(self) -> None:
        summary = self.tracker.summary()
        self.summary_labels["students"].config(text=f"Students: {summary['students']}")
        self.summary_labels["courses"].config(text=f"Courses: {summary['courses']}")
        self.summary_labels["grades"].config(text=f"Grades: {summary['grades']}")
        self.summary_labels["average"].config(text=f"Class Average: {summary['average']:.1f}%")
        self.summary_labels["honors"].config(text=f"Honors Students: {summary['honors']}")

    def export_csv(self) -> None:
        path = filedialog.asksaveasfilename(
            title="Export Grade Report",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            initialfile="student_grade_report.csv",
        )
        if not path:
            return
        try:
            self.tracker.export_csv(path)
            self.status.config(text=f"Report exported successfully: {path}")
            messagebox.showinfo("Export Complete", "The CSV report was created successfully.")
        except OSError as error:
            messagebox.showerror("Export Failed", str(error))

    def show_about(self) -> None:
        messagebox.showinfo(
            "About Student Grade Tracker",
            "Student Grade Tracker\n\nCreated by Madison Dowden\nSDEV 220 Final Project\nIvy Tech Community College\n\nPython Desktop Application",
        )

    def _run_action(self, action, success_message: str, *, clear_student=False, clear_course=False, clear_grade=False) -> None:
        try:
            action()
            if clear_student:
                self.student_id_entry.delete(0, "end")
                self.student_name_entry.delete(0, "end")
            if clear_course:
                self.course_entry.delete(0, "end")
            if clear_grade:
                self.assignment_entry.delete(0, "end")
                self.score_entry.delete(0, "end")
                self.selected_grade = None
            self.refresh_all()
            self.status.config(text=success_message)
        except (ValueError, OSError) as error:
            messagebox.showerror("Unable to Complete Action", str(error))

    @staticmethod
    def _info(message: str) -> None:
        messagebox.showinfo("Selection Required", message)
