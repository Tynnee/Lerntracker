from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from models import db, Goal, Task

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///learn_tracker.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

@app.route('/')
def index():
    goals = Goal.query.all()
    return render_template('index.html', goals=goals)

@app.route('/add_goal', methods=['GET', 'POST'])
def add_goal():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        new_goal = Goal(title=title, description=description)
        db.session.add(new_goal)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('goal_form.html')

@app.route('/add_task/<int:goal_id>', methods=['GET', 'POST'])
def add_task(goal_id):
    goal = Goal.query.get_or_404(goal_id)
    if request.method == 'POST':
        title = request.form['title']
        new_task = Task(title=title, goal_id=goal_id)
        db.session.add(new_task)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('task_form.html', goal=goal)

@app.route('/toggle_task/<int:task_id>', methods=['POST'])
def toggle_task(task_id):
    task = Task.query.get_or_404(task_id)
    task.completed = not task.completed
    goal = task.goal
    tasks = goal.tasks
    total_tasks = len(tasks)
    completed_tasks = sum(1 for task in tasks if task.completed)
    goal.progress = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
    db.session.commit()
    return redirect(url_for('index'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(port=5005, debug=True)