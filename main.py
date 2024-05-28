import json
import pandas as pd
import random

# Загрузка данных с указанием кодировки UTF-8
print("Загрузка данных...")
with open('class_subs_hours.json', 'r', encoding='utf-8') as f:
    class_subs_hours = json.load(f)

with open('teacher_subs_room_class.json', 'r', encoding='utf-8') as f:
    teacher_subs_room_class = json.load(f)
print("Данные загружены.")

# Преобразование данных в DataFrame для удобства работы
print("Преобразование данных...")
class_hours_df = pd.DataFrame(class_subs_hours).T
teachers_df = pd.json_normalize(teacher_subs_room_class, 'Классы', ['Учитель', 'Предметы', 'Кабинет'])
print("Данные преобразованы.")

# Создание структуры расписания
print("Создание структуры расписания...")
days = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница']
lessons_per_day = 6

schedule = {cls: {day: [''] * lessons_per_day for day in days} for cls in class_subs_hours}
print("Структура расписания создана.")

# Функция для назначения учителя и кабинета
def assign_teacher_and_room(subject, cls):
    teacher_data = teachers_df[(teachers_df['Предметы'].apply(lambda x: subject in x)) & (teachers_df[0] == cls)]
    if not teacher_data.empty:
        teacher = teacher_data.iloc[0]['Учитель']
        room = teacher_data.iloc[0]['Кабинет']
        return teacher, room
    return None, None

# Распределение предметов по расписанию
def distribute_subjects():
    for cls, subjects in class_hours_df.iterrows():
        print(f"Распределение предметов для класса {cls}...")
        for subject, hours in subjects.items():
            if hours > 0:
                distribute_hours(cls, subject, hours)
                print(f"    {subject} распределён для {cls}. Осталось часов: {hours}")

def distribute_hours(cls, subject, hours):
    days_available = list(days)
    while hours > 0:
        if not days_available:
            print(f"Предупреждение: Недостаточно доступных дней для класса {cls} и предмета {subject}.")
            break
        day = random.choice(days_available)
        lesson_slots = schedule[cls][day]
        for i in range(lessons_per_day):
            if lesson_slots[i] == '':
                teacher, room = assign_teacher_and_room(subject, cls)
                if teacher and room:
                    lesson_slots[i] = f"{subject} ({teacher}, {room})"
                    hours -= 1
                    print(f"        Назначен {subject} для {cls} на {day}, урок {i+1}. Осталось часов: {hours}.")
                    if hours == 0:
                        break
        days_available.remove(day)

# Функция для записи расписания в JSON файл
def save_schedule_to_json(schedule, filename):
    print(f"Сохранение расписания в файл {filename}...")
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(schedule, f, ensure_ascii=False, indent=4)
    print(f"Расписание сохранено в файл {filename}.")

# Распределяем предметы
print("Начинаем распределение предметов...")
distribute_subjects()
print("Распределение предметов завершено.")

# Сохраняем расписание в JSON файл
save_schedule_to_json(schedule, 'schedule.json')
print("Готово!")
