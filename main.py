import json
import random
import string
from pathlib import Path
from datetime import datetime
import os
from dotenv import load_dotenv

class Library:
    # manage database connection
    from pymongo import MongoClient
    MONGO_URI = os.getenv("MONGO_URI") 
    
    # Check if URI is available before connecting
    if not MONGO_URI:
        raise ValueError("MONGO_URI environment variable not set. Cannot connect to database.")

    client = MongoClient(MONGO_URI)
    db = client["librarymanage"]
    books_collection = db["book"]
    members_collection = db["members"]
    
    if Path("books.json").exists():
        with open("books.json", "r") as file:
            books = json.load(file)
    else:
        with open("books.json", "w") as file:
            json.dump([], file)        

    #
    def generate_id(Prefix ="B"):
        random_id =""
        for i in range(5):
            random_id += random.choice(string.ascii_uppercase + string.digits)
            
        return Prefix + "-" + random_id
    
        
    def add_book(self):
        title = input("Enter book title: ")
        author = input("Enter book author: ")
        copies = int(input("Enter number of copies: "))
        book ={
            "id":Library.generate_id(),
            "title": title,
            "author": author,
            "copies": copies,
            "available_copies": copies,
            "addd_on": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        books_collection = Library.books_collection
        books_collection.insert_one(book)
        print("Book added successfully:", book)
    
    def list_books(self):
    # 1. Check for documents using a quick count first.
    # Note: Use count_documents({}) for large collections or if the estimate is inaccurate.
        if library.books_collection.count_documents({}) == 0:
            print("No books available.")
            return
        
        
        print(f"{'ID':<12} {'Title':<25} {'Author':<20} {'Total Copies':<12} {'Available Copies':<16}")
        print("-" * 100)
    
    # 2. Re-run the find() method immediately before the loop
    # to get a fresh cursor for iteration.
        books_cursor = library.books_collection.find({})
    
        for book in books_cursor:
        # Use .get() for safety against missing keys
            book_id = book.get('id', 'N/A')
            title = book.get('title', 'N/A')
            author = book.get('author', 'N/A')
            copies = book.get('copies', 'N/A')
            available_copies = book.get('available_copies', 'N/A')
        
        # Print the formatted output
        print(
            f"{str(book_id):<12} "
            f"{str(title)[:24]:<25} "
            f"{str(author)[:19]:<20} "
            f"{str(copies):<12} "
            f"{str(available_copies):<16}"
        ) 
   
    print()
    def add_member(self):
        name = input("Enter member name: ")
        email = input("Enter member email: ")
        member ={
            "id":Library.generate_id("M"),
            "name": name,
            "email": email,
            "joined_on": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "borrowed":[]
            
             
        }
        members_collection = Library.db["members"]
        members_collection.insert_one(member)
        print("Member added successfully:", member)
       
    def list_members(self):
        if not Library.members_collection.count_documents({}):
            print("No members available.")
            return
        else:
            for m in Library.members_collection.find({}):
                print(f"ID: {m['id']:12}, Name: {m['name'][:24]:25}, Email: {m['email'][:29]:30}, Joined On: {m['joined_on']}")
                print("this guy has borrowed these books")
                print(f"{'Book ID':<12} {'Title':<25} {'Borrowed On':<20} ")
                
    def borrow_book(self):
        member_id = input("enter the member ID").strip()
        members =[m for m in Library.members_collection.find({"id":member_id}) if m['id']==member_id]
        if not members:
            print("member not found")
            return
        member = members[0]
        book_id = input("enter the book ID").strip()
        books =[b for b in Library.books_collection.find({"id":book_id}) if b['id']==book_id]
        if not books:
            print("book not found")
            return
        book = books[0]
        if book['available_copies'] <=0:
            print("no copies available")
            return
        borrow_record ={
            "book_id": book['id'],
            "title": book['title'],
            "borrowed_on": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
        member['borrowed'].append(borrow_record)
        book['available_copies'] -=1
        Library.members_collection.update_one({"id":member['id']},{"$set":{"borrowed":member['borrowed']}})
        Library.books_collection.update_one({"id":book['id']},{"$set":{"available_copies":book['available_copies']}})
        print("book borrowed successfully")
     
    def return_book(self):
        member_id = input("enter the member ID").strip()
        members=[m for m in Library.members_collection.find({"id":member_id}) if m['id']==member_id]
        if not members:
            print("member not found")
            return
        member = members[0]
        if member['borrowed']==[]:
            print("this member has not borrowed any book")
            return
        print("borrowed books:")
        for i,b in enumerate (member['borrowed'],start=1):
            print(f"{i}. {b['title']} (ID: {b['book_id']}) borrowed on {b['borrowed_on']}")
            
        try:
            choice = int(input("enter number of book to return: "))
            selected = member['borrowed'].pop(choice -1)
        except Exception as err:
            print("invalid choice", err)
        books =[b for b in Library.books_collection.find({"id":selected['book_id']}) if b['id']==selected['book_id']]
        if books:
            book = books[0]
            book['available_copies'] +=1
            Library.books_collection.update_one({"id":book['id']},{"$set":{"available_copies":book['available_copies']}})
            Library.members_collection.update_one({"id":member['id']},{"$set":{"borrowed":member['borrowed']}})
            print("book returned successfully")    
            
            
                    
                    
        
        

    
while True:

    print("="*50)
    print("Library Management System")
    print("="*50)
    print("1. Add Book")
    print("2. List Books")
    print("3. Add Member")
    print("4. List Members")
    print("5. Borrow Book")
    print("6. Return Book")
    print("0. Exit")
    print("="*50)

    choice = input("what task do you want")

    if choice == "1":
        library = Library()
        library.add_book()
    
    if choice == "2":
        library = Library()
        library.list_books() 
    if choice == "3":
        library = Library()
        library.add_member()   
    
    if choice == "4":
        library = Library()
        library.list_members() 
    
    if choice == "5": 
        library = Library()
        library.borrow_book() 
    
    if choice == "6":
        library = Library()
        library.return_boo()
        
    if choice == "0":
        print("Exiting the system. Goodbye!")
        exit(0)        
    
    
    
    