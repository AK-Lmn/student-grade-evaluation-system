import tablib
import os

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
                student_num = row[0]
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
                        print("Warning: grades.csv has incorrect format. Resetting grades dataset.")
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
                    student_num = row[0]
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
        except Exception as e:
            print(f"Error loading grades.csv: {e}. Starting with fresh grades dataset.")
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


def validate_grade_input(prompt):
    while True:
        try:
            grade = float(input(prompt))
            if grade < 65 or grade > 100:
                print("Error: Grade must be between 65 and 100.")
                continue
            return grade
        except ValueError:
            print("Error: Please enter a valid number.")


def store_student(name, student_num, section):
    dict_student[student_num] = {
        "name": name.upper(),
        "section": section.upper()
    }

    students_dataset.append([student_num, name.upper(), section.upper()])
    save_to_files()

    return dict_student[student_num]


def view_all_students_by_section():
    if not dict_student:
        print("No registered students yet.")
        return

    print("\n" + "=" * 60)
    print("ALL STUDENTS BY SECTION")
    print("=" * 60)

    sections_dict = {}
    for student_num, info in dict_student.items():
        section = info['section']
        if section not in sections_dict:
            sections_dict[section] = []
        sections_dict[section].append((info['name'], student_num))

    for section, students in sorted(sections_dict.items()):
        print(f"\n{section} SECTION:")
        print("-" * 50)
        print(f"{'No.':<4} {'NAME':<30} {'STUDENT NUMBER':<15}")
        print("-" * 50)

        for i, (name, student_num) in enumerate(sorted(students, key=lambda x: x[0]), 1):
            print(f"{i:<4} {name:<30} {student_num:<15}")

        print(f"Total in {section}: {len(students)} students")


def view_section_students():
    if not dict_student:
        print("No registered students yet.")
        return

    section = input("Enter section to view (e.g., BSCS-12M1): ").upper()

    section_students = []
    for row in students_dataset:
        if row[2] == section:
            section_students.append((row[1], row[0]))

    if not section_students:
        print(f"No students found in section {section}.")
        return

    print(f"\n{section} SECTION:")
    print("-" * 50)
    print(f"{'No.':<4} {'NAME':<30} {'STUDENT NUMBER':<15}")
    print("-" * 50)

    for i, (name, student_num) in enumerate(sorted(section_students, key=lambda x: x[0]), 1):
        print(f"{i:<4} {name:<30} {student_num:<15}")

    print(f"Total: {len(section_students)} students")


def calculate_quarter_average(grades, quarter):
    total = 0
    count = 0

    for subject in subjects:
        if subject in grades and quarter in grades[subject]:
            total += grades[subject][quarter]
            count += 1

    return total / count if count > 0 else 0


def calculate_final_subject_grade(grades, subject):
    if subject in grades:
        subj_grades = grades[subject]
        if all(quarter in subj_grades for quarter in ['prelim', 'midterm', 'prefinal', 'final']):
            final_grade = (subj_grades['prelim'] * 0.20 +
                           subj_grades['midterm'] * 0.25 +
                           subj_grades['prefinal'] * 0.25 +
                           subj_grades['final'] * 0.30)
            return final_grade
    return 0


def calculate_final_average(grades):
    subject_final_grades = []

    for subject in subjects:
        if subject in grades:
            final_grade = calculate_final_subject_grade(grades, subject)
            if final_grade > 0:
                subject_final_grades.append(final_grade)

    return sum(subject_final_grades) / len(subject_final_grades) if subject_final_grades else 0


