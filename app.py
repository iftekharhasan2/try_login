from flask import Flask, render_template, url_for, request, session, redirect
from datetime import datetime ,timedelta
import os
import pymongo
import bcrypt

app = Flask(__name__)
app.secret_key = "testing"

def MongoDB():
    client = pymongo.MongoClient("mongodb+srv://ifty:sCp6ZkEsSrg4Lz4O@ifty3656.qh27v.mongodb.net/")
    db = client.get_database('total_records')
    records = db.register
    return records
records = MongoDB()

@app.route("/", methods=['POST', 'GET'])
def index():
    message = ''
    if "email" in session:
        return redirect(url_for("logged_in"))
    if request.method == "POST":
        user = request.form.get("fullname")
        email = request.form.get("email")
        password1 = request.form.get("password1")
        password2 = request.form.get("password2")
        user_found = records.find_one({"name": user})
        email_found = records.find_one({"email": email})
        if user_found:
            message = 'There already is a user by that name'
            return render_template('index.html', message=message)
        if email_found:
            message = 'This email already exists in database'
            return render_template('index.html', message=message)
        if password1 != password2:
            message = 'Passwords should match!'
            return render_template('index.html', message=message)
        else:
            hashed = bcrypt.hashpw(password2.encode('utf-8'), bcrypt.gensalt())
            user_input = {'name': user, 'email': email, 'password': hashed}
            records.insert_one(user_input)
            user_data = records.find_one({"email": email})
            new_email = user_data['email']
            session["email"] = new_email
            return redirect(url_for("logged_in"))
    return render_template('index.html')

@app.route("/login", methods=["POST", "GET"])
def login():
    message = 'Please login to your account'
    if "email" in session:
        return redirect(url_for("logged_in"))

    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        #check if email exists in database
        email_found = records.find_one({"email": email})
        if email_found:
            email_val = email_found['email']
            passwordcheck = email_found['password']
            #encode the password and check if it matches
            if bcrypt.checkpw(password.encode('utf-8'), passwordcheck):
                session["email"] = email_val
                return redirect(url_for('logged_in'))
            else:
                message = 'Wrong password'
                return render_template('login.html', message=message)
        else:
            message = 'Email not found'
            return render_template('login.html', message=message)
    return render_template('login.html', message=message)

@app.route('/logged_in')
def logged_in():
    if "email" in session:
        email = session["email"]
        return render_template('logged_in.html', email=email)
    else:
        return redirect(url_for("login"))

@app.route("/logout", methods=["POST", "GET"])
def logout():
    if "email" in session:
        session.pop("email", None)
        return redirect(url_for("index"))
    else:
        return redirect(url_for("index"))




@app.route('/subscribe', methods=['GET', 'POST'])
def subscribe():
    message = ""
    message1 = ""
    message2 = ""
    current_time = datetime.now().strftime("%d-%m-%Y")  # Get current date and time
    if request.method == 'POST':
        message1 = f" You are subcribed"
        message = f"Subcribe date is {current_time}"
        future_time = datetime.now() + timedelta(days=30) #Set the expiry date here by adding days
        message2 = f" Expiry date is {future_time.strftime('%d-%m-%Y')}"
        
    return render_template('subscribe.html', message=message, message2=message2 ,message1=message1)




UPLOAD_FOLDER = 'uploaded_videos'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/video', methods=['GET', 'POST'])
def video():
    if request.method == 'POST':
        if 'video' not in request.files:
            return "No file part"
        file = request.files['video']
        if file.filename == '':
            return "No selected file"
        if file:
            save_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(save_path)
            return f"Video saved to {save_path}"
    return render_template('video.html')

if __name__ == '__main__':
    app.run(debug=False)