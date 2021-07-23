import pandas as pd
from vocasta import db
from flask_login import UserMixin
from datetime import datetime
import sqlite3

# database = sqlite3.connect("vocasta.db")
# df = pd.read_sql_query("SELECT*FROM word", database)
# database.close()
# df.to_csv("word.csv", index=False)


class StudyLog(db.Model):
    __tablename__ = 'study_log'
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    word_id = db.Column(db.Integer, db.ForeignKey('word.id'))
    num_of_learning = db.Column(db.Integer, default=1)
    num_of_remember = db.Column(db.Integer, default=0)
    initial_created_time = db.Column(db.DateTime, default=datetime.utcnow)
    updated_time = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    word = db.relationship("Word")


class User(UserMixin, db.Model):
    __tablename__ = 'user'
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(300), unique=True, nullable=False)
    password = db.Column(db.String(300), nullable=False)
    study_logs = db.relationship("StudyLog", backref="user")


class Word(db.Model):
    __tablename__ = 'word'
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    lang_name = db.Column(db.String(5), nullable=False)
    word = db.Column(db.String(50), nullable=False)
    japanese = db.Column(db.String(50), nullable=False)


def get_data(lang_name: str) -> list:
    df = pd.read_csv(f"{lang_name}.csv")
    print(f"Successfully Loaded Language: {lang_name}.")
    return df.to_dict(orient="records")


def get_data_from_db(lang_name: str) -> list:
    """Return Word List Retrieved From Database
    :rtype: object
    """
    data_list = db.session.query(Word).filter_by(lang_name=lang_name).all()
    if data_list:
        print(f"Successfully Loaded Language: {lang_name}")
        return [{f"{lang_name}": row.word, "ja": row.japanese, "word_id": row.id} for row in data_list]
    else:
        raise FileNotFoundError("NoneDataError")


# # -----データベースをリセットして作り直す時の記述-----
db.drop_all()
print("database dropped")
db.create_all()


# # ------------CSVデータをデータベースに移行する記述---------------------
def append_word_data_to_db(lang_list: list):
    for lang in lang_list:
        word_list = get_data(lang)
        for word_dict in word_list:
            db_row = Word()
            db_row.lang_name = lang
            db_row.word = word_dict[lang]
            db_row.japanese = word_dict["ja"]
            db.session.add(db_row)
            db.session.commit()
        print(f"Successfully Added {lang} to the Database.")


# append_word_data_to_db(["en", "fr", "zh", "es", "ko"])
# ---------------------------------------------------------------