def view_specific_student_grades():
    if not dict_student:
        print("No registered students yet.")
        return

    student_num = input("Enter student number: ")

    if student_num not in dict_student:
        print("Student not found!")
        return

    student_info = dict_student[student_num]
    student_name = student_info['name']

    if student_num not in dict_grades:
        print(f"\nNo grades recorded yet for {student_name}.")
        return

    grades = dict_grades[student_num]

    print("\n" + "=" * 80)
    print(f"GRADE REPORT FOR: {student_name}")
    print(f"Section: {student_info['section']}")
    print("=" * 80)

    print(f"\n{'SUBJECT':<15} {'PRELIM':<10} {'MIDTERM':<10} {'PREFINAL':<12} {'FINAL':<10} {'FINAL GRADE':<12}")
    print("-" * 80)

    for subject in subjects:
        if subject in grades:
            subj_grades = grades[subject]
            final_grade = calculate_final_subject_grade(grades, subject)

            print(f"{subject:<15} "
                  f"{subj_grades.get('prelim', 0):<10.1f} "
                  f"{subj_grades.get('midterm', 0):<10.1f} "
                  f"{subj_grades.get('prefinal', 0):<12.1f} "
                  f"{subj_grades.get('final', 0):<10.1f} "
                  f"{final_grade:<12.2f}")

    if 'final_average' in grades:
        print("\n" + "-" * 80)
        print(f"OVERALL FINAL GRADE AVERAGE: {grades['final_average']:.2f}")
        print(f"FINAL REMARKS: {grades['remarks']}")
        print("-" * 80)


def view_section_grades():
    if not dict_student:
        print("No registered students yet.")
        return

    section = input("Enter section to view grades (e.g., BSCS-12M1): ").upper()

    section_students = []
    for student_num, info in dict_student.items():
        if info['section'] == section:
            section_students.append((info['name'], student_num))

    if not section_students:
        print(f"No students found in section {section}.")
        return

    print(f"\n{'=' * 80}")
    print(f"GRADES FOR SECTION: {section}")
    print(f"{'=' * 80}")

    for name, student_num in sorted(section_students, key=lambda x: x[0]):
        print(f"\n{name} ({student_num}):")
        print("-" * 70)

        if student_num in dict_grades:
            grades = dict_grades[student_num]

            print(f"{'SUBJECT':<15} {'PRELIM':<10} {'MIDTERM':<10} {'PREFINAL':<12} {'FINAL':<10} {'FINAL GRADE':<12}")
            print("-" * 70)

            for subject in subjects:
                if subject in grades:
                    subj_grades = grades[subject]
                    final_grade = calculate_final_subject_grade(grades, subject)

                    print(f"{subject:<15} "
                          f"{subj_grades.get('prelim', 0):<10.1f} "
                          f"{subj_grades.get('midterm', 0):<10.1f} "
                          f"{subj_grades.get('prefinal', 0):<12.1f} "
                          f"{subj_grades.get('final', 0):<10.1f} "
                          f"{final_grade:<12.2f}")

            if 'final_average' in grades:
                print(f"\nFINAL AVERAGE: {grades['final_average']:.2f} | REMARKS: {grades['remarks']}")
        else:
            print("No grades recorded yet.")


def rank_students_by_section():
    if not dict_grades:
        print("No grades recorded yet.")
        return

    section = input("Enter section to rank (e.g., BSCS-12M1): ").upper()

    student_list = []
    for s_num, g_data in dict_grades.items():
        if g_data['section'] == section:
            student_list.append({
                "student_number": s_num,
                "name": g_data['name'],
                "final_average": g_data['final_average'],
                "remarks": g_data['remarks']
            })

    if not student_list:
        print(f"No grade records found for section {section}.")
        return

    n = len(student_list)
    for i in range(n - 1):
        for j in range(0, n - i - 1):
            if student_list[j]['final_average'] < student_list[j + 1]['final_average']:
                student_list[j], student_list[j + 1] = student_list[j + 1], student_list[j]

    print("\n" + "=" * 65)
    print(f"CLASS RANKING - SECTION: {section}")
    print("=" * 65)
    print(f"{'RANK':<6} {'STUDENT NO.':<15} {'NAME':<25} {'AVERAGE':<10} {'REMARKS'}")
    print("-" * 65)

    for rank, student in enumerate(student_list, 1):
        print(f"{rank:<6} {student['student_number']:<15} {student['name']:<25} "
              f"{student['final_average']:<10.2f} {student['remarks']}")
    print("-" * 65)


