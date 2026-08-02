"""Automated tests for the Student Grade Tracker."""

from __future__ import annotations

import csv
import tempfile
import unittest
from pathlib import Path

from grade_tracker import GradeTracker
from models import Course, Grade, Student, score_to_letter


class ModelTests(unittest.TestCase):
    def test_score_to_letter(self) -> None:
        self.assertEqual(score_to_letter(100), "A")
        self.assertEqual(score_to_letter(89.9), "B")
        self.assertEqual(score_to_letter(70), "C")
        self.assertEqual(score_to_letter(60), "D")
        self.assertEqual(score_to_letter(59.9), "F")

    def test_grade_validation(self) -> None:
        self.assertEqual(Grade("Quiz", 91).letter, "A")
        with self.assertRaises(ValueError):
            Grade("", 90)
        with self.assertRaises(ValueError):
            Grade("Quiz", 101)

    def test_course_average_and_update(self) -> None:
        course = Course("Python")
        course.add_grade("Quiz", 80)
        course.add_grade("Project", 100)
        self.assertEqual(course.average, 90)
        self.assertEqual(course.letter_grade, "A")
        course.update_grade(0, "Quiz", 90)
        self.assertEqual(course.average, 95)
        course.delete_grade(1)
        self.assertEqual(len(course.grades), 1)

    def test_student_overall_average(self) -> None:
        student = Student("1", "Alex")
        student.add_course("Python")
        student.add_course("Database")
        student.courses["Python"].add_grade("Quiz", 80)
        student.courses["Database"].add_grade("Lab", 100)
        self.assertEqual(student.overall_average, 90)



    def test_gpa_and_recognition(self):
        student = Student("S200", "Jordan Lee")
        student.add_course("Python")
        student.courses["Python"].add_grade("Final", 95)
        self.assertEqual(student.gpa, 4.0)
        self.assertEqual(student.recognition, "Dean's List")

class GradeTrackerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_directory = tempfile.TemporaryDirectory()
        self.data_file = Path(self.temp_directory.name) / "students.json"
        self.tracker = GradeTracker(self.data_file)

    def tearDown(self) -> None:
        self.temp_directory.cleanup()

    def test_full_crud_and_persistence(self) -> None:
        self.tracker.add_student("100", "Madison")
        self.tracker.add_course("100", "Python")
        self.tracker.add_grade("100", "Python", "Final", 96)
        self.tracker.update_student("100", "Madison D.")
        self.tracker.update_grade("100", "Python", 0, "Final Project", 98)

        reloaded = GradeTracker(self.data_file)
        self.assertEqual(reloaded.students["100"].name, "Madison D.")
        grade = reloaded.students["100"].courses["Python"].grades[0]
        self.assertEqual(grade.assignment, "Final Project")
        self.assertEqual(grade.score, 98)

        reloaded.delete_grade("100", "Python", 0)
        reloaded.delete_course("100", "Python")
        reloaded.delete_student("100")
        self.assertEqual(reloaded.students, {})

    def test_duplicate_validation(self) -> None:
        self.tracker.add_student("100", "Alex")
        with self.assertRaises(ValueError):
            self.tracker.add_student("100", "Jordan")
        self.tracker.add_course("100", "Python")
        with self.assertRaises(ValueError):
            self.tracker.add_course("100", "Python")

    def test_search_and_summary(self) -> None:
        self.tracker.add_student("100", "Alex Johnson")
        self.tracker.add_student("200", "Jordan Lee")
        self.tracker.add_course("100", "Python")
        self.tracker.add_grade("100", "Python", "Quiz", 90)
        self.assertEqual([student.student_id for student in self.tracker.search_students("alex")], ["100"])
        self.assertEqual([student.student_id for student in self.tracker.search_students("200")], ["200"])
        summary = self.tracker.summary()
        self.assertEqual(summary["students"], 2)
        self.assertEqual(summary["courses"], 1)
        self.assertEqual(summary["grades"], 1)
        self.assertEqual(summary["average"], 90)

    def test_csv_export(self) -> None:
        self.tracker.add_student("100", "Alex")
        self.tracker.add_course("100", "Python")
        self.tracker.add_grade("100", "Python", "Quiz", 93)
        report_path = Path(self.temp_directory.name) / "report.csv"
        self.tracker.export_csv(report_path)
        with report_path.open(newline="", encoding="utf-8") as report:
            rows = list(csv.reader(report))
        self.assertEqual(rows[0][0], "Student ID")
        self.assertEqual(rows[1][0], "100")
        self.assertEqual(rows[1][5], "A")


if __name__ == "__main__":
    unittest.main()
