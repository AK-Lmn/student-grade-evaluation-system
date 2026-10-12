import os
import tablib
import algorithms

dict_student = {}
dict_grades = {}
subjects = ["PROGRAMMING", "DISCRETE", "STATISTICS"]

students_dataset = tablib.Dataset()
students_dataset.headers = ['Student Number', 'Name', 'Section']

grades_dataset = tablib.Dataset()
grades_dataset.headers = ['Student Number', 'Name', 'Section', 'Subject', 'PRELIM', 'MIDTERM', 'PREFINAL', 'FINAL',
                          'SUBJECT_FINAL_GRADE', 'REMARKS', 'FINAL_AVERAGE']


def save_to_files():
    if os.path.exists('students.csv'):
        os.remove('students.csv')

    with open('students.csv', 'w', newline='') as f:
        f.write(students_dataset.export('csv'))

    if os.path.exists('grades.csv'):
        os.remove('grades.csv')

    with open('grades.csv', 'w', newline='') as f:
        f.write(grades_dataset.export('csv'))


def load_from_files():
    global students_dataset, grades_dataset, dict_student, dict_grades

    if os.path.exists('students.csv'):
        with open('students.csv', 'r') as f:
            students_dataset = tablib.Dataset().load(f.read(), format='csv')

            dict_student.clear()
            for row in students_dataset:
                student_num = str(row[0])
                dict_student[student_num] = {
                    "name": row[1],
                    "section": row[2]
                }

    if os.path.exists('grades.csv'):
        try:
            with open('grades.csv', 'r') as f:
                content = f.read()
                if content.strip():
                    loaded_dataset = tablib.Dataset().load(content, format='csv')

                    if loaded_dataset.headers and len(loaded_dataset.headers) == 11:
                        grades_dataset = loaded_dataset
                    else:
                        grades_dataset = tablib.Dataset()
                        grades_dataset.headers = ['Student Number', 'Name', 'Section', 'Subject', 'PRELIM', 'MIDTERM',
                                                  'PREFINAL', 'FINAL', 'SUBJECT_FINAL_GRADE', 'REMARKS',
                                                  'FINAL_AVERAGE']
                        os.remove('grades.csv')
                        return
                else:
                    grades_dataset = tablib.Dataset()
                    grades_dataset.headers = ['Student Number', 'Name', 'Section', 'Subject', 'PRELIM', 'MIDTERM',
                                              'PREFINAL', 'FINAL', 'SUBJECT_FINAL_GRADE', 'REMARKS', 'FINAL_AVERAGE']
                    return

                dict_grades.clear()
                current_student = None
                for row in grades_dataset:
                    student_num = str(row[0])
                    subject = row[3]

                    if student_num != current_student:
                        dict_grades[student_num] = {
                            'name': row[1],
                            'section': row[2],
                            'final_average': float(row[10]) if row[10] else 0,
                            'remarks': "PASSED" if (row[10] and float(row[10]) >= 75) else "FAILED"
                        }
                        current_student = student_num

                    dict_grades[student_num][subject] = {
                        'prelim': float(row[4]) if row[4] else 0,
                        'midterm': float(row[5]) if row[5] else 0,
                        'prefinal': float(row[6]) if row[6] else 0,
                        'final': float(row[7]) if row[7] else 0
                    }
        except Exception:
            grades_dataset = tablib.Dataset()
            grades_dataset.headers = ['Student Number', 'Name', 'Section', 'Subject', 'PRELIM', 'MIDTERM',
                                      'PREFINAL', 'FINAL', 'SUBJECT_FINAL_GRADE', 'REMARKS', 'FINAL_AVERAGE']
            if os.path.exists('grades.csv'):
                os.remove('grades.csv')


def validate_student_number(student_num):
    student_num = str(student_num).strip()
    if not student_num.isdigit():
        return False, "Student Number must contain digits only."
    if len(student_num) != 6:
        return False, "Student Number must be exactly 6 digits (e.g., 100001)."
    return True, ""