def view_student_records_menu():
    while True:
        print("\n" + "=" * 50)
        print("VIEW STUDENT RECORDS")
        print("=" * 50)
        print("1. View all students by section")
        print("2. View students in a specific section")
        print("3. View specific student's grades")
        print("4. View grades of all students in a section")
        print("5. Rank students by section")
        print("6. Return to main menu")

        try:
            choice = int(input("\nEnter choice: "))
        except ValueError:
            print("Invalid input. Please enter a number.")
            continue

        if choice == 1:
            view_all_students_by_section()
            input("\nPress Enter to continue...")

        elif choice == 2:
            view_section_students()
            input("\nPress Enter to continue...")

        elif choice == 3:
            view_specific_student_grades()
            input("\nPress Enter to continue...")

        elif choice == 4:
            view_section_grades()
            input("\nPress Enter to continue...")

        elif choice == 5:
            rank_students_by_section()
            input("\nPress Enter to continue...")

        elif choice == 6:
            break

        else:
            print("Invalid choice. Please select 1-6.")


def compute_quarter_grades():
    if not dict_student:
        print("No registered students yet. Please register students first.")
        input("Press Enter to return to main menu...")
        return

    print("\n" + "=" * 50)
    print("TEACHER'S LOG - GRADE COMPUTATION BY QUARTER")
    print("=" * 50)

    while True:
        print("\nREGISTERED STUDENTS (Organized by Section):")
        print("-" * 60)

        sections_dict = {}
        for student_num, info in dict_student.items():
            section = info['section']
            if section not in sections_dict:
                sections_dict[section] = []
            sections_dict[section].append((info['name'], student_num))

        for section, students in sorted(sections_dict.items()):
            print(f"\n{section} SECTION:")
            for name, student_num in sorted(students, key=lambda x: x[0]):
                print(f"  {name} - {student_num}")

        print("\n" + "-" * 60)
        print("\nSelect student to compute grades:")
        print("1. Enter student number")
        print("2. Return to main menu")

        try:
            choice = int(input("\nEnter choice: "))
        except ValueError:
            print("Invalid input. Please enter a number.")
            continue

        if choice == 2:
            break

        elif choice == 1:
            student_num = input("Enter student number: ")

            if student_num not in dict_student:
                print("Student not found. Please enter a registered student number.")
                continue

            student_name = dict_student[student_num]['name']

            print(f"\nComputing grades for: {student_name}")
            print("-" * 40)

            print("\nSelect QUARTER to compute:")
            print("1. PRELIM Quarter")
            print("2. MIDTERM Quarter")
            print("3. PREFINAL Quarter")
            print("4. FINAL Quarter")
            print("5. Return to student selection")

            try:
                quarter_choice = int(input("\nEnter choice: "))
            except ValueError:
                print("Invalid input. Please enter a number.")
                continue

            if quarter_choice == 5:
                continue

            quarter_map = {1: 'prelim', 2: 'midterm', 3: 'prefinal', 4: 'final'}
            if quarter_choice not in quarter_map:
                print("Invalid choice.")
                continue

            quarter = quarter_map[quarter_choice]

            student_grades = {}
            if student_num in dict_grades:
                student_grades = dict_grades[student_num].copy()
                for subject in subjects:
                    if subject in student_grades:
                        student_grades[subject] = student_grades[subject].copy()
            else:
                student_grades = {
                    'name': student_name,
                    'section': dict_student[student_num]['section']
                }

            print(f"\nComputing {quarter.upper()} QUARTER grades:")
            print("-" * 30)

            if student_num in dict_grades:
                print("\nPREVIOUS GRADES (for reference):")
                print(f"{'SUBJECT':<15}", end='')

                quarters_to_show = []
                if quarter == 'midterm':
                    quarters_to_show = ['prelim']
                elif quarter == 'prefinal':
                    quarters_to_show = ['prelim', 'midterm']
                elif quarter == 'final':
                    quarters_to_show = ['prelim', 'midterm', 'prefinal']

                for q in quarters_to_show:
                    print(f"{q.upper():<10}", end='')
                print()
                print("-" * (15 + 10 * len(quarters_to_show)))

                for subject in subjects:
                    if subject in dict_grades[student_num]:
                        print(f"{subject:<15}", end='')
                        for q in quarters_to_show:
                            grade = dict_grades[student_num][subject].get(q, 0)
                            print(f"{grade:<10.1f}", end='')
                        print()
                print()

            print(f"Enter grades for all 3 subjects ({quarter.upper()} Quarter)")

            quarter_grades = {}
            for subject in subjects:
                print(f"\n{subject}:")
                grade = validate_grade_input(f"  Enter {quarter.upper()} grade (65-100): ")
                quarter_grades[subject] = grade

                if subject not in student_grades:
                    student_grades[subject] = {}

                student_grades[subject][quarter] = grade

            quarter_average = sum(quarter_grades.values()) / len(subjects)

            print(f"\n{'=' * 50}")
            print(f"{student_name}'s OVERALL {quarter.upper()} QUARTER AVERAGE: {quarter_average:.2f}")

            quarter_status = "PASSED" if quarter_average >= 75 else "FAILED"
            print(f"STATUS: {quarter_status}")
            print(f"{'=' * 50}")

            dict_grades[student_num] = student_grades

            for subject in subjects:
                if subject in student_grades:
                    subj_grades = student_grades[subject]

                    final_grade = 0
                    remarks = ""
                    if all(period in subj_grades for period in ['prelim', 'midterm', 'prefinal', 'final']):
                        final_grade = calculate_final_subject_grade(student_grades, subject)
                        remarks = "PASSED" if final_grade >= 75 else "FAILED"

                    found = False
                    for i, row in enumerate(grades_dataset):
                        if row[0] == student_num and row[3] == subject:
                            grades_dataset[i] = (
                                student_num,
                                student_name,
                                dict_student[student_num]['section'],
                                subject,
                                subj_grades.get('prelim', 0),
                                subj_grades.get('midterm', 0),
                                subj_grades.get('prefinal', 0),
                                subj_grades.get('final', 0),
                                round(final_grade, 2) if final_grade > 0 else 0,
                                remarks if remarks else "",
                                0
                            )
                            found = True
                            break

                    if not found:
                        grades_dataset.append([
                            student_num,
                            student_name,
                            dict_student[student_num]['section'],
                            subject,
                            subj_grades.get('prelim', 0),
                            subj_grades.get('midterm', 0),
                            subj_grades.get('prefinal', 0),
                            subj_grades.get('final', 0),
                            round(final_grade, 2) if final_grade > 0 else 0,
                            remarks if remarks else "",
                            0
                        ])

            final_avg = calculate_final_average(student_grades)
            if final_avg > 0:
                dict_grades[student_num]['final_average'] = round(final_avg, 2)
                dict_grades[student_num]['remarks'] = "PASSED" if final_avg >= 75 else "FAILED"

                for i, row in enumerate(grades_dataset):
                    if row[0] == student_num:
                        grades_dataset[i] = (
                            row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9],
                            round(final_avg, 2)
                        )

            save_to_files()

            print(f"\n" + "=" * 50)
            print(f"Grades computed successfully for {student_name}!")
            print("=" * 50)

            while True:
                print("\nWhat would you like to do next?")
                print("1. Compute more grades for another student/quarter")
                print("2. Edit this student's grades")
                print("3. Return to main menu")

                try:
                    next_choice = int(input("\nEnter choice: "))
                except ValueError:
                    print("Invalid input.")
                    continue

                if next_choice == 1:
                    break
                elif next_choice == 2:
                    edit_student_grades(student_num)
                    break
                elif next_choice == 3:
                    return
                else:
                    print("Invalid choice.")

            if next_choice == 1:
                continue
            elif next_choice == 3:
                break

        else:
            print("Invalid choice. Please select 1 or 2.")


