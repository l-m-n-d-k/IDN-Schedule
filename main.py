import json
from collections import defaultdict
import time

def read_data():
    with open('class_subs_hours.json', 'r', encoding='utf-8') as f:
        class_hours = json.load(f)
    with open('teacher_subs_room_class.json', 'r', encoding='utf-8') as f:
        teacher_data = json.load(f)
    return class_hours, teacher_data

def initialize_schedule(class_hours):
    schedule = {}
    for class_name in class_hours.keys():
        schedule[class_name] = {
            'Monday': ['Important Conversations'] + [None] * 5,
            'Tuesday': [None] * 6,
            'Wednesday': [None] * 6,
            'Thursday': [None] * 5 + ['Class Hour'],
            'Friday': [None] * 6
        }
    return schedule

def build_teacher_cache(teacher_data):
    cache = defaultdict(lambda: defaultdict(list))
    for teacher in teacher_data:
        for subject in teacher['Предметы']:
            for class_name in teacher['Классы']:
                cache[subject][class_name].append((teacher['Учитель'], teacher['Кабинет']))
    return cache

def assign_classes(schedule, class_hours, teacher_data):
    teacher_schedule = defaultdict(lambda: defaultdict(lambda: [None] * 7))
    room_schedule = defaultdict(lambda: defaultdict(lambda: [None] * 7))
    teacher_cache = build_teacher_cache(teacher_data)

    for class_name, subjects in class_hours.items():
        day_index = 0
        lesson_index = 1
        for subject, hours in subjects.items():
            hours_assigned = 0
            while hours_assigned < hours:
                if (class_name.startswith('5') or class_name.startswith('6')) and lesson_index == 6:
                    lesson_index = 1
                    day_index += 1
                    if day_index == 5:
                        day_index = 0
                elif lesson_index == 7:
                    lesson_index = 1
                    day_index += 1
                    if day_index == 5:
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
                lesson_index += 1
                if lesson_index == 6:
                    lesson_index = 1
                    day_index += 1
                    if day_index == 5:
                        day_index = 0
    return schedule

def save_schedule_to_json(schedule, filename):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(schedule, f, ensure_ascii=False, indent=4)

def main():
    start_time = time.time()
    class_hours, teacher_data = read_data()
    schedule = initialize_schedule(class_hours)
    schedule = assign_classes(schedule, class_hours, teacher_data)
    end_time = time.time()
    execution_time = end_time - start_time
    save_schedule_to_json(schedule, 'school_schedule.json')
    return schedule, execution_time

schedule, execution_time = main()

# Display the resulting schedule for review
for class_name, days in schedule.items():
    print(f"Schedule for class {class_name}:")
    for day, lessons in days.items():
        print(f"  {day}: {lessons}")

# Output the execution time
print(f"Execution time: {execution_time} seconds")
