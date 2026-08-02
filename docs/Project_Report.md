# Student Grade Tracker Project Report

## Student
Madison Dowden

## Executive Summary

The Student Grade Tracker is a complete Python desktop application developed for a small educational organization. It replaces handwritten grade records and disconnected spreadsheets with a searchable system that stores students, courses, assignments, and scores in one location.

## Problem Statement

Teachers, tutors, and training staff need to record student performance accurately. Manual calculations can introduce errors, and separate spreadsheets can make records difficult to locate or maintain. The system solves this problem by calculating results automatically and saving all data in a consistent format.

## Functional Requirements

The completed system can:

- Create, update, search, and delete student records
- Create and delete courses
- Create, update, and delete grades
- Calculate letter grades and averages
- Display summary statistics
- Save and reload data automatically
- Export a CSV report
- Validate incorrect and missing input

## Object-Oriented Design

The program separates responsibilities into related classes:

- `Grade` validates an assignment and score and determines a letter grade.
- `Course` owns a list of grades and calculates its average.
- `Student` owns a dictionary of courses and calculates an overall average.
- `GradeTracker` manages records, persistence, searching, summary statistics, and CSV reports.
- `GradeTrackerApp` presents the graphical interface and responds to user actions.

This design keeps interface code separate from reusable business logic.

## Collections

The project uses dictionaries and lists throughout the system. Student IDs are dictionary keys, course names are dictionary keys, and each course contains a list of `Grade` objects. Lists are also used when filtering students and calculating averages.

## Data Persistence

The application writes data to `data/students.json` after every change. JSON was selected because it is human-readable and supported by Python's standard library. Saving uses a temporary file followed by replacement of the original file to reduce the risk of partial data.

## Error Handling and Validation

The program handles missing names, missing IDs, duplicate IDs, duplicate courses, invalid selections, missing assignments, nonnumeric scores, scores outside 0–100, missing records, malformed JSON, and file export errors. The GUI displays understandable message boxes rather than raw exceptions.

## Testing

Automated unit tests cover model validation, grade conversion, average calculations, CRUD operations, searching, persistence, summary statistics, and CSV export. A manual GUI test plan is also included. The application modules compile successfully and the automated test suite passes.

## Version Control

Git and GitHub are used to store the source code and documentation. This provides a history of changes and gives the instructor one repository URL for reviewing and testing the project.

## Conclusion

The final system satisfies the assignment by providing a working Python application, more than three classes, lists and dictionaries, a graphical user interface, documentation, file persistence, validation, calculations, reporting, and testing.


## Final Enhancements

The completed system also calculates an estimated 4.0-scale GPA, assigns Dean's List or Honor Roll recognition, allows users to sort student records by name, average, or GPA, and includes those results in exported CSV reports.
