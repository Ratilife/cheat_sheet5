import os
from datetime import datetime, timedelta

def validate_date(date_str):
    try:
        datetime.strptime(date_str, '%d.%m.%Y')
        return True
    except ValueError:
        return False

def validate_time(time_str):
    try:
        datetime.strptime(time_str, '%H:%M')
        return True
    except ValueError:
        return False

def calculate_time_duration(start, end):
    start_time = datetime.strptime(start, '%H:%M')
    end_time = datetime.strptime(end, '%H:%M')
    if end_time < start_time:
        end_time += timedelta(days=1)  # Для случая работы после полуночи
    duration = end_time - start_time
    hours, remainder = divmod(duration.seconds, 3600)
    minutes = remainder // 60
    return f"{hours:02d}:{minutes:02d}"

def format_time_duration(minutes):
    hours = minutes // 60
    mins = minutes % 60
    return f"{hours:02d}:{mins:02d}"

def get_weekday(date_str):
    date = datetime.strptime(date_str, '%d.%m.%Y')
    weekdays = ['понедельник', 'вторник', 'среда', 'четверг', 'пятница', 'суббота', 'воскресенье']
    return weekdays[date.weekday()]

def save_to_file(data):
    with open('Учет_времени.txt', 'a', encoding='utf-8') as f:
        f.write(data)

def main():
    print("Учет рабочего времени. Введите 'q' для выхода.")
    
    while True:
        date = input("\nВведите дату (ДД.ММ.ГГГГ) или 'q' для выхода: ").strip()
        if date.lower() == 'q':
            break
        
        if not validate_date(date):
            print("Ошибка: Некорректный формат даты. Используйте ДД.ММ.ГГГГ")
            continue
        
        weekday = get_weekday(date)
        daily_total_minutes = 0
        daily_data = f"\n{date} - {weekday}\n"
        
        while True:
            task = input("Введите название задачи: ").strip()
            if not task:
                print("Ошибка: Название задачи не может быть пустым")
                continue
                
            task_data = f"{task}\n"
            task_total_minutes = 0
            
            while True:
                start_time = input("Начало (ЧЧ:ММ): ").strip()
                if not validate_time(start_time):
                    print("Ошибка: Некорректный формат времени. Используйте ЧЧ:ММ")
                    continue
                    
                end_time = input("Окончание (ЧЧ:ММ): ").strip()
                if not validate_time(end_time):
                    print("Ошибка: Некорректный формат времени. Используйте ЧЧ:ММ")
                    continue
                
                duration = calculate_time_duration(start_time, end_time)
                hours, minutes = map(int, duration.split(':'))
                task_total_minutes += hours * 60 + minutes
                
                task_data += f"  Начало: {start_time} - Окончание: {end_time} Потрачено: {duration}\n"
                
                more_intervals = input("Добавить еще интервал для этой задачи? (y/n): ").strip().lower()
                if more_intervals != 'y':
                    break
            
            task_total = format_time_duration(task_total_minutes)
            daily_total_minutes += task_total_minutes
            task_data += f"Всего по задаче: {task_total}\n"
            daily_data += task_data
            
            more_tasks = input("Добавить еще задачу для этой даты? (y/n): ").strip().lower()
            if more_tasks != 'y':
                break
        
        daily_total = format_time_duration(daily_total_minutes)
        daily_data += f"Всего за день: {daily_total}\n"
        
        save_to_file(daily_data)
        print(f"Данные за {date} сохранены в файл 'Учет_времени.txt'")

if __name__ == "__main__":
    main()