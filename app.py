from flask import Flask, render_template, request, redirect
import datetime
import threading
import time
from plyer import notification

app = Flask(__name__)
TASK_FILE = 'tasks.txt'


# Read tasks from file
def read_tasks():
    tasks = []
    try:
        with open(TASK_FILE, 'r') as file:
            for line in file:
                task, time_str = line.strip().split(' | ')
                tasks.append((task, time_str))
    except FileNotFoundError:
        open(TASK_FILE, 'w').close()  # Create the file if it doesn't exist
    return tasks


# Write task to file
def write_task(task, reminder_time):
    with open(TASK_FILE, 'a') as file:
        file.write(f'{task} | {reminder_time}\n')


# Background thread to check reminders
def check_reminders():
    while True:
        now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
        tasks = read_tasks()
        updated_tasks = tasks.copy()
        for task, reminder_time in tasks:
            if reminder_time == now:
                notification.notify(
                    title='Task Reminder!',
                    message=task,
                    timeout=10
                )
                updated_tasks.remove((task, reminder_time))
        # Rewrite tasks after notification
        with open(TASK_FILE, 'w') as file:
            for t, rt in updated_tasks:
                file.write(f'{t} | {rt}\n')
        time.sleep(60)


# Home route
@app.route('/')
def index():
    tasks = read_tasks()
    return render_template('index.html', tasks=tasks)


# Add task route
@app.route('/add', methods=['POST'])
def add():
    task = request.form['task']
    reminder_time = request.form['time'].replace('T', ' ')
    write_task(task, reminder_time)
    return redirect('/')


# Start the app
if __name__ == '__main__':
    threading.Thread(target=check_reminders, daemon=True).start()
    app.run(debug=True)
