if (Test-Path db.sqlite3) { Remove-Item db.sqlite3 }
python manage.py migrate
python scripts\seed_data.py