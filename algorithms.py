def bubble_sort_students(student_list):
    n = len(student_list)
    for i in range(n - 1):
        for j in range(0, n - i - 1):
            if student_list[j]['final_average'] < student_list[j + 1]['final_average']:
                student_list[j], student_list[j + 1] = student_list[j + 1], student_list[j]
    return student_list


def linear_search_student(student_list, student_number):
    for index, student in enumerate(student_list):
        if student.get('student_number') == student_number:
            return index, student
    return -1, None


def calculate_quarter_average(grades, subjects, quarter):
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
            return (subj_grades['prelim'] * 0.20 +
                    subj_grades['midterm'] * 0.25 +
                    subj_grades['prefinal'] * 0.25 +
                    subj_grades['final'] * 0.30)
    return 0


def calculate_final_average(grades, subjects):
    subject_final_grades = []
    for subject in subjects:
        if subject in grades:
            final_grade = calculate_final_subject_grade(grades, subject)
            if final_grade > 0:
                subject_final_grades.append(final_grade)
    return sum(subject_final_grades) / len(subject_final_grades) if subject_final_grades else 0
