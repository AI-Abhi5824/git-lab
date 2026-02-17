from app import app
from models import Guard, Student, db

DEMO_STUDENTS = [
    ("2401132001", "Aarav Patil", "Computer", "FY", "A", "aarav@example.com", "9876543201", "https://randomuser.me/api/portraits/men/11.jpg", "active"),
    ("2401132002", "Isha Kulkarni", "IT", "SY", "B", "isha@example.com", "9876543202", "https://randomuser.me/api/portraits/women/21.jpg", "active"),
    ("2401132003", "Rohan Jadhav", "Mechanical", "TY", "A", "rohan@example.com", "9876543203", "https://randomuser.me/api/portraits/men/31.jpg", "blocked"),
    ("2401132004", "Sneha Deshmukh", "Civil", "FY", "C", "sneha@example.com", "9876543204", "https://randomuser.me/api/portraits/women/41.jpg", "active"),
    ("2401132005", "Aditya More", "Electronics", "SY", "A", "aditya@example.com", "9876543205", "https://randomuser.me/api/portraits/men/51.jpg", "active"),
    ("2401132006", "Neha Shinde", "Computer", "TY", "B", "neha@example.com", "9876543206", "https://randomuser.me/api/portraits/women/61.jpg", "blocked"),
    ("2401132007", "Omkar Pawar", "AI/DS", "FY", "A", "omkar@example.com", "9876543207", "https://randomuser.me/api/portraits/men/71.jpg", "active"),
    ("2401132008", "Pooja Kale", "IT", "SY", "C", "pooja@example.com", "9876543208", "https://randomuser.me/api/portraits/women/81.jpg", "active"),
    ("2401132009", "Sahil Gaikwad", "Mechanical", "TY", "C", "sahil@example.com", "9876543209", "https://randomuser.me/api/portraits/men/91.jpg", "active"),
    ("2401132010", "Tanvi Joshi", "Civil", "FY", "B", "tanvi@example.com", "9876543210", "https://randomuser.me/api/portraits/women/12.jpg", "active"),
]

with app.app_context():
    db.create_all()

    if not Guard.query.filter_by(username="guard").first():
        db.session.add(Guard(username="guard", password="guard123"))

    for row in DEMO_STUDENTS:
        if not Student.query.get(row[0]):
            db.session.add(
                Student(
                    prn=row[0],
                    name=row[1],
                    branch=row[2],
                    year=row[3],
                    section=row[4],
                    email=row[5],
                    phone=row[6],
                    photo_url=row[7],
                    status=row[8],
                )
            )

    db.session.commit()
    print("Database initialized with demo guard and 10 students.")
