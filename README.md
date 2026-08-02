# Student Grade Tracker

**SDEV 220 Final Project**  
**Author:** Madison Dowden

The Student Grade Tracker is a desktop Python system designed for a small school, tutoring center, or employee-training organization. It gives staff one place to maintain student records, courses, assignments, scores, averages, and printable grade-report data.

## Major Features

- Add, update, search, and delete students
- Add and delete courses for an individual student
- Add, update, and delete assignment grades
- Validate required fields and scores from 0 through 100
- Calculate letter grades, course averages, student averages, a class average, and an estimated 4.0 GPA
- Recognize Dean's List and Honor Roll students automatically
- Sort students by name, average, or GPA
- Save records automatically to a JSON file
- Export a detailed CSV report
- Display dashboard totals for students, courses, grades, and class average
- Confirm destructive operations before deleting data
- Run without third-party Python packages

## Object-Oriented Design

The project uses five primary classes:

1. `Grade` stores one assignment name and score.
2. `Course` stores a list of `Grade` objects and calculates a course average.
3. `Student` stores identifying information and a dictionary of courses.
4. `GradeTracker` handles business rules, searching, persistence, and CSV reporting.
5. `GradeTrackerApp` creates and controls the Tkinter graphical interface.

## Collections Used

- A **dictionary** stores all students by student ID.
- A **dictionary** stores each student's courses by course name.
- A **list** stores the grades in each course.
- Lists are also used for search results, averages, and report generation.

## Project Structure

```text
SDEV220-Student-Grade-Tracker/
├── app.py                  # Tkinter graphical interface
├── grade_tracker.py        # Business logic, saving, search, and reports
├── models.py               # Grade, Course, and Student classes
├── main.py                 # Program entry point
├── run_app.bat             # Windows double-click launcher
├── requirements.txt        # Dependency information
├── data/
│   └── students.json       # Sample and saved application data
├── docs/
│   ├── Class_Diagram.md
│   ├── Project_Proposal.md
│   ├── Project_Report.md
│   ├── Sample_Output.md
│   └── Test_Plan.md
└── tests/
    └── test_grade_tracker.py
```

## Requirements

- Python 3.10 or newer
- Tkinter (included with the normal Windows Python installer)

No third-party packages are required.

## Running the Application

Open the project folder in VS Code and run:

```powershell
py main.py
```

You can also double-click `run_app.bat` on Windows.

## Running the Automated Tests

From the project folder, run:

```powershell
py -m unittest discover -s tests -v
```

## Basic Use

1. Add a student using a unique student ID and name.
2. Select the student in the left table.
3. Add a course.
4. Enter an assignment and score, then add the grade.
5. Select an existing grade to update or delete it.
6. Use the search box to filter the student list.
7. Select **File → Export CSV Report** to create a spreadsheet-compatible report.

## Data Storage

Records are saved automatically in `data/students.json`. The application uses a temporary file during saving and then replaces the existing file, reducing the chance of a partially written data file.

## Documentation

The `docs` folder contains the project proposal, full report, class diagram, test plan, and sample output description.
