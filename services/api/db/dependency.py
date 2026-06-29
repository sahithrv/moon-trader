from db.session import SessionLocal

def get_db():
    db = SessionLocal()

    try:
        yield db #used to temporarily provide a db sesion to caller, closes after the session is done
    finally:
        db.close()