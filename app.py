from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime
from collections import defaultdict

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///learn_tracker.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your-secret-key'  # Für Flash-Nachrichten benötigt

db = SQLAlchemy(app)
migrate = Migrate(app, db)

class Goal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    progress = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    tasks = db.relationship('Task', backref='goal', lazy=True)
    badges = db.relationship('Badge', backref='goal', lazy=True)

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    completed = db.Column(db.Boolean, default=False)
    completed_at = db.Column(db.DateTime, nullable=True)
    goal_id = db.Column(db.Integer, db.ForeignKey('goal.id'), nullable=False)

class Badge(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(200), nullable=True)
    goal_id = db.Column(db.Integer, db.ForeignKey('goal.id'), nullable=False)

def check_badges(goal):
    """Prüft und vergibt oder entfernt Abzeichen basierend auf Fortschritt und Aufgaben."""
    tasks = goal.tasks
    total_tasks = len(tasks)
    completed_tasks = sum(1 for task in tasks if task.completed)

    # Abzeichen: Anfänger (5 Aufgaben erledigt)
    if completed_tasks >= 5:
        existing_badge = Badge.query.filter_by(goal_id=goal.id, name="Anfänger").first()
        if not existing_badge:
            new_badge = Badge(name="Anfänger", description="5 Aufgaben erledigt!", goal_id=goal.id)
            db.session.add(new_badge)
            flash(f"Glückwunsch! Du hast das 'Anfänger'-Abzeichen für '{goal.title}' erhalten!", "success")
    else:
        existing_badge = Badge.query.filter_by(goal_id=goal.id, name="Anfänger").first()
        if existing_badge:
            db.session.delete(existing_badge)
            flash(f"'Anfänger'-Abzeichen für '{goal.title}' entfernt.", "info")

    # Abzeichen: Meister (100% Fortschritt)
    if goal.progress >= 100:
        existing_badge = Badge.query.filter_by(goal_id=goal.id, name="Meister").first()
        if not existing_badge:
            new_badge = Badge(name="Meister", description="Ziel zu 100% abgeschlossen!", goal_id=goal.id)
            db.session.add(new_badge)
            flash(f"Glückwunsch! Du hast das 'Meister'-Abzeichen für '{goal.title}' erhalten!", "success")
    else:
        existing_badge = Badge.query.filter_by(goal_id=goal.id, name="Meister").first()
        if existing_badge:
            db.session.delete(existing_badge)
            flash(f"'Meister'-Abzeichen für '{goal.title}' entfernt.", "info")

    # Abzeichen: Marathon (3 aufeinanderfolgende Tage mit erledigten Aufgaben)
    completed_dates = [task.completed_at.date() for task in tasks if task.completed and task.completed_at]
    marathon_qualified = False
    if completed_dates:
        unique_dates = sorted(set(completed_dates))
        consecutive_days = 1
        for i in range(1, len(unique_dates)):
            if (unique_dates[i] - unique_dates[i-1]).days == 1:
                consecutive_days += 1
            else:
                consecutive_days = 1
            if consecutive_days >= 3:
                marathon_qualified = True
                existing_badge = Badge.query.filter_by(goal_id=goal.id, name="Marathon").first()
                if not existing_badge:
                    new_badge = Badge(name="Marathon", description="Aufgaben an 3 aufeinanderfolgenden Tagen erledigt!", goal_id=goal.id)
                    db.session.add(new_badge)
                    flash(f"Glückwunsch! Du hast das 'Marathon'-Abzeichen für '{goal.title}' erhalten!", "success")
                break
    if not marathon_qualified:
        existing_badge = Badge.query.filter_by(goal_id=goal.id, name="Marathon").first()
        if existing_badge:
            db.session.delete(existing_badge)
            flash(f"'Marathon'-Abzeichen für '{goal.title}' entfernt.", "info")

    # Abzeichen: Schnellstarter (Aufgabe innerhalb von 24 Stunden nach Zielerstellung erledigt)
    schnellstarter_qualified = False
    for task in tasks:
        if task.completed and task.completed_at and goal.created_at:
            time_diff = task.completed_at - goal.created_at
            if time_diff.total_seconds() <= 24 * 3600:
                schnellstarter_qualified = True
                existing_badge = Badge.query.filter_by(goal_id=goal.id, name="Schnellstarter").first()
                if not existing_badge:
                    new_badge = Badge(name="Schnellstarter", description="Aufgabe innerhalb von 24 Stunden erledigt!", goal_id=goal.id)
                    db.session.add(new_badge)
                    flash(f"Glückwunsch! Du hast das 'Schnellstarter'-Abzeichen für '{goal.title}' erhalten!", "success")
                break
    if not schnellstarter_qualified:
        existing_badge = Badge.query.filter_by(goal_id=goal.id, name="Schnellstarter").first()
        if existing_badge:
            db.session.delete(existing_badge)
            flash(f"'Schnellstarter'-Abzeichen für '{goal.title}' entfernt.", "info")

    db.session.commit()

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
        check_badges(goal)
        return redirect(url_for('index'))
    return render_template('task_form.html', goal=goal)

@app.route('/toggle_task/<int:task_id>', methods=['POST'])
def toggle_task(task_id):
    task = Task.query.get_or_404(task_id)
    task.completed = not task.completed
    if task.completed:
        task.completed_at = datetime.utcnow()
    else:
        task.completed_at = None
    goal = task.goal
    tasks = goal.tasks
    total_tasks = len(tasks)
    completed_tasks = sum(1 for task in tasks if task.completed)
    goal.progress = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
    db.session.commit()
    check_badges(goal)
    return redirect(url_for('index'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5005)