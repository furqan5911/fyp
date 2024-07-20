from flask import render_template, request, redirect, url_for, session, flash

def login_user():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        
        if username == "admin" and password == "python@123":
            session['logged_in'] = True
            return redirect(url_for('home'))
        else:
            flash("Invalid credentials. Please try again.")
    
    return render_template("index.html")

def logout_user():
    session.pop('logged_in', None)
    return redirect(url_for('login'))
