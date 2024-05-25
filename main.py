import pandas as pd
import re

# Загрузка данных из файлов
class_subs_hours_path = 'class+subs-hours.xlsx'
teacher_subs_room_class_path = 'teacher_subs_room_class.xlsx'

class_subs_hours = pd.read_excel(class_subs_hours_path)
teacher_subs_room_class = pd.read_excel(teacher_subs_room_class_path)

# Преобразование данных из таблиц в удобный формат
class_subs_hours.columns = ['Класс/Предмет', 'Часы']
class_subs_hours['Класс/Предмет'] = class_subs_hours['Класс/Предмет'].fillna('')

class_data = {}
current_class = None

for index, row in class_subs_hours.iterrows():
    if pd.isna(row['Часы']) and row['Класс/Предмет'] != '':
        current_class = row['Класс/Предмет']
        class_data[current_class] = {}
    elif not pd.isna(row['Часы']) and current_class:
        class_data[current_class][row['Класс/Предмет']] = int(row['Часы'])

# Подготовка данных о нагрузке учителей
teacher_data = teacher_subs_room_class[['Учитель', 'Предметы', 'Кабинет', 'Классы']]
teacher_data['Классы'] = teacher_data['Классы'].str.replace('\n', '')

# Создание словаря с расписанием для каждого класса
days = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница']
schedule = {class_name: {day: ['']*7 for day in days} for class_name in class_data.keys()}

# Заполнение фиксированных уроков
for class_name in schedule:
    schedule[class_name]['Понедельник'][0] = 'Разговоры о важном'
    schedule[class_name]['Четверг'][6] = 'Классный час'

# Функция проверки занятости учителя
def is_teacher_available(schedule, teacher, day, lesson):
    for class_schedule in schedule.values():
        if class_schedule[day][lesson] == teacher:
            return False
    return True

# Функция проверки допустимого количества уроков в день для класса
def is_class_limit_exceeded(class_name, schedule, day, max_lessons):
    return sum(1 for lesson in schedule[class_name][day] if lesson) >= max_lessons

# Распределение уроков с учетом занятости учителей и ограничений
def distribute_lessons(schedule, class_data, teacher_data):
    days = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница']
    
    # Создаем словарь соответствия учителей и предметов
    teacher_subjects = {}
    for _, row in teacher_data.iterrows():
        teacher = row['Учитель']
        subjects = row['Предметы'].split(',')
        for subject in subjects:
            if subject not in teacher_subjects:
                teacher_subjects[subject] = []
            teacher_subjects[subject].append(teacher)
    
    for class_name, subjects in class_data.items():
        lessons_to_schedule = [(subject, hours) for subject, hours in subjects.items()]
        
        # Сортируем предметы по убыванию часов для равномерного распределения
        lessons_to_schedule.sort(key=lambda x: x[1], reverse=True)
        
        max_lessons = 6 if "5" in class_name or "6" in class_name else 7
        
        for subject, hours in lessons_to_schedule:
            distributed_hours = 0
            
            for day in days:
                if distributed_hours >= hours:
                    break

                for lesson in range(7):
                    if schedule[class_name][day][lesson] == '' and (lesson == 0 or schedule[class_name][day][lesson-1] != subject):
                        if is_class_limit_exceeded(class_name, schedule, day, max_lessons):
                            continue
                        available_teachers = teacher_subjects.get(subject, [])
                        for teacher in available_teachers:
                            if is_teacher_available(schedule, teacher, day, lesson):
                                schedule[class_name][day][lesson] = subject
                                distributed_hours += 1
                                break

                        if distributed_hours >= hours:
                            break

    return schedule

# Применяем функцию к нашему расписанию
updated_schedule = distribute_lessons(schedule, class_data, teacher_data)

# Функция для вывода расписания в текстовом формате для одного класса
def schedule_to_text(schedule, class_name):
    output = []
    for day, lessons in schedule[class_name].items():
        lessons_str = ', '.join([lesson if lesson else '---' for lesson in lessons])
        output.append(f"{day}: {lessons_str}")
    return "\n".join(output)

# Сохранение расписания в текстовый файл
def save_schedule_to_text_file(schedule, class_name, file_path):
    schedule_text = schedule_to_text(schedule, class_name)
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(schedule_text)

# Сохранение расписания для всех классов в текстовые файлы
for class_name in schedule:
    sanitized_class_name = re.sub(r'[^\w\s-]', '', class_name).replace(' ', '_')
    text_file_path = f'schedule_{sanitized_class_name}.txt'
    save_schedule_to_text_file(updated_schedule, class_name, text_file_path)
    print(f"Saved schedule for {class_name} to {text_file_path}")

# Проверка содержимого одного из файлов
text_file_path
