# database.py
import os
import random
import string
from datetime import datetime
from pymongo import MongoClient
from dotenv import load_dotenv

# Load environment variables (Make sure your .env file is set up!)
load_dotenv()

class LibraryDB:
    # --- 1. Database Connection and Setup ---
    MONGO_URI = os.getenv("MONGO_URI") 
    
    if not MONGO_URI:
        raise ValueError("MONGO_URI environment variable not set. Cannot connect to database.")

    client = MongoClient(MONGO_URI)
    db = client["librarymanage"]
    books_collection = db["book"]
    members_collection = db["members"]

    # --- 2. Utility Functions ---
    @staticmethod
    def generate_id(prefix="B"):
        random_id = "".join(random.choice(string.ascii_uppercase + string.digits) for _ in range(5))
        return prefix + "-" + random_id

    # --- 3. Book Management Methods ---
    def add_book(self, title, author, copies):
        """Adds a new book document to the database."""
        book = {
            "id": self.generate_id("B"),
            "title": title,
            "author": author,
            "copies": copies,
            "available_copies": copies,
            "added_on": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self.books_collection.insert_one(book)
        return book

    def list_books(self):
        """Returns a list of all books from the database."""
        books_cursor = self.books_collection.find({})
        
        # Convert cursor to list for easy use in Streamlit
        return list(books_cursor)

    # --- 4. Member Management Methods ---
    def add_member(self, name, email):
        """Adds a new member document to the database."""
        member = {
            "id": self.generate_id("M"),
            "name": name,
            "email": email,
            "joined_on": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "borrowed": []
        }
        self.members_collection.insert_one(member)
        return member

    def list_members(self):
        """Returns a list of all members from the database."""
        members_cursor = self.members_collection.find({})
        return list(members_cursor)

    # --- 5. Transaction Methods (Modified to use arguments) ---
    def borrow_book(self, member_id, book_id):
        # 1. Find member and book
        member = self.members_collection.find_one({"id": member_id})
        book = self.books_collection.find_one({"id": book_id})

        if not member: return "Member not found."
        if not book: return "Book not found."
        if book['available_copies'] <= 0: return "No copies available."

        # 2. Update records
        borrow_record = {
            "book_id": book['id'],
            "title": book['title'],
            "borrowed_on": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # Atomically update DB records
        self.members_collection.update_one(
            {"id": member_id}, 
            {"$push": {"borrowed": borrow_record}}
        )
        self.books_collection.update_one(
            {"id": book_id}, 
            {"$inc": {"available_copies": -1}}
        )
        return f"Book '{book['title']}' borrowed successfully by {member['name']}."

    def return_book(self, member_id, book_id):
        # 1. Find member and book
        member = self.members_collection.find_one({"id": member_id})
        book = self.books_collection.find_one({"id": book_id})

        if not member: return "Member not found."
        if not book: return "Book not found."

        # Check if book is actually borrowed
        borrowed_books = [b for b in member.get('borrowed', []) if b['book_id'] == book_id]
        if not borrowed_books: return f"Member has not borrowed book ID {book_id}."
        
        # 2. Update records
        self.members_collection.update_one(
            {"id": member_id},
            {"$pull": {"borrowed": {"book_id": book_id}}} # $pull removes the item from the array
        )
        self.books_collection.update_one(
            {"id": book_id},
            {"$inc": {"available_copies": 1}}
        )
        return f"Book '{book['title']}' returned successfully."
    
    # Inside LibraryDB class in database.py
def get_recommendations(self, member_id):
    # 1. Get the member's previously borrowed book titles/genres
    member = self.members_collection.find_one({"id": member_id})
    if not member or not member.get('borrowed'):
         return "Please borrow a book first for personalized recommendations."

    # Example using the last borrowed book title:
    last_title = member['borrowed'][-1]['title']

    # 2. Use a simple text-matching/embedding service (or a pre-trained model)
    # Placeholder for actual AI logic:
    # For a professional setup, you'd use embeddings (vector search) here.
    recommended_books = self.books_collection.find(
        {"title": {"$ne": last_title}} # Find books with a different title
    ).limit(3)

    # Simple AI-like output
    titles = [b['title'] for b in recommended_books]
    return f"Based on your last read, '{last_title}', we recommend: {', '.join(titles)}"