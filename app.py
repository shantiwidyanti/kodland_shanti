from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user, UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, Question
import requests
from datetime import datetime
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///quiz.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your_secret_key_here'
db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/', methods=['GET', 'POST'])
def index():
    city = request.args.get('city')
    forecast = None
    # Ini dari https://openweathermap.org/api menggunakan akunku sendiri (harus masukin kotanya itu huruf kapital di awal cth : Jakarta)
    if city:
       
        api_key = os.getenv('OPENWEATHER_API_KEY', 'db08caf317d28da122d4f68c0625ce1f')
        if not os.getenv('OPENWEATHER_API_KEY'):
            app.logger.warning('OPENWEATHER_API_KEY not set in environment please dont tamper the code and use the Set OPENWEATHER_API_KEY i had put.')
        url = f'https://api.openweathermap.org/data/2.5/forecast?q={city}&appid={api_key}&units=metric&lang=id'
        try:
            response = requests.get(url)
            data = response.json()
            if data.get('cod') == '200':
                days = {}
                for entry in data['list']:
                    date = entry['dt_txt'].split(' ')[0]
                    temp = entry['main']['temp']
                    desc = entry['weather'][0]['description']
                    icon = entry['weather'][0]['icon'] if 'icon' in entry['weather'][0] else None
                    hour = int(entry['dt_txt'].split(' ')[1][:2])
                    if date not in days:
                        days[date] = {'temps_day': [], 'temps_night': [], 'descs': [], 'icons': []}
                    if 6 <= hour <= 18:
                        days[date]['temps_day'].append(temp)
                    else:
                        days[date]['temps_night'].append(temp)
                    days[date]['descs'].append(desc)
                    days[date]['icons'].append(icon)
                forecast = []
                for i, (date, vals) in enumerate(days.items()):
                    if i >= 3:
                        break
                    dt = datetime.strptime(date, '%Y-%m-%d')
                    day_name = dt.strftime('%A')
                    temp_day = round(sum(vals['temps_day'])/len(vals['temps_day'])) if vals['temps_day'] else '-'
                    temp_night = round(sum(vals['temps_night'])/len(vals['temps_night'])) if vals['temps_night'] else '-'
                    description = max(set(vals['descs']), key=vals['descs'].count)
                    icon = max(set(vals['icons']), key=vals['icons'].count) if vals['icons'] else None
                    forecast.append({
                        'day_name': day_name,
                        'date': date,
                        'temp_day': temp_day,
                        'temp_night': temp_night,
                        'description': description,
                        'icon': icon
                    })
            else:
                flash('Kota tidak ditemukan, API ERROR, atau dipencarian Huruf awalnya tidak kapital (cth : Sydney S nya kapital).', 'error')
        except Exception as e:
            flash('Terjadi kesalahan saat mengambil data cuaca.', 'error')


    users = User.query.order_by(User.score.desc()).all()
    return render_template('index.html', city=city, forecast=forecast, users=users)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        login_name = request.form['login']
        nickname = request.form['nickname']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        if password != confirm_password:
            return render_template('register.html', error="Password tidak cocok.")
        if User.query.filter_by(login=login_name).first():
            return render_template('register.html', error="Login sudah digunakan.")
        if User.query.filter_by(nickname=nickname).first():
            return render_template('register.html', error="Nickname sudah digunakan.")
        password_hash = generate_password_hash(password)
        new_user = User(login=login_name, nickname=nickname, password_hash=password_hash)
        db.session.add(new_user)
        db.session.commit()
        flash('Registrasi berhasil! Silakan login.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        login_name = request.form['login']
        password = request.form['password']
        user = User.query.filter_by(login=login_name).first()
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for('quiz'))
        return render_template('login.html', error="Login atau password salah.")
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

 # Quiz logic di halaman home dihapus, quiz hanya di /quiz

@app.route('/quiz', methods=['GET', 'POST'])
@login_required
def quiz():
    user = current_user
    if request.method == 'POST':
   
        question_id = request.form.get('question_id')
        answer = request.form.get('answer')
        
        if question_id and answer:
            question = Question.query.get(int(question_id))
  
            if question and int(answer) == question.correct_option:
                user.score += 1
                db.session.commit()
        
        return redirect(url_for('quiz'))
    
    question = Question.query.order_by(db.func.random()).first()
    return render_template('quiz.html', user=user, question=question)

@app.route('/leaderboard')
def leaderboard():
    users = User.query.order_by(User.score.desc()).all()
    return render_template('leaderboard.html', users=users)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        if Question.query.count() == 0:
            q1 = Question(text="Apa itu Computer Vision?", option1="Teknologi untuk membuat robot", option2="Bidang AI yang fokus pada pemahaman gambar dan video", option3="Metode untuk menulis kode", option4="Aplikasi edit foto", correct_option=2)
            q2 = Question(text="Library Python populer untuk Computer Vision adalah?", option1="OpenCV", option2="Django", option3="NumPy saja", option4="Flask", correct_option=1)
            q3 = Question(text="NLP (Natural Language Processing) dalam Python biasanya menggunakan library?", option1="OpenCV", option2="NLTK dan spaCy", option3="TensorFlow saja", option4="Pandas", correct_option=2)
            q4 = Question(text="Siapa penemu bahasa pemrograman Python?", option1="Guido van Rossum", option2="Elon Musk", option3="Bill Gates", option4="Mark Zuckerberg", correct_option=1)
            q5 = Question(text="Framework mana yang paling populer untuk menerapkan AI di Python?", option1="TensorFlow dan PyTorch", option2="Django", option3="Flask", option4="Pandas", correct_option=1)
            q6 = Question(text="Apa singkatan dari AI?", option1="Automated Interface", option2="Artificial Intelligence", option3="Advanced Internet", option4="Automated Instruction", correct_option=2)
            q7 = Question(text="Library Python untuk machine learning dasar adalah?", option1="scikit-learn", option2="Django", option3="Flask", option4="BeautifulSoup", correct_option=1)
            q8 = Question(text="Apa kegunaan utama NumPy dalam AI/Machine Learning?", option1="Membuat website", option2="Komputasi array dan matrix numerik", option3="Database management", option4="Web scraping", correct_option=2)
            db.session.add_all([q1, q2, q3, q4, q5, q6, q7, q8])
            db.session.commit()
    app.run(debug=True)
