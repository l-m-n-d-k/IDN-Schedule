import smtplib
import imaplib
import email
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import json
import re
import time
import schedule

sent_emails = []

def send_email():
    global sent_emails
    from_address = input("Введите ваш email: ")
    password = input("Введите ваш пароль: ")  
    to_addresses = input("Введите email адреса получателей через запятую: ").split(',')
    subject = "Проведение уроков во втором здании школы ГБОУ №2009"
    message_body = "Здравствуйте! По каким дням недели у вас есть возможность проводить уроки в 2 здании ГБОУ школы №2009"

    smtp_server = 'smtp.gmail.com'
    smtp_port = 587

    msg = MIMEMultipart()
    msg['From'] = from_address
    msg['To'] = ', '.join(to_addresses)
    msg['Subject'] = subject

    msg.attach(MIMEText(message_body, 'plain'))

    server = smtplib.SMTP(smtp_server, smtp_port)
    server.starttls()

    try:
        server.login(from_address, password)
        server.sendmail(from_address, to_addresses, msg.as_string())
        sent_emails = to_addresses
        print("Письма успешно отправлены!")
    except Exception as e:
        print(f"Не удалось отправить письма. Ошибка: {e}")
    finally:
        server.quit()

def read_email():
    from_address = input("Введите ваш email для чтения: ")
    password = input("Введите ваш пароль для чтения: ")
    
    imap_server = 'imap.gmail.com'
    imap = imaplib.IMAP4_SSL(imap_server)
    imap.login(from_address, password)
    imap.select('inbox')

    status, messages = imap.search(None, 'ALL')
    email_ids = messages[0].split()

    for email_id in email_ids:
        status, msg_data = imap.fetch(email_id, '(RFC822)')
        msg = email.message_from_bytes(msg_data[0][1])
        
        if msg['From'] in sent_emails:
            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_type() == "text/plain":
                        message_body = part.get_payload(decode=True).decode()
                        response_data = parse_response(message_body)
                        if response_data:
                            process_response(msg['From'], response_data)

    imap.logout()

def parse_response(message_body):
    pattern = re.compile(r'Доступные дни:\(\((.*?)\)\) Доступные уроки в \(.*?\) (.*)')
    match = pattern.search(message_body)
    if match:
        days = match.group(1).split()
        teacher = match.group(2).strip()
        return {
            "Учитель": teacher,
            "Доступные дни": days,
            "Доступные уроки": ["урок 1", "урок 2", "урок 3", "урок 4", "урок 5", "урок 6", "урок 7"]
        }
    return None

def process_response(email, response_data):
    with open('teacher_subs_room_class.json', 'r', encoding='utf-8') as file:
        data = json.load(file)

    found = False
    for teacher in data:
        if teacher['Учитель'] == response_data['Учитель']:
            teacher['Доступные дни'] = response_data['Доступные дни']
            teacher['Доступные уроки'] = response_data['Доступные уроки']
            found = True
            break

    if not found:
        print(f"Учитель {response_data['Учитель']} не найден в JSON файле")

    with open('teacher_subs_room_class.json', 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

    print(f"Информация для учителя {response_data['Учитель']} обновлена в JSON файле")

def update_unresponsive_teachers():
    with open('teacher_subs_room_class.json', 'r', encoding='utf-8') as file:
        data = json.load(file)

    default_days = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница"]
    default_lessons = ["урок 1", "урок 2", "урок 3", "урок 4", "урок 5", "урок 6", "урок 7"]

    for teacher in data:
        if 'Доступные дни' not in teacher or not teacher['Доступные дни']:
            teacher['Доступные дни'] = default_days
        if 'Доступные уроки' not in teacher or not teacher['Доступные уроки']:
            teacher['Доступные уроки'] = default_lessons

    with open('teacher_subs_room_class.json', 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

    print("Информация для учителей, которые не ответили, обновлена")

def check_emails_periodically():
    read_email()
    update_unresponsive_teachers()

send_email()

schedule.every(10).minutes.do(check_emails_periodically)

while True:
    schedule.run_pending()
    time.sleep(1)
