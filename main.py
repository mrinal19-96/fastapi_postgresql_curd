from fastapi import FastAPI, Depends, HTTPException
import services, models, schemas
from db import get_db, engine
from sqlalchemy.orm import Session

app = FastAPI()

@app.get('/books/', response_model=list[schemas.Book])
def get_all_books(db: Session = Depends(get_db)):
    return services.get_books(db)


@app.post('/books/', response_model=schemas.Book)
def create_new_book(book: schemas.BookCreate, db: Session = Depends(get_db)):
    
    new_book = services.create_book(db, book)
    return new_book

@app.get('/books/{book_id}', response_model=schemas.Book)
def get_book_by_id(book_id: int, db: Session = Depends(get_db)):
    book_query_set = services.get_book_by_id(db, book_id)
    if book_query_set:
        return book_query_set   
    
    raise HTTPException(status_code=404, detail="Book not found")


@app.put('/books/{book_id}', response_model=schemas.Book)
def update_book(book_id: int, book: schemas.BookCreate, db: Session = Depends(get_db)):
    updated_book = services.update_book(db, book_id, book)
    if updated_book:
        return updated_book
    
    raise HTTPException(status_code=404, detail="Book not found")

@app.delete('/books/{book_id}')
def delete_book(book_id: int, db: Session = Depends(get_db)):
    result = services.delete_book(db, book_id)
    if result:
        return {"detail": "Book deleted successfully"}
    
    raise HTTPException(status_code=404, detail="Book not found")