from ... import db

def sql_commit():
    db.session.commit()

def sql_rollback():
    db.session.rollback()