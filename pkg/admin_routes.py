from functools import wraps
from flask import render_template, abort, request, redirect, flash, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from pkg import app, csrf
from pkg.models import db, Admin, User, Categories


def login_required(f):
    @wraps(f)
    def check_login(*args, **kwargs):
        if session.get("adminonline") !=None:
            return f(*args, **kwargs)
        else:
            flash("You must be logged in to access this page", category="error")
            return redirect(url_for("admin_login"))
    return check_login

@app.route("/admin/login/", methods=['POST', 'GET'])
def admin_login():
    if request.method == "GET":
        return render_template('admin/login.html')
    else: #retrieve form data
        email=request.form.get('email')
        pwd=request.form.get('pwd')

        admin=db.session.query(Admin).filter(Admin.admin_username == email).first()
        if admin !=None: #Check password
            saved_pwd=admin.admin_pwd
            check=check_password_hash(saved_pwd,pwd)
            if check:
                session['adminonline']=admin.admin_id
                flash("Welcome!", category='success')
                return redirect(url_for('admin_dashboard')) #create this route
            else:
                flash("Invalid credentials", category='error')
                return redirect(url_for('admin_login'))
        else:
            flash("Invalid credentials", category='error')
            return redirect(url_for('admin_login'))

@app.route("/admin/logout/")
@login_required
def admin_logout():
    if session.get("adminonline") !=None:
        session.pop("adminonline", None)
    return redirect("/admin/login")

@app.route("/admin/dashboard/", methods=['GET', 'POST'])
@login_required
def admin_dashboard():
    allcategories=Categories.query.all()
    if request.method=='GET':
        return render_template("admin/dashboard.html", allcategories=allcategories)
    else:
        category=request.form.get('cat')
        
        newcategory=Categories(cat_name=category)
        db.session.add(newcategory)
        db.session.commit()
        flash('Category created successfully')
        return redirect('/admin/dashboard/')

@app.route('/delete_category/<int:category_id>')
@login_required
def delete_category(category_id):
    category = Categories.query.get_or_404(category_id)
    db.session.delete(category)
    db.session.commit()
    flash("Category Deleted Successfully")
    return redirect('/admin/dashboard/')

@app.route('/alladmin/')
@login_required
def alladmin():
    admins=Admin.query.all()
    return render_template("admin/admins.html", admins=admins)

@app.route('/allusers/')
@login_required
def allusers():
    users=User.query.all()
    if request.method == "GET":
        return render_template("admin/users.html", users=users)

@app.route('/makeadmin/<int:userid>')
@login_required
def make_admin(userid):
    fetchuser=User.query.get(userid)
    fetchadmin=Admin.query.filter(Admin.admin_userid==userid).first()
    if fetchadmin != None:
        flash("User is already an admin", category='error')
        return redirect("/allusers/")
    else:
        NewAdmin = Admin(admin_username=fetchuser.user_email, admin_pwd=fetchuser.user_password, admin_userid=userid)
        db.session.add(NewAdmin)
        db.session.commit()
        flash("User added as an admin, sucessfully")
        return redirect("/allusers/")
    
@app.route('/delete_admin/<int:adminid>')
@login_required
def delete_admin(adminid):
    fetchadmin=Admin.query.get(adminid)
    db.session.delete(fetchadmin)
    db.session.commit()
    flash("Admin removed sucessfully")
    return redirect("/alladmin/")

@app.route('/delete_user/<int:userid>')
@login_required
def delete_user(userid):
    fetchuser=User.query.get(userid)
    fetchadmin=Admin.query.filter(Admin.admin_userid==userid).first()
    if fetchadmin != None:
        db.session.delete(fetchadmin)
        db.session.delete(fetchuser)
        db.session.commit()
        flash("User deleted successfully", category='error')
        return redirect("/allusers/")
    else:
        db.session.delete(fetchuser)
        db.session.commit()
        flash("User deleted successfully", category='error')
        return redirect("/allusers/")

@app.route("/admin/")
def admin():
    return redirect('/admin/login/')