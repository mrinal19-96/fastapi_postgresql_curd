from models import Book
from sqlalchemy.orm import Session
from schemas import BookCreate


def create_book(db: Session, data: BookCreate):
    Books_obj = Book(**data.model_dump())
    db.add(Books_obj)
    db.commit()
    db.refresh(Books_obj)
    return Books_obj


def get_books(db: Session):
    return db.query(Book).all()

def get_book_by_id(db: Session, book_id: int):
    return db.query(Book).filter(Book.id == book_id).first()


def update_book(db: Session, book_id: int, data: BookCreate):
    book_query = db.query(Book).filter(Book.id == book_id).first()
    
    if book_query:
        for key, value in data.model_dump().items():
            setattr(book_query, key, value)
        db.commit()
        db.refresh(book_query)
        return book_query
    return None


def delete_book(db: Session, book_id: int):
    book_query = db.query(Book).filter(Book.id == book_id).first()
    
    if book_query:
        db.delete(book_query)
        db.commit()
        return True
    return False