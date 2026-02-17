# Smart Student Verification System using PRN and NLP

A complete Flask full-stack project for guard-friendly gate verification in colleges.

## Overview
- Guard authentication (`guard / guard123`)
- NLP PRN extraction from typed/voice text
- Student verification with photo and status badge
- Student CRUD (add, edit, delete, search)
- CSV import with strict header validation
- Multilingual UI (English, Hindi, Marathi)
- Verification logging to database and `logs/access.log`

## Setup
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Run
```bash
python db_init.py
python app.py
```
Open: `http://127.0.0.1:5000`

## Login
- Username: `guard`
- Password: `guard123`

## CSV Format
Header must be exactly:
```csv
prn,name,branch,year,section,email,phone,photo_url,status
```

### Import via script
```bash
python import_students.py students.csv
```

### Import via UI
- Login
- Go to **Import CSV**
- Upload `.csv`
- See success and row-level errors

## Demo Steps
1. Login as guard.
2. On dashboard type: `My PRN is 2401132002` and click verify.
3. Try microphone button and speak PRN.
4. Open Students section and test CRUD.
5. Use language dropdown to switch English/Hindi/Marathi.
6. Check recent logs and `logs/access.log`.
