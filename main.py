import pandas as pd
import json

# Обработка данных
def process_class_subs_hours(df):
    classes = {}
    current_class = None
    for index, row in df.iterrows():
        if pd.isna(row.iloc[0]):
            continue
        if pd.isna(row.iloc[1]):
            current_class = row.iloc[0]
            classes[current_class] = []
        else:
            subject = row.iloc[0].strip()
            hours = row.iloc[1]
            if current_class is not None:
                classes[current_class].append((subject, hours))
            else:
                print(f"Error at index {index}: current_class is None")
    return classes

# Генерация расписания
def generate_schedule(classes_data):
    # Инициализация пустого расписания
    schedule = {}
    days = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница']
    max_lessons_per_day = {'5': 6, '6': 6, '7': 7, '8': 7, '9': 7, '10': 7, '11': 7}
    
    for cls in classes_data.keys():
        grade = cls.split(" ")[0]  # Получаем класс (например, '5', '6', ...)
        schedule[cls] = {day: [None] * max_lessons_per_day[grade] for day in days}
    
    # Заполнение фиксированных уроков
    for cls in classes_data.keys():
        schedule[cls]['Понедельник'][0] = 'Разговоры о важном'
        grade = cls.split(" ")[0]  # Получаем класс (например, '5', '6', ...)
        last_lesson_index = max_lessons_per_day[grade] - 1
        schedule[cls]['Четверг'][last_lesson_index] = 'Классный час'  # Предполагается, что классный час - последний урок
    
    # Заполнение оставшегося расписания
    for cls, subjects in classes_data.items():
        grade = cls.split(" ")[0]  # Получаем класс (например, '5', '6', ...)
        max_lessons = max_lessons_per_day[grade]
        
        day_order = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница']
        day_index, lesson_index = 0, 1
        
        for subject, hours in subjects:
            while hours > 0 and day_index < len(day_order):
                if lesson_index >= max_lessons:
                    lesson_index = 0
                    day_index += 1
                    if day_index >= len(day_order):
                        break
                day = day_order[day_index]
                if schedule[cls][day][lesson_index] is None:
                    # Проверка на повторение более двух раз подряд
                    if lesson_index < 2 or schedule[cls][day][lesson_index-1] != subject or schedule[cls][day][lesson_index-2] != subject:
                        schedule[cls][day][lesson_index] = subject
                        hours -= 1
                lesson_index += 1

    return schedule

# Загружаем данные
class_subs_hours = pd.read_csv('class_subs_hours.csv')
teacher_subs_room_class = pd.read_csv('teacher_subs_room_class.csv')

# Обработка данных из первой таблицы
classes_data = process_class_subs_hours(class_subs_hours)

# Генерация расписания
schedule = generate_schedule(classes_data)

# Сохранение расписания для всех классов в JSON-файл
def save_schedule_to_json(schedule, filename='school_schedule.json'):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(schedule, f, ensure_ascii=False, indent=4)

# Сохранение расписания
save_schedule_to_json(schedule)
