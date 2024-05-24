import pandas as pd
import random

# Загрузка данных
class_subs_hours_path = 'class+subs-hours.xlsx'
teacher_subs_room_class_path = 'teacher_subs_room_class.xlsx'

# Загрузка данных из файлов
class_subs_hours_df = pd.read_excel(class_subs_hours_path, header=None)
teacher_subs_room_class_df = pd.read_excel(teacher_subs_room_class_path)

# Обработка данных для class+subs-hours.xlsx
def process_class_subs_hours(df):
    classes = {}
    current_class = None
    for index, row in df.iterrows():
        if pd.isna(row[1]):
            current_class = row[0]
            classes[current_class] = {}
        else:
            subject = row[0]
            hours = int(row[1])
            classes[current_class][subject] = hours
    return classes

class_hours = process_class_subs_hours(class_subs_hours_df)

# Обработка данных для teacher_subs_room_class.xlsx
teacher_subs_room_class_df['Предметы'] = teacher_subs_room_class_df['Предметы'].str.split(',')
teacher_subs_room_class_df['Классы'] = teacher_subs_room_class_df['Классы'].str.split(',')

teachers = teacher_subs_room_class_df.to_dict(orient='records')

# Функция для создания расписания
def create_schedule(classes, teachers):
    schedule = {class_name: [] for class_name in classes.keys()}
    days = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница']
    periods_per_day = 7
    
    # Создаем структуру для учета занятости учителей и кабинетов
    teacher_availability = {teacher['Учитель']: {day: [True] * periods_per_day for day in days} for teacher in teachers}
    room_availability = {teacher['Кабинет']: {day: [True] * periods_per_day for day in days} for teacher in teachers}

    def assign_period(class_name, subject, teacher, day, period):
        if teacher_availability[teacher['Учитель']][day][period - 1] and room_availability[teacher['Кабинет']][day][period - 1]:
            schedule[class_name].append((day, period, teacher['Учитель'], subject))
            teacher_availability[teacher['Учитель']][day][period - 1] = False
            room_availability[teacher['Кабинет']][day][period - 1] = False
            return True
        return False

    # Сортируем предметы по количеству часов в убывающем порядке для каждого класса
    for class_name, subjects in classes.items():
        sorted_subjects = sorted(subjects.items(), key=lambda item: item[1], reverse=True)
        
        for subject, hours in sorted_subjects:
            assigned_hours = 0
            for day in days:
                for period in range(1, periods_per_day + 1):
                    if assigned_hours >= hours:
                        break
                    available_teachers = [
                        teacher for teacher in teachers 
                        if subject in teacher['Предметы'] and class_name in teacher['Классы']
                    ]
                    if available_teachers:
                        for teacher in available_teachers:
                            if assign_period(class_name, subject, teacher, day, period):
                                assigned_hours += 1
                                break
                    if assigned_hours >= hours:
                        break

    return schedule

schedule = create_schedule(class_hours, teachers)

# Функция для отображения расписания
def display_schedule(schedule):
    schedule_df = []
    for class_name, lessons in schedule.items():
        for day, period, teacher, subject in lessons:
            schedule_df.append([class_name, day, period, teacher, subject])
    
    schedule_df = pd.DataFrame(schedule_df, columns=['Класс', 'День', 'Период', 'Учитель', 'Предмет'])
    return schedule_df

schedule_df = display_schedule(schedule)
schedule_df.sort_values(by=['Класс', 'День', 'Период'], inplace=True)

# Отображение первых 10 строк расписания
print(schedule_df.head(10))

# Сохранение результата в файл
schedule_df.to_excel('school_schedule.xlsx', index=False)
