import json
from collections import defaultdict
import random

# Чтение данных
def read_data():
    with open('class_subs_hours.json', 'r', encoding='utf-8') as f:
        class_hours = json.load(f)
    with open('teacher_subs_room_class.json', 'r', encoding='utf-8') as f:
        teacher_data = json.load(f)
    return class_hours, teacher_data

# Инициализация расписания
def initialize_schedule(class_hours):
    schedule = {}
    for class_name in class_hours.keys():
        if class_name.startswith("5") or class_name.startswith("6"):
            max_lessons_per_day = 6
        else:
            max_lessons_per_day = 7
        
        schedule[class_name] = {
            'Понедельник': ['Разговоры о важном'] + [None] * (max_lessons_per_day - 1),
            'Вторник': [None] * max_lessons_per_day,
            'Среда': [None] * max_lessons_per_day,
            'Четверг': [None] * (max_lessons_per_day - 1) + ['Классный час'],
            'Пятница': [None] * max_lessons_per_day
        }
    return schedule

# Создание кэша учителей
def build_teacher_cache(teacher_data):
    cache = defaultdict(lambda: defaultdict(list))
    for teacher in teacher_data:
        for subject in teacher['Предметы']:
            for class_name in teacher['Классы']:
                cache[subject][class_name].append((teacher['Учитель'], teacher['Кабинет']))
    return cache

# Назначение уроков
def assign_classes(schedule, class_hours, teacher_data):
    teacher_cache = build_teacher_cache(teacher_data)
    teacher_schedule = defaultdict(lambda: defaultdict(lambda: [None] * 7))
    room_schedule = defaultdict(lambda: defaultdict(lambda: [None] * 7))

    # Определение учителей, приходящих из других зданий (Шк3)
    for teacher in teacher_data:
        if "ШК-3" in teacher['Кабинет']:
            for class_name in teacher['Классы']:
                for subject in teacher['Предметы']:
                    for day in ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница']:
                        for lesson_index in range(1, len(schedule[class_name][day])):
                            if schedule[class_name][day][lesson_index] is None:
                                schedule[class_name][day][lesson_index] = {
                                    'subject': subject,
                                    'teacher': teacher['Учитель'],
                                    'room': teacher['Кабинет']
                                }
                                teacher_schedule[teacher['Учитель']][day][lesson_index] = class_name
                                room_schedule[teacher['Кабинет']][day][lesson_index] = class_name
                                break

    # Определение учителей и их доступности
    for class_name, subjects in class_hours.items():
        for subject, hours in subjects.items():
            hours_assigned = 0
            while hours_assigned < hours:
                day_found = False
                for day in ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница']:
                    for lesson_index in range(1, len(schedule[class_name][day])):
                        if schedule[class_name][day][lesson_index] is None:
                            for teacher_name, room_number in teacher_cache[subject][class_name]:
                                if teacher_schedule[teacher_name][day][lesson_index] is None and room_schedule[room_number][day][lesson_index] is None:
                                    schedule[class_name][day][lesson_index] = {
                                        'subject': subject,
                                        'teacher': teacher_name,
                                        'room': room_number
                                    }
                                    teacher_schedule[teacher_name][day][lesson_index] = class_name
                                    room_schedule[room_number][day][lesson_index] = class_name
                                    hours_assigned += 1
                                    day_found = True
                                    break
                            if day_found:
                                break
                    if day_found:
                        break
                if not day_found:
                    break
    return schedule

# Сохранение расписания в JSON файл
def save_schedule_to_json(schedule, filename):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(schedule, f, ensure_ascii=False, indent=4)

# Основная функция
def main():
    class_hours, teacher_data = read_data()
    schedule = initialize_schedule(class_hours)
    schedule = assign_classes(schedule, class_hours, teacher_data)
    save_schedule_to_json(schedule, 'school_schedule.json')
    return schedule

schedule = main()

# Отобразить полученное расписание для проверки
for class_name, days in schedule.items():
    print(f"Расписание для класса {class_name}:")
    for day, lessons in days.items():
        print(f"  {day}: {lessons}")