def edit_student_grades(student_num=None):
    if not dict_student:
        print("No registered students yet.")
        return

    if student_num is None:
        print("\nREGISTERED STUDENTS (Organized by Section):")
        print("-" * 60)

        sections_dict = {}
        for num, info in dict_student.items():
            section = info['section']
            if section not in sections_dict:
                sections_dict[section] = []
            sections_dict[section].append((info['name'], num))

        for section, students in sorted(sections_dict.items()):
            print(f"\n{section} SECTION:")
            for name, num in sorted(students, key=lambda x: x[0]):
                print(f"  {name} - {num}")

        student_num = input("\nEnter student number to edit grades: ")

    if student_num not in dict_student:
        print("Student not found!")
        return

    if student_num not in dict_grades:
        print("No grades computed for this student yet.")
        return

    student_name = dict_student[student_num]['name']

    print(f"\n" + "=" * 60)
    print(f"EDITING GRADES FOR: {student_name}")
    print("=" * 60)

    while True:
        print("\nSelect QUARTER to edit:")
        print("1. PRELIM Quarter")
        print("2. MIDTERM Quarter")
        print("3. PREFINAL Quarter")
        print("4. FINAL Quarter")
        print("5. Show current grades and quarter averages")
        print("6. Return to previous menu")

        try:
            quarter_choice = int(input("\nEnter choice: "))
        except ValueError:
            print("Invalid input.")
            continue

        if quarter_choice == 6:
            break

        if quarter_choice == 5:
            if student_num in dict_grades:
                print(f"\nCurrent Grades for {student_name}:")
                print("-" * 85)

                grades = dict_grades[student_num]
                print(
                    f"{'SUBJECT':<15} {'PRELIM':<10} {'MIDTERM':<10} {'PREFINAL':<12} {'FINAL':<10} {'FINAL GRADE':<12}")
                print("-" * 70)

                for subject in subjects:
                    if subject in grades:
                        subj_grades = grades[subject]
                        final_grade = calculate_final_subject_grade(grades, subject)
                        print(f"{subject:<15} "
                              f"{subj_grades.get('prelim', 0):<10.1f} "
                              f"{subj_grades.get('midterm', 0):<10.1f} "
                              f"{subj_grades.get('prefinal', 0):<12.1f} "
                              f"{subj_grades.get('final', 0):<10.1f} "
                              f"{final_grade:<12.2f}")

                print("\nOVERALL QUARTER AVERAGES:")
                print(f"  PRELIM: {calculate_quarter_average(grades, 'prelim'):.2f}")
                print(f"  MIDTERM: {calculate_quarter_average(grades, 'midterm'):.2f}")
                print(f"  PREFINAL: {calculate_quarter_average(grades, 'prefinal'):.2f}")
                print(f"  FINAL: {calculate_quarter_average(grades, 'final'):.2f}")

                if 'final_average' in grades:
                    print(f"\nOVERALL FINAL GRADE AVERAGE: {grades['final_average']:.2f}")
                    print(f"FINAL REMARKS: {grades['remarks']}")
            continue

        if quarter_choice not in [1, 2, 3, 4]:
            print("Invalid choice.")
            continue

        quarter_map = {1: 'prelim', 2: 'midterm', 3: 'prefinal', 4: 'final'}
        quarter = quarter_map[quarter_choice]

        print(f"\nCURRENT {quarter.upper()} GRADES for {student_name}:")
        print("-" * 50)
        print(f"{'SUBJECT':<20} {'CURRENT GRADE':<15}")
        print("-" * 50)

        for subject in subjects:
            if subject in dict_grades[student_num]:
                current_grade = dict_grades[student_num][subject].get(quarter, 0)
                print(f"{subject:<20} {current_grade:<15.1f}")
        print()

        print(f"Editing {quarter.upper()} QUARTER grades:")
        print("1. Edit ALL subjects at once")

        for i, subject in enumerate(subjects, 2):
            print(f"{i}. Edit {subject} only")

        print(f"{len(subjects) + 2}. Back to quarter selection")

        try:
            edit_choice = int(input("\nEnter choice: "))
        except ValueError:
            print("Invalid input.")
            continue

        if edit_choice == len(subjects) + 2:
            continue

        if edit_choice == 1:
            print(f"\nEditing ALL {quarter.upper()} grades:")
            print("-" * 40)

            new_grades = {}
            for subject in subjects:
                current_grade = dict_grades[student_num][subject].get(quarter, 0)
                print(f"\n{subject} (Current: {current_grade:.1f})")
                new_grade = validate_grade_input(f"  Enter new {quarter} grade (65-100): ")
                new_grades[subject] = new_grade

            for subject, new_grade in new_grades.items():
                dict_grades[student_num][subject][quarter] = new_grade

                for i, row in enumerate(grades_dataset):
                    if row[0] == student_num and row[3] == subject:
                        old_prelim = float(row[4]) if row[4] else 0
                        old_midterm = float(row[5]) if row[5] else 0
                        old_prefinal = float(row[6]) if row[6] else 0
                        old_final = float(row[7]) if row[7] else 0

                        if quarter == 'prelim':
                            prelim, midterm, prefinal, final = new_grade, old_midterm, old_prefinal, old_final
                        elif quarter == 'midterm':
                            prelim, midterm, prefinal, final = old_prelim, new_grade, old_prefinal, old_final
                        elif quarter == 'prefinal':
                            prelim, midterm, prefinal, final = old_prelim, old_midterm, new_grade, old_final
                        elif quarter == 'final':
                            prelim, midterm, prefinal, final = old_prelim, old_midterm, old_prefinal, new_grade

                        final_grade_calc = 0
                        remarks_calc = ""
                        if all(grade > 0 for grade in [prelim, midterm, prefinal, final]):
                            final_grade_calc = (prelim * 0.20) + (midterm * 0.25) + (prefinal * 0.25) + (final * 0.30)
                            remarks_calc = "PASSED" if final_grade_calc >= 75 else "FAILED"

                        grades_dataset[i] = (
                            row[0], row[1], row[2], row[3],
                            prelim, midterm, prefinal, final,
                            round(final_grade_calc, 2) if final_grade_calc > 0 else 0,
                            remarks_calc if remarks_calc else "",
                            row[10] if len(row) > 10 else 0
                        )
                        break

            final_avg = calculate_final_average(dict_grades[student_num])
            dict_grades[student_num]['final_average'] = round(final_avg, 2)
            dict_grades[student_num]['remarks'] = "PASSED" if final_avg >= 75 else "FAILED"

            for i, row in enumerate(grades_dataset):
                if row[0] == student_num:
                    grades_dataset[i] = (
                        row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9],
                        round(final_avg, 2)
                    )

            quarter_avg = calculate_quarter_average(dict_grades[student_num], quarter)

            print(f"\n" + "=" * 50)
            print(f"All {quarter.upper()} grades updated successfully!")
            print(f"Updated OVERALL {quarter.upper()} QUARTER AVERAGE: {quarter_avg:.2f}")
            print(f"Updated OVERALL FINAL GRADE AVERAGE: {dict_grades[student_num]['final_average']:.2f}")
            print(f"Updated FINAL REMARKS: {dict_grades[student_num]['remarks']}")
            print("=" * 50)

        elif 2 <= edit_choice <= len(subjects) + 1:
            subject = subjects[edit_choice - 2]

            if subject not in dict_grades[student_num]:
                print(f"No grades recorded for {subject} yet.")
                continue

            current_grade = dict_grades[student_num][subject].get(quarter, 0)
            print(f"\nEditing {subject} - {quarter.upper()} (Current: {current_grade:.1f})")
            new_grade = validate_grade_input(f"Enter new {quarter} grade for {subject} (65-100): ")

            dict_grades[student_num][subject][quarter] = new_grade

            for i, row in enumerate(grades_dataset):
                if row[0] == student_num and row[3] == subject:
                    old_prelim = float(row[4]) if row[4] else 0
                    old_midterm = float(row[5]) if row[5] else 0
                    old_prefinal = float(row[6]) if row[6] else 0
                    old_final = float(row[7]) if row[7] else 0

                    if quarter == 'prelim':
                        prelim, midterm, prefinal, final = new_grade, old_midterm, old_prefinal, old_final
                    elif quarter == 'midterm':
                        prelim, midterm, prefinal, final = old_prelim, new_grade, old_prefinal, old_final
                    elif quarter == 'prefinal':
                        prelim, midterm, prefinal, final = old_prelim, old_midterm, new_grade, old_final
                    elif quarter == 'final':
                        prelim, midterm, prefinal, final = old_prelim, old_midterm, old_prefinal, new_grade

                    final_grade_calc = 0
                    remarks_calc = ""
                    if all(grade > 0 for grade in [prelim, midterm, prefinal, final]):
                        final_grade_calc = (prelim * 0.20) + (midterm * 0.25) + (prefinal * 0.25) + (final * 0.30)
                        remarks_calc = "PASSED" if final_grade_calc >= 75 else "FAILED"

                    grades_dataset[i] = (
                        row[0], row[1], row[2], row[3],
                        prelim, midterm, prefinal, final,
                        round(final_grade_calc, 2) if final_grade_calc > 0 else 0,
                        remarks_calc if remarks_calc else "",
                        row[10] if len(row) > 10 else 0
                    )
                    break

            final_avg = calculate_final_average(dict_grades[student_num])
            dict_grades[student_num]['final_average'] = round(final_avg, 2)
            dict_grades[student_num]['remarks'] = "PASSED" if final_avg >= 75 else "FAILED"

            for i, row in enumerate(grades_dataset):
                if row[0] == student_num:
                    grades_dataset[i] = (
                        row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9],
                        round(final_avg, 2)
                    )

            quarter_avg = calculate_quarter_average(dict_grades[student_num], quarter)

            print(f"\n" + "=" * 50)
            print(f"Grade updated successfully!")
            print(f"New {quarter} grade for {subject}: {new_grade}")
            print(f"Updated OVERALL {quarter.upper()} QUARTER AVERAGE: {quarter_avg:.2f}")
            print(f"Updated OVERALL FINAL GRADE AVERAGE: {dict_grades[student_num]['final_average']:.2f}")
            print(f"Updated FINAL REMARKS: {dict_grades[student_num]['remarks']}")
            print("=" * 50)
        else:
            print("Invalid choice.")
            continue

        confirm = input("\nSave these changes? (y/n): ").lower()
        if confirm == 'y':
            save_to_files()
            print("Changes saved successfully!")
        else:
            print("Changes discarded.")
            load_from_files()


