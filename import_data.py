import csv
from database import db, Word, app

def import_words():
    with app.app_context():
        db.create_all()
        with open('words.csv', 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                word_entry = Word(word=row['word'], meaning=row['meaning'], example=row['example'], az=row['az'], ru=row['ru'], tr=row['tr'])
                db.session.add(word_entry)
            db.session.commit()
        print("Data Imported Successfully")

if __name__ == "__main__":
    import_words()
