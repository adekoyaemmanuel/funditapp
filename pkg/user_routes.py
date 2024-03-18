from datetime import datetime
import requests, json
import os, random, string
from functools import wraps
from flask import render_template ,request, redirect, flash, url_for, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from pkg import app, csrf
from pkg.models import db, User, Budget, BudgetItem, Categories, Expense


def login_required(f):
    @wraps(f)
    def check_login(*args, **kwargs):
        if session.get("useronline") !=None:
            return f(*args, **kwargs)
        else:
            flash("You must be logged in to access this page", category="error")
            return redirect(url_for("login"))
    return check_login


@app.route('/')
def onboarding_page():
    
    return render_template('user/onboarding.html')

@app.route('/about/')
def about_page():
    
    return render_template('user/about.html')

    

@app.route('/changedp/', methods=['POST', 'GET'])
@login_required
def change_dp():
    id=session.get('useronline')
    deets=User.query.get(id)
    budgets=Budget.query.filter(Budget.budget_userid==id).order_by(Budget.budget_id.desc()).slice(0, 10).all()
    oldpix=deets.user_pix
    if request.method == "GET":
        return render_template("user/changedp.html",deets=deets, budgets=budgets)
    else:
        dp=request.files.get("dp")
        filename=dp.filename 
        if filename=="":
            flash("Please select a file, category='error")
            return redirect('/changedp/')
        else:
            name, ext=os.path.splitext(filename)
            allowed=['.jpg', '.png', '.jpeg']
            if ext.lower() in allowed:
                final_name=int(random.random()*1000000)
                final_name=str(final_name)+ext 
                dp.save(f'pkg/static/profile/{final_name}')
                user=db.session.query(User).get(id) 
                user.user_pix=final_name
                db.session.commit()
                try:
                    os.remove(f"pkg/static/profile/{oldpix}")
                except:
                    pass
                
                flash("Profile picture added", category='success')
                return redirect('/dashboard') 
            else:
                flash("extension not allowed", category='error')
                return redirect("/changedp/")
        


@app.route('/profile/', methods=['POST', 'GET'])
@login_required
def user_profile():
    id=session.get("useronline")
    if request.method =='GET':
        deets=User.query.get(id)
        budgets=Budget.query.filter(Budget.budget_userid==id).order_by(Budget.budget_id.desc()).slice(0, 10).all()
        return render_template('user/profile.html', deets=deets, budgets=budgets)
    else:
        fname=request.form.get('fname')
        lname=request.form.get('lname')
        email=request.form.get('email')
        person=User.query.get(id)

        person.user_fname=fname
        person.user_lname=lname
        person.user_email=email
        db.session.commit()
        flash("Profile updated sucessfully", category='error')
        return redirect('/profile/')


@app.route('/dashboard/', methods=['POST', 'GET'])
@login_required
def user_dashboard():
    id=session.get('useronline')
    deets=User.query.get(id)
    budgetss=Budget.query.filter(Budget.budget_userid==id).all()
    budgets=Budget.query.filter(Budget.budget_userid==id).order_by(Budget.budget_id.desc()).slice(0, 10).all()
    expenses=Expense.query.filter(Expense.expense_userid==id).order_by(Expense.expense_id.desc()).slice(0, 10).all()
    if request.method == "GET":
        return render_template('user/dashboard.html', deets=deets, budgets=budgets, expenses=expenses, budgetss=budgetss)
    else:
        item_name = request.form.get('itemname')
        exp_amt = request.form.get('amt')
        exp_desc = request.form.get('desc')
        exp_date = request.form.get('dat')
        if item_name!='' and exp_amt!='' and exp_date!='':
            newexpense = Expense(expense_userid=id, expense_itemid=item_name, expense_amount=exp_amt, expense_date=exp_date, expense_desc=exp_desc)
            db.session.add(newexpense)
            db.session.commit()
            flash("Expense added successfully")
            expenses=Expense.query.filter(Expense.expense_userid==id).order_by(Expense.expense_id.desc()).slice(0, 10).all()
    return render_template('user/dashboard.html', deets=deets, budgets=budgets, expenses=expenses, budgetss=budgetss)

@app.route('/report/', methods=['POST', 'GET'])
@login_required
def report():
    id=session.get('useronline')
    deets=User.query.get(id)
    budgets=Budget.query.filter(Budget.budget_userid==id).order_by(Budget.budget_id.desc()).slice(0, 10).all()
    budgetss=Budget.query.filter(Budget.budget_userid==id).all()
    expenses=Expense.query.filter(Expense.expense_userid==id).all()
    if request.method == "GET":
        return render_template('user/report.html', deets=deets, budgets=budgets, budgetss=budgetss, expenses=expenses)
    else:
        budgett=request.form.get('budgetname')
        if budgett:
            fetchexpenses=[]
            for expense in expenses:
                if expense.expenseitem_deets:
                    if expense.expenseitem_deets.budget.budget_name == budgett:
                        fetchexpenses.append(expense)
            if fetchexpenses==[]:
                message="There are no expenses for the selected budget name."
                return render_template('user/report.html', deets=deets, budgets=budgets, budgetss=budgetss, message=message)
        return render_template('user/report.html', deets=deets, budgets=budgets, budgetss=budgetss, fetchexpenses=fetchexpenses, expenses=expenses)

