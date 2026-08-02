"""Domain models for the Student Grade Tracker."""

from __future__ import annotations

from dataclasses import dataclass, field
from statistics import mean


def score_to_letter(score: float) -> str:
    """Convert a numeric percentage to a standard letter grade."""
    if score >= 90:
        return "A"
    if score >= 80:
        return "B"
    if score >= 70:
        return "C"
    if score >= 60:
        return "D"
    return "F"


@dataclass
class Grade:
    """Represents one assignment and its percentage score."""

    assignment: str
    score: float

    def __post_init__(self) -> None:
        self.assignment = self.assignment.strip()
        if not self.assignment:
            raise ValueError("Assignment name is required.")
        if not 0 <= self.score <= 100:
            raise ValueError("Score must be between 0 and 100.")

    @property
    def letter(self) -> str:
        return score_to_letter(self.score)


@dataclass
class Course:
    """Represents a course containing a collection of grades."""

    name: str
    grades: list[Grade] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.name = self.name.strip()
        if not self.name:
            raise ValueError("Course name is required.")

    def add_grade(self, assignment: str, score: float) -> None:
        self.grades.append(Grade(assignment, score))

    def update_grade(self, index: int, assignment: str, score: float) -> None:
        self.grades[index] = Grade(assignment, score)

    def delete_grade(self, index: int) -> None:
        del self.grades[index]

    @property
    def average(self) -> float:
        return mean(grade.score for grade in self.grades) if self.grades else 0.0

    @property
    def letter_grade(self) -> str:
        return score_to_letter(self.average) if self.grades else "N/A"


@dataclass
class Student:
    """Represents a student and the courses assigned to that student."""

    student_id: str
    name: str
    courses: dict[str, Course] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.student_id = self.student_id.strip()
        self.name = self.name.strip()
        if not self.student_id or not self.name:
            raise ValueError("Student ID and name are required.")

    def add_course(self, course_name: str) -> None:
        course_name = course_name.strip()
        if not course_name:
            raise ValueError("Course name is required.")
        if course_name in self.courses:
            raise ValueError("That course already exists for this student.")
        self.courses[course_name] = Course(course_name)

    def delete_course(self, course_name: str) -> None:
        if course_name not in self.courses:
            raise ValueError("Course was not found.")
        del self.courses[course_name]

    @property
    def overall_average(self) -> float:
        active_courses = [course.average for course in self.courses.values() if course.grades]
        return mean(active_courses) if active_courses else 0.0

    @property
    def gpa(self) -> float:
        """Return an estimated 4.0-scale GPA based on course averages."""
        points = {"A": 4.0, "B": 3.0, "C": 2.0, "D": 1.0, "F": 0.0}
        active_courses = [course for course in self.courses.values() if course.grades]
        if not active_courses:
            return 0.0
        return mean(points[score_to_letter(course.average)] for course in active_courses)

    @property
    def recognition(self) -> str:
        """Return an academic recognition label based on overall average."""
        if not any(course.grades for course in self.courses.values()):
            return "No Grades"
        if self.overall_average >= 90:
            return "Dean's List"
        if self.overall_average >= 80:
            return "Honor Roll"
        return "Good Standing"
