Python SQLAlchemy
=================

SQLAlchemy allows defining models and their relationships which then
directly map to a database schema which can be automatically
generated. For example, three models::

class Budget(db.Model):
    month_year = db.Column(db.Date, primary_key=True)
    amount = db.Column(db.Numeric(20,6), nullable=False)

class Expense(db.Model):
    expense_id = db.Column(db.Integer, primary_key=True)
    entry_date = db.Column(db.Date, nullable=False)
    expense_category_id = db.Column(
        db.Integer,
        db.ForeignKey('expense_category.expense_category_id'),
        nullable=False)
    amount =
    db.Column(db.Numeric(20,6), nullable=False)
    memo = db.Column(db.String(100))
    expense_category = db.relationship(
        'ExpenseCategory',
        backref=db.backref('expense_category',
        lazy='dynamic'))

class ExpenseCategory(db.Model):
    expense_category_id = db.Column(db.Integer,
    primary_key=True)
   category_name = db.Column(db.String(100), nullable=False)
