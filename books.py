from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
import models
from database import engine, SessionLocal

app = FastAPI()

# Create database tables
models.Base.metadata.create_all(bind=engine)

# --------------------------
#     DATABASE SESSION
# --------------------------
def get_db():
    db = SessionLocal()    # FIXED: correct DB session
    try:
        yield db
    finally:
        db.close()


# --------------------------
#     PYDANTIC MODEL
# --------------------------
class BookCreate(BaseModel):
    title: str = Field(min_length=1)
    author: str = Field(min_length=1, max_length=180)
    description: str = Field(min_length=1, max_length=100)
    rating: int = Field(gt=-1, lt=101)


# --------------------------
#     ROUTES
# --------------------------

# Get all books
@app.get("/")
def read_books(db: Session = Depends(get_db)):
    return db.query(models.Book).all()     # FIXED: query, not querry


# Create a book
@app.post("/")
def create_book(book: BookCreate, db: Session = Depends(get_db)):
    book_model = models.Book(
        title=book.title,
        author=book.author,
        description=book.description,
        rating=book.rating
    )
    db.add(book_model)
    db.commit()
    db.refresh(book_model)
    return book_model


# Update an existing book
@app.put("/{book_id}")
def update_book(book_id: int, book: BookCreate, db: Session = Depends(get_db)):

    book_model = db.query(models.Book).filter(models.Book.id == book_id).first()

    if book_model is None:
        raise HTTPException(status_code=404, detail=f"Book with ID {book_id} not found")

    book_model.title = book.title
    book_model.author = book.author
    book_model.description = book.description
    book_model.rating = book.rating

    db.commit()
    db.refresh(book_model)
    return book_model


# Delete a book
@app.delete("/{book_id}")
def delete_book(book_id: int, db: Session = Depends(get_db)):
    book_model = db.query(models.Book).filter(models.Book.id == book_id).first()

    if book_model is None:
        raise HTTPException(status_code=404, detail=f"Book with ID {book_id} not found")

    db.delete(book_model)
    db.commit()

    return {"message": f"Book with ID {book_id} deleted successfully"}

# https://www.youtube.com/watch?v=QkGqjPFIGCA&list=PLK8U0kF0E_D6l19LhOGWhVZ3sQ6ujJKq_&index=4
