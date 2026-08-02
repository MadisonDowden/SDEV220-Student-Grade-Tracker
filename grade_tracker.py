"""Business logic, persistence, search, and reporting."""

from __future__ import annotations

import csv
import json
from pathlib import Path

from models import Course, Grade, Student

DEFAULT_DATA_FILE = Path(__file__).parent / "data" / "students.json"


class GradeTracker:
    """Manages all student records and application operations."""

    def __init__(self, data_file: Path = DEFAULT_DATA_FILE) -> None:
        self.data_file = Path(data_file)
        self.students: dict[str, Student] = {}
        self.load()

    def add_student(self, student_id: str, name: str) -> None:
        student = Student(student_id, name)
        if student.student_id in self.students:
            raise ValueError("That student ID already exists.")
        self.students[student.student_id] = student
        self.save()

    def update_student(self, student_id: str, new_name: str) -> None:
        new_name = new_name.strip()
        if not new_name:
            raise ValueError("Student name is required.")
        self._get_student(student_id).name = new_name
        self.save()

    def delete_student(self, student_id: str) -> None:
        self._get_student(student_id)
        del self.students[student_id]
        self.save()

    def add_course(self, student_id: str, course_name: str) -> None:
        self._get_student(student_id).add_course(course_name)
        self.save()

    def delete_course(self, student_id: str, course_name: str) -> None:
        self._get_student(student_id).delete_course(course_name)
        self.save()

    def add_grade(self, student_id: str, course_name: str, assignment: str, score: float) -> None:
        self._get_course(student_id, course_name).add_grade(assignment, score)
        self.save()

    def update_grade(
        self,
        student_id: str,
        course_name: str,
        grade_index: int,
        assignment: str,
        score: float,
    ) -> None:
        course = self._get_course(student_id, course_name)
        self._validate_grade_index(course, grade_index)
        course.update_grade(grade_index, assignment, score)
        self.save()

    def delete_grade(self, student_id: str, course_name: str, grade_index: int) -> None:
        course = self._get_course(student_id, course_name)
        self._validate_grade_index(course, grade_index)
        course.delete_grade(grade_index)
        self.save()

    def search_students(self, query: str, sort_by: str = "Name (A-Z)") -> list[Student]:
        query = query.strip().lower()
        students = list(self.students.values())
        if query:
            students = [
                student
                for student in students
                if query in student.student_id.lower() or query in student.name.lower()
            ]
        sort_options = {
            "Name (A-Z)": lambda student: (student.name.lower(), student.student_id),
            "Name (Z-A)": lambda student: (student.name.lower(), student.student_id),
            "Highest Average": lambda student: student.overall_average,
            "Lowest Average": lambda student: student.overall_average,
            "Highest GPA": lambda student: student.gpa,
        }
        reverse = sort_by in {"Name (Z-A)", "Highest Average", "Highest GPA"}
        return sorted(students, key=sort_options.get(sort_by, sort_options["Name (A-Z)"]), reverse=reverse)

    def save(self) -> None:
        self.data_file.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            student_id: {
                "student_id": student.student_id,
                "name": student.name,
                "courses": {
                    course_name: {
                        "name": course.name,
                        "grades": [
                            {"assignment": grade.assignment, "score": grade.score}
                            for grade in course.grades
                        ],
                    }
                    for course_name, course in student.courses.items()
                },
            }
            for student_id, student in self.students.items()
        }
        temporary_file = self.data_file.with_suffix(".tmp")
        temporary_file.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        temporary_file.replace(self.data_file)

    def load(self) -> None:
        if not self.data_file.exists():
            return
        try:
            raw_data = json.loads(self.data_file.read_text(encoding="utf-8"))
            loaded: dict[str, Student] = {}
            for student_id, raw_student in raw_data.items():
                student = Student(raw_student["student_id"], raw_student["name"])
                for course_name, raw_course in raw_student.get("courses", {}).items():
                    course = Course(raw_course["name"])
                    course.grades = [
                        Grade(item["assignment"], float(item["score"]))
                        for item in raw_course.get("grades", [])
                    ]
                    student.courses[course_name] = course
                loaded[student_id] = student
            self.students = loaded
        except (OSError, json.JSONDecodeError, KeyError, TypeError, ValueError):
            self.students = {}

    def export_csv(self, path: str | Path) -> None:
        with Path(path).open("w", newline="", encoding="utf-8") as report:
            writer = csv.writer(report)
            writer.writerow(
                [
                    "Student ID",
                    "Student Name",
                    "Course",
                    "Assignment",
                    "Score",
                    "Letter Grade",
                    "Course Average",
                    "Overall Average",
                    "Estimated GPA",
                    "Recognition",
                ]
            )
            for student in self.search_students(""):
                if not student.courses:
                    writer.writerow([student.student_id, student.name, "", "", "", "", "", "0.0", "0.00", student.recognition])
                    continue
                for course in sorted(student.courses.values(), key=lambda item: item.name.lower()):
                    if not course.grades:
                        writer.writerow(
                            [student.student_id, student.name, course.name, "", "", "", "0.0", f"{student.overall_average:.1f}", f"{student.gpa:.2f}", student.recognition]
                        )
                    for grade in course.grades:
                        writer.writerow(
                            [
                                student.student_id,
                                student.name,
                                course.name,
                                grade.assignment,
                                f"{grade.score:.1f}",
                                grade.letter,
                                f"{course.average:.1f}",
                                f"{student.overall_average:.1f}",
                                f"{student.gpa:.2f}",
                                student.recognition,
                            ]
                        )

    def summary(self) -> dict[str, int | float]:
        courses = [course for student in self.students.values() for course in student.courses.values()]
        grades = [grade for course in courses for grade in course.grades]
        return {
            "students": len(self.students),
            "courses": len(courses),
            "grades": len(grades),
            "average": sum(grade.score for grade in grades) / len(grades) if grades else 0.0,
            "honors": sum(1 for student in self.students.values() if student.recognition in {"Dean's List", "Honor Roll"}),
        }

    def _get_student(self, student_id: str) -> Student:
        try:
            return self.students[student_id]
        except KeyError as error:
            raise ValueError("Student was not found.") from error

    def _get_course(self, student_id: str, course_name: str) -> Course:
        student = self._get_student(student_id)
        try:
            return student.courses[course_name]
        except KeyError as error:
            raise ValueError("Course was not found.") from error

    @staticmethod
    def _validate_grade_index(course: Course, grade_index: int) -> None:
        if not 0 <= grade_index < len(course.grades):
            raise ValueError("Grade was not found.")
