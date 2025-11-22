# streamlit_app.py
import streamlit as st
import pandas as pd
from database import LibraryDB # Import your core logic

# Initialize the database connector
try:
    db = LibraryDB()
except ValueError as e:
    st.error(f"Configuration Error: {e}")
    st.stop() # Stop the app if the connection fails

st.set_page_config(layout="wide", page_title="Classy Library Manager")

st.title("📚 University Library Management System")

# --- Sidebar Navigation ---
selection = st.sidebar.radio(
    "Navigation",
    ["📖 List Books", "➕ Add Book", "👥 List Members", "👤 Add Member", "🔄 Borrow/Return", "✨ AI Recommendation"]
)
st.sidebar.markdown("---")
st.sidebar.caption("Powered by MongoDB & Streamlit")

# --- Content Areas ---

if selection == "📖 List Books":
    st.header("Available Books")
    books_data = db.list_books()
    if books_data:
        # Select and rename columns for display
        df = pd.DataFrame(books_data)
        # Handle cases where columns might be missing
        display_cols = ['id', 'title', 'author', 'copies', 'available_copies']
        df_display = df.reindex(columns=display_cols).rename(columns={'id': 'Book ID', 'available_copies': 'Available'})
        st.dataframe(df_display, use_container_width=True)
    else:
        st.info("No books available in the library.")

elif selection == "➕ Add Book":
    st.header("Add New Book")
    with st.form("add_book_form"):
        title = st.text_input("Title", key="title_input")
        author = st.text_input("Author", key="author_input")
        copies = st.number_input("Number of Copies", min_value=1, value=1, step=1, key="copies_input")
        
        submitted = st.form_submit_button("Submit Book")
        
        if submitted and title and author:
            try:
                result = db.add_book(title, author, copies)
                st.success(f"Book **'{result['title']}'** added successfully! (ID: {result['id']})")
            except Exception as e:
                st.error(f"Error adding book: {e}")

elif selection == "🔄 Borrow/Return":
    st.header("Book Transactions")
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Borrow Book")
        with st.form("borrow_form"):
            member_id = st.text_input("Member ID")
            book_id = st.text_input("Book ID to Borrow")
            borrow_submitted = st.form_submit_button("Borrow")
            
            if borrow_submitted and member_id and book_id:
                message = db.borrow_book(member_id.strip(), book_id.strip())
                if "success" in message:
                    st.success(message)
                else:
                    st.warning(message)

    with col2:
        st.subheader("Return Book")
        with st.form("return_form"):
            member_id_r = st.text_input("Member ID for Return")
            book_id_r = st.text_input("Book ID to Return")
            return_submitted = st.form_submit_button("Return")
            
            if return_submitted and member_id_r and book_id_r:
                message = db.return_book(member_id_r.strip(), book_id_r.strip())
                if "success" in message:
                    st.success(message)
                else:
                    st.warning(message)

# NOTE: You would implement the rest of the navigation (Add Member, List Members, AI Recommendation) 
# following the pattern shown above.