def validate_section(section):
    section = str(section).strip().upper()
    if len(section) != 9 or section[4] != "-":
        return False

    if (section[:4].isalpha() and
            section[5:7].isdigit() and
            section[7].isalpha() and
            section[8].isdigit()):
        return True

    if (section[:3].isalpha() and
            section[3].isdigit() and
            section[5:7].isdigit() and
            section[7].isalpha() and
            section[8].isdigit()):
        return True

    return False


def validate_name_format(name):
    if len(name) > 50:
        return False, "Name cannot exceed 50 characters."

    if ',' not in name:
        return False, "Name must be in format: SURNAME, FIRSTNAME M.I."

    parts = name.split(',')
    if len(parts) != 2:
        return False, "Name must be in format: SURNAME, FIRSTNAME M.I."

    surname = parts[0].strip()
    given_names = parts[1].strip()

    if not surname or not given_names:
        return False, "Both surname and given names are required."

    if not all(char.isalpha() or char.isspace() or char in ".," for char in name):
        return False, "Name can only contain letters, spaces, commas, and periods."

    return True, ""


def store_student(name, student_num, section):
    student_num = str(student_num).strip()
    dict_student[student_num] = {
        "name": name.upper().strip(),
        "section": section.upper().strip()
    }

    students_dataset.append([student_num, name.upper().strip(), section.upper().strip()])
    save_to_files()
    return dict_student[student_num]


def validate_grade(val):
    try:
        val_str = str(val).strip()
        score = float(val_str)
        if 0.0 <= score <= 100.0:
            return True, round(score, 2)
        return False, "Grade must be between 0 and 100."
    except (ValueError, TypeError):
        return False, "Grade must be a valid number."


def save_student_grades(student_num, subject_scores):
    """
    Save or update grades for a student across all subjects.
    subject_scores format:
    {
        'PROGRAMMING': {'prelim': 85.0, 'midterm': 88.0, 'prefinal': 90.0, 'final': 92.0},
        ...
    }
    """
    global grades_dataset
    student_num = str(student_num).strip()
    if student_num not in dict_student:
        return False, f"Student number '{student_num}' is not registered."

    s_name = dict_student[student_num]["name"]
    s_sec = dict_student[student_num]["section"]

    if student_num not in dict_grades:
        dict_grades[student_num] = {
            'name': s_name,
            'section': s_sec,
            'final_average': 0.0,
            'remarks': 'FAILED'
        }
    else:
        dict_grades[student_num]['name'] = s_name
        dict_grades[student_num]['section'] = s_sec

    for subj in subjects:
        if subj in subject_scores:
            scores = subject_scores[subj]
            dict_grades[student_num][subj] = {
                'prelim': float(scores.get('prelim', 0.0)),
                'midterm': float(scores.get('midterm', 0.0)),
                'prefinal': float(scores.get('prefinal', 0.0)),
                'final': float(scores.get('final', 0.0))
            }

    final_avg = algorithms.calculate_final_average(dict_grades[student_num], subjects)
    dict_grades[student_num]['final_average'] = round(final_avg, 2)
    dict_grades[student_num]['remarks'] = "PASSED" if final_avg >= 75 else "FAILED"

    # Rebuild grades_dataset to keep everything consistent
    new_dataset = tablib.Dataset()
    new_dataset.headers = ['Student Number', 'Name', 'Section', 'Subject', 'PRELIM', 'MIDTERM',
                           'PREFINAL', 'FINAL', 'SUBJECT_FINAL_GRADE', 'REMARKS', 'FINAL_AVERAGE']

    for s_id, s_info in dict_grades.items():
        name = s_info.get('name', '')
        section = s_info.get('section', '')
        avg = s_info.get('final_average', 0.0)
        for subj in subjects:
            if subj in s_info and isinstance(s_info[subj], dict):
                q = s_info[subj]
                p = q.get('prelim', 0.0)
                m = q.get('midterm', 0.0)
                pf = q.get('prefinal', 0.0)
                f = q.get('final', 0.0)
                subj_final = round(algorithms.calculate_final_subject_grade(s_info, subj), 2)
                subj_remarks = "PASSED" if subj_final >= 75 else "FAILED"
                new_dataset.append([
                    s_id, name, section, subj,
                    p, m, pf, f,
                    subj_final, subj_remarks, avg
                ])

    grades_dataset = new_dataset
    save_to_files()
    return True, "Grades successfully saved!"
