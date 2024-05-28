import json
from collections import defaultdict
import time

def read_data():
    start_time = time.time()
    with open('class_subs_hours.json', 'r', encoding='utf-8') as f:
        class_hours = json.load(f)
    with open('teacher_subs_room_class.json', 'r', encoding='utf-8') as f:
        teacher_data = json.load(f)
    end_time = time.time()
    print(f"Чтение данных: {end_time - start_time} секунд")
    return class_hours, teacher_data

def initialize_schedule(class_hours):
    start_time = time.time()
    schedule = {}
    for class_name in class_hours.keys():
        schedule[class_name] = {
            'Понедельник': ['Разговоры о важном'] + [None] * 5,
            'Вторник': [None] * 6,
            'Среда': [None] * 6,
            'Четверг': [None] * 5 + ['Классный час'],
            'Пятница': [None] * 6
        }
    end_time = time.time()
    print(f"Инициализация расписания: {end_time - start_time} секунд")
    return schedule

def build_teacher_cache(teacher_data):
    start_time = time.time()
    cache = defaultdict(lambda: defaultdict(list))
    for teacher in teacher_data:
        for subject in teacher['Предметы']:
            for class_name in teacher['Классы']:
                cache[subject][class_name].append((teacher['Учитель'], teacher['Кабинет']))
    end_time = time.time()
    print(f"Построение кэша учителей: {end_time - start_time} секунд")
    return cache

def assign_classes(schedule, class_hours, teacher_data):
    start_time = time.time()
    teacher_schedule = defaultdict(lambda: defaultdict(lambda: [None] * 7))
    room_schedule = defaultdict(lambda: defaultdict(lambda: [None] * 7))
    teacher_cache = build_teacher_cache(teacher_data)

    total_subjects = sum(len(subjects) for subjects in class_hours.values())
    processed_subjects = 0

    for class_name, subjects in class_hours.items():
        day_index = 0
        lesson_index = 1
        for subject, hours in subjects.items():
            hours_assigned = 0
            while hours_assigned < hours:
                processed_subjects += 1
                if processed_subjects % 100 == 0:
                    print(f"Обработано {processed_subjects} из {total_subjects} предметов")

                if (class_name.startswith('5') or class_name.startswith('6')) and lesson_index == 6:
                    lesson_index = 1
                    day_index += 1
                    if day_index == 5:
                        print(f"Сброс day_index для класса {class_name} и предмета {subject}")
                        day_index = 0
                elif lesson_index == 7:
                    lesson_index = 1
                    day_index += 1
                    if day_index == 5:
                        print(f"Сброс day_index для класса {class_name} и предмета {subject}")
                        day_index = 0

                day_name = list(schedule[class_name].keys())[day_index]
                if schedule[class_name][day_name][lesson_index] is None:
                    for teacher_name, room_number in teacher_cache[subject][class_name]:
                        teacher_available = teacher_schedule[teacher_name][day_name][lesson_index] is None
                        room_available = room_schedule[room_number][day_name][lesson_index] is None
                        if teacher_available and room_available:
                            schedule[class_name][day_name][lesson_index] = {
                                'subject': subject,
                                'teacher': teacher_name,
                                'room': room_number
                            }
                            teacher_schedule[teacher_name][day_name][lesson_index] = subject
                            room_schedule[room_number][day_name][lesson_index] = subject
                            hours_assigned += 1
                            break
                else:
                    print(f"Время {lesson_index} в {day_name} уже занято для класса {class_name}")
                
                lesson_index += 1
                if lesson_index == 6:
                    lesson_index = 1
                    day_index += 1
                    if day_index == 5:
                        day_index = 0

                # Safety check to avoid infinite loop
                if processed_subjects > total_subjects * 10:
                    raise RuntimeError("Программа застряла в бесконечном цикле")

    end_time = time.time()
    print(f"Назначение уроков: {end_time - start_time} секунд")
    return schedule

def save_schedule_to_json(schedule, filename):
    start_time = time.time()
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(schedule, f, ensure_ascii=False, indent=4)
    end_time = time.time()
    print(f"Сохранение расписания в JSON: {end_time - start_time} секунд")

def main():
    start_time = time.time()
    class_hours, teacher_data = read_data()
    schedule = initialize_schedule(class_hours)
    schedule = assign_classes(schedule, class_hours, teacher_data)
    save_schedule_to_json(schedule, 'school_schedule.json')
    end_time = time.time()
    execution_time = end_time - start_time
    return schedule, execution_time

schedule, execution_time = main()

# Отобразить полученное расписание для проверки
for class_name, days in schedule.items():
    print(f"Расписание для класса {class_name}:")
    for day, lessons in days.items():
        print(f"  {day}: {lessons}")

# Вывести время выполнения
print(f"Общее время выполнения: {execution_time} секунд")