def edit_student_info():
    if not dict_student:
        print("No registered students yet.")
        input("Press Enter to return to main menu...")
        return

    print("=" * 50)
    print("EDIT STUDENT INFORMATION")
    print("=" * 50)

    print("\nREGISTERED STUDENTS (Organized by Section):")
    print("-" * 60)

    sections_dict = {}
    for student_num, info in dict_student.items():
        section = info['section']
        if section not in sections_dict:
            sections_dict[section] = []
        sections_dict[section].append((info['name'], student_num))

    for section, students in sorted(sections_dict.items()):
        print(f"\n{section} SECTION:")
        for name, student_num in sorted(students, key=lambda x: x[0]):
            print(f"  {name} - {student_num}")

    student_num = input("\nEnter student number to edit: ")

    if student_num not in dict_student:
        print("Student not found!")
        input("Press Enter to return to main menu...")
        return

    current_info = dict_student[student_num]

    while True:
        print(f"\n" + "=" * 40)
        print(f"Editing: {current_info['name']}")
        print("=" * 40)
        print("1. Edit Name")
        print("2. Edit Section")
        print("3. Edit Student Number")
        print("4. Return to Main Menu")

        try:
            choice = int(input("\nSelect what to edit: "))
        except ValueError:
            print("Please enter a number.")
            continue

        if choice == 1:
            while True:
                new_name = input(f"Current name: {current_info['name']}\nEnter new name (SURNAME, FIRSTNAME M.I.): ")

                is_valid, error_msg = validate_name_format(new_name)
                if not is_valid:
                    print(error_msg)
                    continue

                if len(new_name) < 3 or len(new_name) > 50:
                    print("Name must be between 3 and 50 characters.")
                    continue

                dict_student[student_num]['name'] = new_name.upper()

                for i, row in enumerate(students_dataset):
                    if row[0] == student_num:
                        students_dataset[i][1] = new_name.upper()
                        break

                if student_num in dict_grades:
                    dict_grades[student_num]['name'] = new_name.upper()
                    for i, row in enumerate(grades_dataset):
                        if row[0] == student_num:
                            grades_dataset[i][1] = new_name.upper()

                print(f"Name updated to: {new_name.upper()}")
                current_info['name'] = new_name.upper()
                save_to_files()
                break

        elif choice == 2:
            while True:
                new_section = input(
                    f"Current section: {current_info['section']}\nEnter new section (format: ABCD-12A3 or BSE1-12A3): ").upper()

                if validate_section(new_section):
                    dict_student[student_num]['section'] = new_section

                    for i, row in enumerate(students_dataset):
                        if row[0] == student_num:
                            students_dataset[i][2] = new_section
                            break

                    if student_num in dict_grades:
                        dict_grades[student_num]['section'] = new_section
                        for i, row in enumerate(grades_dataset):
                            if row[0] == student_num:
                                grades_dataset[i][2] = new_section

                    print(f"Section updated to: {new_section}")
                    current_info['section'] = new_section
                    save_to_files()
                    break
                else:
                    print("Invalid format. Use format: ABCD-12A3 or BSE1-12A3")

        elif choice == 3:
            while True:
                new_student_num = input(f"Current student number: {student_num}\nEnter new student number: ")

                if len(new_student_num) != 6 or not new_student_num.isdigit():
                    print("Student number must be 6 digits.")
                    continue

                if new_student_num in dict_student and new_student_num != student_num:
                    print("This student number is already taken.")
                    continue

                dict_student[new_student_num] = dict_student[student_num]
                del dict_student[student_num]

                for i, row in enumerate(students_dataset):
                    if row[0] == student_num:
                        students_dataset[i][0] = new_student_num
                        break

                if student_num in dict_grades:
                    dict_grades[new_student_num] = dict_grades[student_num]
                    del dict_grades[student_num]
                    dict_grades[new_student_num]['name'] = current_info['name']

                    for i, row in enumerate(grades_dataset):
                        if row[0] == student_num:
                            grades_dataset[i][0] = new_student_num

                print(f"Student number updated from {student_num} to {new_student_num}")
                student_num = new_student_num
                save_to_files()
                break

        elif choice == 4:
            break

        else:
            print("Invalid choice. Please select 1-4.")

    print("\nStudent information updated successfully!")
    input("Press Enter to return to main menu...")


