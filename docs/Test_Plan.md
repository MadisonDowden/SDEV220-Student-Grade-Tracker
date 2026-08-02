# Test Plan

## Automated Testing

Run the automated test suite with:

```powershell
py -m unittest discover -s tests -v
```

The tests verify:

- Numeric-to-letter conversion
- Grade score validation
- Course average calculations
- Student overall averages
- Student, course, and grade creation
- Student and grade updates
- Delete operations
- Student searching
- JSON save and reload
- Summary statistics
- CSV report generation

## Manual GUI Tests

| ID | Action | Expected Result |
|---|---|---|
| M01 | Start `main.py` | Main window opens without an error |
| M02 | Add a unique student ID and name | Student appears in the list and totals update |
| M03 | Add a duplicate student ID | Error message appears and duplicate is not added |
| M04 | Select a student and update the name | New name appears and remains after restart |
| M05 | Search by part of a name | Only matching students appear |
| M06 | Add a course | Course appears with “No grades yet” |
| M07 | Add a score from 0–100 | Grade, letter, and averages appear |
| M08 | Enter text for the score | Friendly error message appears |
| M09 | Update an existing grade | Score, letter, and averages change |
| M10 | Delete a grade, course, or student | Confirmation appears before deletion |
| M11 | Close and reopen the program | Saved records reload from JSON |
| M12 | Export the CSV report | CSV file opens with headings and data |

## Test Result

All Python files compile successfully. The automated tests pass using Python's built-in `unittest` framework.
