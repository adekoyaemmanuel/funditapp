from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
      
class User(db.Model):  
    user_id = db.Column(db.Integer, autoincrement=True,primary_key=True)
    user_fname = db.Column(db.String(100),nullable=False)
    user_lname = db.Column(db.String(100),nullable=False)
    user_email = db.Column(db.String(120),nullable=False, unique=True) 
    user_password=db.Column(db.String(255),nullable=False) 
    user_pix=db.Column(db.String(120),nullable=True) 
    user_datereg=db.Column(db.DateTime(), default=datetime.utcnow)

    mybudgetdeets = db.relationship("Budget", backref="users")
    myexpensedeets = db.relationship("Expense", backref="userr")

class Expense(db.Model):  
    expense_id = db.Column(db.Integer, autoincrement=True,primary_key=True)
    expense_userid = db.Column(db.Integer, db.ForeignKey('user.user_id'))
    expense_itemid = db.Column(db.Integer, db.ForeignKey('budget_item.item_id', ondelete='CASCADE'))
    expense_amount= db.Column(db.Float,nullable=False)
    expense_desc= db.Column(db.String(200),nullable=False)
    expense_date=db.Column(db.DateTime(), default=datetime.utcnow)

    expenseitem_deets = db.relationship("BudgetItem", back_populates="expense_deets")

class Budget(db.Model):  
    budget_id = db.Column(db.Integer, autoincrement=True,primary_key=True)
    budget_userid = db.Column(db.Integer, db.ForeignKey('user.user_id'))
    budget_name = db.Column(db.String(100),nullable=False, unique=True)
    current_income = db.Column(db.Float,nullable=False)
    start_date = db.Column(db.DateTime(), default=datetime.utcnow)#default date
    end_date = db.Column(db.DateTime())

    items = db.relationship("BudgetItem", back_populates="budget")

class Categories(db.Model):  
    cat_id = db.Column(db.Integer, autoincrement=True,primary_key=True)
    cat_name = db.Column(db.String(100),nullable=False)

    itemcat=db.relationship("BudgetItem", back_populates="catego")

class BudgetItem(db.Model):  
    item_id = db.Column(db.Integer, autoincrement=True,primary_key=True)
    item_budgetid = db.Column(db.Integer, db.ForeignKey('budget.budget_id', ondelete='CASCADE'), nullable=False)
    item_catid = db.Column(db.Integer, db.ForeignKey('categories.cat_id'), nullable=False)
    item_name = db.Column(db.String(100),nullable=False)
    item_amount = db.Column(db.Float,nullable=False)
    item_status= db.Column(db.Enum('1', '0'),nullable=False)
    

    catego=db.relationship("Categories", back_populates="itemcat")
    budget = db.relationship("Budget", back_populates="items")
    expense_deets = db.relationship("Expense", back_populates="expenseitem_deets")
    

class Admin(db.Model):
    admin_id=db.Column(db.Integer, autoincrement=True,primary_key=True)
    admin_username=db.Column(db.String(20),nullable=True)
    admin_pwd=db.Column(db.String(255),nullable=True)