def main_menu():
    load_from_files()

    while True:
        print("\n" + "=" * 50)
        print("WELCOME TO STUDENT GRADE EVALUATION SYSTEM")
        print("=" * 50)
        print("\n--- MAIN MENU ---")
        print("1. Register Student")
        print("2. View Student Records")
        print("3. Teacher's Log (Compute Quarter Grades)")
        print("4. Edit Student Information")
        print("5. Exit")

        try:
            choice = int(input("\nPlease input a number: "))
        except ValueError:
            print("Invalid input. Please enter a number.")
            continue

        if choice == 1:
            while True:
                student_num = input("\nEnter Student Number (6 digits): ")

                if len(student_num) != 6 or not student_num.isdigit():
                    print("Invalid input. Student number must be 6 digits.")
                    continue
                if student_num in dict_student:
                    print("This student number has already been registered.")
                    continue
                break

            while True:
                name = input("Enter Name (Format: SURNAME, FIRSTNAME M.I.): ")

                is_valid, error_msg = validate_name_format(name)
                if not is_valid:
                    print(error_msg)
                    continue

                if len(name) < 3 or len(name) > 50:
                    print("Name must be between 3 and 50 characters.")
                    continue

                if any(char.isdigit() for char in name):
                    print("Error: Name cannot contain numbers.")
                    continue
                break

            while True:
                section = input("Enter Section (format: ABCD-12A3 or BSE1-12A3): ").upper()

                if validate_section(section):
                    store_student(name, student_num, section)
                    print(f"\nSuccessfully registered {name.upper()}!")
                    break
                else:
                    print("Invalid format. Use format: ABCD-12A3 or BSE1-12A3")

        elif choice == 2:
            view_student_records_menu()

        elif choice == 3:
            compute_quarter_grades()

        elif choice == 4:
            edit_student_info()

        elif choice == 5:
            print("\nThank you for using Student Grade Evaluation System!")
            print("Exiting program...")
            save_to_files()
            break

        else:
            print("Invalid choice. Please select 1-5.")


if __name__ == "__main__":
    main_menu()
