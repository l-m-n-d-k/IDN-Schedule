import json
from collections import defaultdict

# Function to read provided JSON files
def read_data():
    with open('/mnt/data/class_subs_hours.json', 'r', encoding='utf-8') as f:
        class_hours = json.load(f)
    with open('/mnt/data/teacher_subs_room_class.json', 'r', encoding='utf-8') as f:
        teacher_data = json.load(f)
    return class_hours, teacher_data

# Function to initialize the schedule
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

# Function to assign classes to the schedule
def assign_classes(schedule, class_hours, teacher_data):
    teacher_schedule = defaultdict(lambda: defaultdict(lambda: [None] * 7))
    room_schedule = defaultdict(lambda: defaultdict(lambda: [None] * 7))

    for class_name, subjects in class_hours.items():
        day_index = 0
        lesson_index = 1
        for subject, hours in subjects.items():
            hours_assigned = 0
            while hours_assigned < hours and day_index < 5:
                if (class_name.startswith('5') or class_name.startswith('6')) and lesson_index == 6:
                    lesson_index = 0
                    day_index += 1
                    if day_index == 5:
                        day_index = 0
                elif lesson_index == 7:
                    lesson_index = 0
                    day_index += 1
                    if day_index == 5:
                        day_index = 0

                day_name = list(schedule[class_name].keys())[day_index]
                if schedule[class_name][day_name][lesson_index] is None:
                    teacher_available = True
                    room_available = True

                    for teacher in teacher_data:
                        if subject in teacher['Предметы'] and class_name in teacher['Классы']:
                            teacher_name = teacher['Учитель']
                            room_number = teacher['Кабинет']
                            if teacher_schedule[teacher_name][day_name][lesson_index] is not None:
                                teacher_available = False
                            if room_schedule[room_number][day_name][lesson_index] is not None:
                                room_available = False
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
                    lesson_index = 0
                    day_index += 1
    return schedule

# Function to save the schedule to a JSON file
def save_schedule_to_json(schedule, filename):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(schedule, f, ensure_ascii=False, indent=4)

# Main function to orchestrate the scheduling
def main():
    class_hours, teacher_data = read_data()
    schedule = initialize_schedule(class_hours)
    schedule = assign_classes(schedule, class_hours, teacher_data)
    save_schedule_to_json(schedule, '/mnt/data/school_schedule.json')
    return schedule

schedule = main()

import pandas as pd
pd.set_option('display.max_colwidth', None)  # Ensure full content is shown
pd.DataFrame(schedule).to_json(orient="index")
