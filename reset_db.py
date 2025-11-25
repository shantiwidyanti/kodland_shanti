
import os
from app import app, db
from models import Question


db_path = 'quiz.db'
if os.path.exists(db_path):
    os.remove(db_path)
    print(f"Database lama ({db_path}) dihapus.")


with app.app_context():
    db.create_all()
    print("Database baru dibuat.")
    
    
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
    
 
    count = Question.query.count()
    print(f"Total {count} pertanyaan baru berhasil di-seed.")
    
    print("\n✓ Database reset selesai!")
    print("Sekarang jalankan: python app.py")
