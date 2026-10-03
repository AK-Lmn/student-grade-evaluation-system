import os
import tablib

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


def validate_section(section):
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