@app.route('/budgetreport/', methods=['POST', 'GET'])
@login_required
def budgetreport():
    id=session.get('useronline')
    deets=User.query.get(id)
    budgets=Budget.query.filter(Budget.budget_userid==id).all()
    expenses=Expense.query.filter(Expense.expense_userid==id).all()
    if request.method == "GET":
        return render_template('user/budgetreport.html', deets=deets, budgets=budgets, expenses=expenses)
    else:
        budgettname=request.form.get('budgetname')
        if budgettname:
            budgetitem=BudgetItem.query.filter(BudgetItem.item_budgetid==budgettname).all()
            budgetitems=[]
            for item in budgetitem:
                print(item.item_name)
                if item.budget:
                    budgetitems.append(item)
        return render_template('user/budgetreport.html', deets=deets, budgets=budgets, budgetitems=budgetitems, expenses=expenses)

@app.route("/login/", methods=['POST', 'GET'])
def login():
    if request.method == 'GET':
     return render_template('user/login.html')
    else:
        #retrieve from database
        email=request.form.get('email')
        pwd=request.form.get('pwd')
        record=db.session.query(User).filter(User.user_email == email).first()
        if record:
            hashed_pwd=record.user_password
            rsp=check_password_hash(hashed_pwd, pwd)
            if rsp:
                id=record.user_id
                session['useronline']=id
                flash('Login Successful')
                return redirect(url_for('createbudget'))
            else:
                flash('Invalid Credentials', category='error')
                return redirect("/login")
        else:
            flash('Invalid Credentials', category='error')
            return redirect("/login")

@app.route("/logout/")
@login_required
def logout():
    if session.get("useronline") !=None:
        session.pop("useronline", None)
    return redirect("/login")

@app.route("/register/", methods=['POST', 'GET'])
def user_register():
    users=User.query.all()
    if request.method == 'GET':
        return render_template('user/register.html')
    else:
        fname=request.form.get('fname')
        lname=request.form.get('lname')
        email=request.form.get('email')
        pwd=request.form.get('pwd')
        confirmpwd=request.form.get('confirmpwd')
        hashed_pwd=generate_password_hash(pwd)
        if email !="" and fname !='' and lname !='' :
            allemail=[]
            for user in users:
                allemail.append(user.user_email)
            if email in allemail:
                flash ("Sorry, you have an account already", category="error")
                return redirect('/register/')
            else:
                if pwd == confirmpwd:
                    user=User(user_fname=fname, user_lname=lname, user_email=email, user_password=hashed_pwd)
                    db.session.add(user)
                    db.session.commit()
                    flash("Registration Successful")
                    return redirect(url_for("login"))
                else:
                    flash("Kindly check your password, it doesn't match", category="error")
                    return redirect(url_for("user_register"))
        else:
            flash("Some of the form fields are blank", category="error")
            return redirect(url_for("user_register"))

@app.route('/budget/', methods=['POST', 'GET'])
@login_required
def createbudget():
    id=session.get('useronline')
    deets=User.query.get(id)
    budgets=budgets=Budget.query.filter(Budget.budget_userid==id).order_by(Budget.budget_id.desc()).slice(0, 10).all()
    category=Categories.query.all()
    if request.method=='GET':
        return render_template('user/budget.html', deets=deets, category=category, budgets=budgets)
    else:
        budgetname = request.form['budget_name']
        currentincome = request.form['current_income']
        startdate = datetime.strptime(request.form['start_date'], '%Y-%m-%d').date()
        enddate = datetime.strptime(request.form['end_date'], '%Y-%m-%d').date()
        print(budgetname)
        newbudget = Budget(budget_userid=id, budget_name=budgetname, current_income=currentincome, start_date=startdate, end_date=enddate)
        
        db.session.add(newbudget)
        db.session.commit()

        item_names = request.form.getlist('item_name[]')
        item_statuses = request.form.getlist('item_status[]')
        item_categories = request.form.getlist('item_category[]')
        item_amounts = request.form.getlist('item_amount[]')
    
        for item_name, item_category, item_status, item_amount in zip(item_names, item_categories, item_statuses, item_amounts):
            newitem = BudgetItem(item_budgetid=newbudget.budget_id, item_catid=item_category, item_name=item_name, item_amount=item_amount, item_status=item_status)

            db.session.add(newitem)
            db.session.commit()
        flash("Budget Created Successfully")
        return render_template('user/budget.html', deets=deets, category=category, budgets=budgets)

