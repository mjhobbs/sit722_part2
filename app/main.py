from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy import create_engine, Column, Integer, String, MetaData, Table
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
from typing import List
import os
from pydantic import BaseModel
from typing import Optional

# PostgreSQL database connection string (replace with your PostgreSQL connection string)
DATABASE_URL = os.environ.get('DATABASE_URL') or "postgresql://admin:E5OJuKRE14iotwfsvHwJeqsjaKK1eKmO@dpg-cq0nb2aju9rs73b0500g-a.oregon-postgres.render.com/part2"

# Initialize FastAPI app
app = FastAPI()

# SQLAlchemy database engine and session
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Define database schema
class Book(Base):
    __tablename__ = "books"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    author = Column(String, index=True)
    year = Column(Integer)

# Create tables if they do not exist
Base.metadata.create_all(bind=engine)

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class BookBase(BaseModel):
    title: str
    author: str
    year: int

class BookCreate(BookBase):
    pass

class BookUpdate(BookBase):
    pass

class BookInDB(BookBase):
    id: int

    class Config:
        orm_mode = True


# Endpoint to create a new book
@app.post("/books/", response_model=BookInDB)
def create_book(book: BookCreate, db: Session = Depends(get_db)):
    db_book = Book(**book.dict())
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    return db_book

# Endpoint to retrieve a book by ID
@app.get("/books/{book_id}", response_model=BookInDB)
def get_book(book_id: int, db: Session = Depends(get_db)):
    db_book = db.query(Book).filter(Book.id == book_id).first()
    if db_book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return db_book

# Endpoint to retrieve all books
@app.get("/books/", response_model=List[BookInDB])
def get_all_books(db: Session = Depends(get_db)):
    return db.query(Book).all()

# Endpoint to update a book by ID
@app.put("/books/{book_id}", response_model=BookInDB)
def update_book(book_id: int, book: BookUpdate, db: Session = Depends(get_db)):
    db_book = db.query(Book).filter(Book.id == book_id).first()
    if db_book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    for field, value in book.dict().items():
        setattr(db_book, field, value)
    db.commit()
    db.refresh(db_book)
    return db_book

# Endpoint to delete a book by ID
@app.delete("/books/{book_id}", response_model=BookInDB)
def delete_book(book_id: int, db: Session = Depends(get_db)):
    db_book = db.query(Book).filter(Book.id == book_id).first()
    if db_book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    db.delete(db_book)
    db.commit()
    return db_book
