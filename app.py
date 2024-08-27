from flask import Flask, request, redirect, url_for, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime, timedelta

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///expenses.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)

class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(50))
    amount = db.Column(db.Float)
    date = db.Column(db.Date)
    time = db.Column(db.Time)

    def __repr__(self):
        return f'<Expense {self.category}>'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/add', methods=['GET', 'POST'])
def add_expense():
    if request.method == 'POST':
        category = request.form['category']
        amount = request.form['amount']
        date = request.form['date']
        time = request.form['time']

        new_expense = Expense(
            category=category,
            amount=amount,
            date=datetime.strptime(date, '%Y-%m-%d').date(),
            time=datetime.strptime(time, '%H:%M').time()
        )
        db.session.add(new_expense)
        db.session.commit()
        return redirect(url_for('index'))

    return render_template('add_expense.html')

@app.route('/view/daily')
def view_daily_expenses():
    today = datetime.today().date()
    expenses = Expense.query.filter_by(date=today).all()
    total_amount = sum(expense.amount for expense in expenses)
    return render_template('daily_expenses.html', expenses=expenses, total_amount=total_amount)

@app.route('/view/weekly')
def view_weekly_expenses():
    today = datetime.today().date()
    start_date = today - timedelta(days=today.weekday())
    end_date = start_date + timedelta(days=6)
    expenses = Expense.query.filter(Expense.date.between(start_date, end_date)).all()
    total_amount = sum(expense.amount for expense in expenses)
    return render_template('weekly_expenses.html', expenses=expenses, total_amount=total_amount)

@app.route('/view/monthly')
def view_monthly_expenses():
    today = datetime.today().date()
    start_date = today.replace(day=1)
    next_month = (today.replace(day=28) + timedelta(days=4)).replace(day=1)
    end_date = next_month - timedelta(days=1)
    expenses = Expense.query.filter(Expense.date.between(start_date, end_date)).all()
    total_amount = sum(expense.amount for expense in expenses)
    return render_template('monthly_expenses.html', expenses=expenses, total_amount=total_amount)

@app.route('/delete/<int:id>')
def delete_expense(id):
    expense = Expense.query.get_or_404(id)
    db.session.delete(expense)
    db.session.commit()
    return redirect(url_for('view_daily_expenses'))

if __name__ == '__main__':
    app.run(debug=True)