@app.route('/budget/items/', methods=['POST'])
def get_items():
    budgetId = request.form.get("budgetId")
    budget = Budget.query.get_or_404(budgetId)
    items = budget.items
    item_data = []
    for item in items:
        item_data.append({"item_id":item.item_id, "item_name":item.item_name})
    return jsonify(item_data)

@app.route('/delete_budget/<int:budget_id>', methods=['GET', 'POST'])
@login_required
def delete_budget(budget_id):
    id=session.get('useronline')
    expenses=Expense.query.filter(Expense.expense_userid==id).all()
    fetchexpense=[]
    for expense in expenses:
        if expense.expenseitem_deets:
            if expense.expenseitem_deets.budget.budget_id == budget_id:
                fetchexpense.append(expense)
    for itemexpense in fetchexpense:
        db.session.delete(itemexpense)
        db.session.commit()

    budgetitems=BudgetItem.query.filter(BudgetItem.item_budgetid==budget_id).all()
    for budgetitem in budgetitems:
        db.session.delete(budgetitem)
        db.session.commit()

    budget = Budget.query.get_or_404(budget_id)
    db.session.delete(budget)
    db.session.commit()
    flash("Budget Deleted Successfully", category="error")
    return redirect(url_for('budgetreport'))

@app.route('/delete_expense/<int:expense_id>')
@login_required
def delete_expense(expense_id):
    expense = Expense.query.get_or_404(expense_id)
    db.session.delete(expense)
    db.session.commit()
    flash("Expense Deleted Successfully")
    return redirect(url_for('report'))

@app.route('/update_expense/<int:expense_id>', methods=['GET', 'POST'])
@login_required
def update_expense(expense_id):
    if request.method == 'GET':
        id=session.get('useronline')
        deets=User.query.get(id)
        budgetss=Budget.query.filter(Budget.budget_userid==id).all()
        expens = Expense.query.get_or_404(expense_id)
        return render_template('user/changeexpense.html', budgetss=budgetss, deets=deets, expens=expens)
    else:
        item_name = request.form.get('itemname')
        exp_amt = request.form.get('amt')
        exp_desc = request.form.get('desc')
        exp_date = request.form.get('dat')
        expense = Expense.query.get_or_404(expense_id)
        if item_name and exp_amt and exp_date:
            expense.expense_itemid=item_name
            expense.expense_amount=exp_amt
            expense.expense_date=exp_date
            expense.expense_desc=exp_desc
            db.session.commit()
            flash("Expense updated sucessfully")
            return redirect(url_for('report'))

@app.route('/update_budget/<int:budget_id>', methods=['GET', 'POST'])
@login_required
def update_budget(budget_id):
    id=session.get('useronline')
    deets=User.query.get(id)
    category=Categories.query.all()
    bud = Budget.query.get_or_404(budget_id)
    for b in bud.items:
        print(b.item_catid)
    if request.method == 'GET':
        return render_template('user/changebudget.html', category=category, deets=deets, bud=bud, budget_id=budget_id)
    else:
        budgetname = request.form['budget_name']
        currentincome = request.form['current_income']
        startdate = datetime.strptime(request.form['start_date'], '%Y-%m-%d').date()
        enddate = datetime.strptime(request.form['end_date'], '%Y-%m-%d').date()

        bud.budget_name=budgetname
        bud.current_income=currentincome
        bud.start_date=startdate
        bud.enddate=enddate
        db.session.commit()

        item_names = request.form.getlist('item_name[]')
        item_statuses = request.form.getlist('item_status[]')
        item_categories = request.form.getlist('item_category[]')
        item_amounts = request.form.getlist('item_amount[]')

        for i in range(len(item_names)):
            item = bud.items[i]
            item.item_catid = item_categories[i]
            item.item_name = item_names[i]
            item.item_amount = item_amounts[i]
            item.item_status = item_statuses[i]
            db.session.commit()
        flash("Budget updated sucessfully")
        return redirect(url_for('budgetreport'))


@app.route('/delete_item/<int:item_id>', methods=['POST'])
@login_required
def delete_item(item_id):
    id=session.get('useronline')
    expenses=Expense.query.filter(Expense.expense_userid==id).all()
    fetchexpense=[]
    for expense in expenses:
        if expense.expenseitem_deets:
            if expense.expenseitem_deets.item_id == item_id:
                fetchexpense.append(expense)
    for itemexpense in fetchexpense:
        db.session.delete(itemexpense)
        db.session.commit()

    budgetitem=BudgetItem.query.get_or_404(item_id)
    db.session.delete(budgetitem)
    db.session.commit()
    flash("item Deleted Successfully", category="error")
    return redirect(url_for('budgetreport'))


