#admin pwd = admin admin123    streamlit run app.py



# import streamlit as st
# import cv2
# import numpy as np
# import face_recognition
# import os
# import pickle
# import hashlib
# import sqlite3
# from PIL import Image
# from datetime import datetime
# import pandas as pd
# import io

# # Initialize database
# def init_db():
#     conn = sqlite3.connect('student_database.db', check_same_thread=False)
#     c = conn.cursor()
    
#     # Create users table for authentication
#     c.execute('''
#     CREATE TABLE IF NOT EXISTS users (
#         id INTEGER PRIMARY KEY AUTOINCREMENT,
#         username TEXT UNIQUE NOT NULL,
#         password TEXT NOT NULL,
#         role TEXT NOT NULL
#     )
#     ''')
    
#     # Create students table
#     c.execute('''
#     CREATE TABLE IF NOT EXISTS students (
#         id INTEGER PRIMARY KEY AUTOINCREMENT,
#         name TEXT NOT NULL,
#         roll_number TEXT UNIQUE NOT NULL,
#         department TEXT NOT NULL,
#         year INTEGER NOT NULL,
#         email TEXT,
#         phone TEXT,
#         address TEXT,
#         username TEXT UNIQUE,
#         face_encoding BLOB,
#         registration_date TEXT,
#         FOREIGN KEY(username) REFERENCES users(username)
#     )
#     ''')
    
#     # Insert default admin if not exists
#     c.execute("SELECT * FROM users WHERE username='admin' AND role='admin'")
#     if not c.fetchone():
#         hashed_pw = hashlib.sha256("admin123".encode()).hexdigest()
#         c.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", 
#                  ("admin", hashed_pw, "admin"))
    
#     conn.commit()
#     return conn

# # Password hashing function
# def hash_password(password):
#     return hashlib.sha256(password.encode()).hexdigest()

# # User authentication
# def authenticate(username, password, role):
#     conn = init_db()
#     c = conn.cursor()
#     hashed_pw = hash_password(password)
#     c.execute("SELECT * FROM users WHERE username=? AND password=? AND role=?", 
#              (username, hashed_pw, role))
#     user = c.fetchone()
#     conn.close()
#     return user is not None

# # Function to register new user
# def register_user(username, password, role):
#     conn = init_db()
#     c = conn.cursor()
#     try:
#         hashed_pw = hash_password(password)
#         c.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", 
#                  (username, hashed_pw, role))
#         conn.commit()
#         conn.close()
#         return True
#     except sqlite3.IntegrityError:
#         conn.close()
#         return False

# # Function to save student data with face encoding
# def save_student(name, roll_number, department, year, email, phone, address, username, face_encoding=None):
#     conn = init_db()
#     c = conn.cursor()
    
#     # Convert face encoding to binary for storage
#     encoding_blob = None
#     if face_encoding is not None:
#         encoding_blob = pickle.dumps(face_encoding)
    
#     try:
#         c.execute("""
#         INSERT INTO students (name, roll_number, department, year, email, phone, address, username, face_encoding, registration_date) 
#         VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
#         """, (name, roll_number, department, year, email, phone, address, username, encoding_blob, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
#         conn.commit()
#         conn.close()
#         return True
#     except sqlite3.IntegrityError as e:
#         conn.close()
#         return False

# # Function to get all students
# def get_all_students():
#     conn = init_db()
#     c = conn.cursor()
#     c.execute("SELECT id, name, roll_number, department, year, email, phone FROM students")
#     students = c.fetchall()
#     conn.close()
    
#     # Convert to DataFrame for nice display
#     df = pd.DataFrame(students, columns=['ID', 'Name', 'Roll Number', 'Department', 'Year', 'Email', 'Phone'])
#     return df

# # Function to get student by roll number
# def get_student_by_roll(roll_number):
#     conn = init_db()
#     c = conn.cursor()
#     c.execute("SELECT * FROM students WHERE roll_number=?", (roll_number,))
#     student = c.fetchone()
#     conn.close()
#     return student

# # Function to retrieve all face encodings for comparison
# def get_all_face_encodings():
#     conn = init_db()
#     c = conn.cursor()
#     c.execute("SELECT id, name, roll_number, department, year, face_encoding FROM students WHERE face_encoding IS NOT NULL")
#     students = c.fetchall()
#     conn.close()
    
#     # Create dictionary of {id: (encoding, student_info)}
#     encodings_dict = {}
#     for student in students:
#         student_id, name, roll_number, department, year, encoding_blob = student
#         if encoding_blob:
#             face_encoding = pickle.loads(encoding_blob)
#             encodings_dict[student_id] = (face_encoding, (name, roll_number, department, year))
    
#     return encodings_dict

# # Function to recognize face and return student info
# def recognize_face(face_encoding):
#     encodings_dict = get_all_face_encodings()
    
#     if not encodings_dict:
#         return None
    
#     # Compare face with all stored faces
#     best_match_id = None
#     best_match_distance = 1.0  # Lower is better, using 0.6 as threshold
    
#     for student_id, (encoding, _) in encodings_dict.items():
#         # Compare faces, get distance
#         face_distances = face_recognition.face_distance([encoding], face_encoding)
#         distance = face_distances[0]
        
#         if distance < best_match_distance and distance < 0.6:  # 0.6 is a good threshold
#             best_match_distance = distance
#             best_match_id = student_id
    
#     if best_match_id:
#         _, student_info = encodings_dict[best_match_id]
#         return student_info, best_match_distance
    
#     return None, None

# # Function to extract face encoding from image
# def extract_face_encoding(image):
#     # Convert from BGR to RGB
#     rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    
#     # Find all faces in the image
#     face_locations = face_recognition.face_locations(rgb_image)
    
#     if not face_locations:
#         return None, "No face detected in the image"
    
#     if len(face_locations) > 1:
#         return None, "Multiple faces detected. Please provide an image with only one face"
    
#     # Get the encoding for the first face found
#     face_encoding = face_recognition.face_encodings(rgb_image, face_locations)[0]
#     return face_encoding, None

# # Main application
# def main():
#     st.set_page_config(page_title="Student Information System", layout="wide")
    
#     # Initialize database connection
#     conn = init_db()
    
#     # Create directory for face images if not exists
#     if not os.path.exists("face_images"):
#         os.makedirs("face_images")
        
#     # Session state
#     if 'authenticated' not in st.session_state:
#         st.session_state.authenticated = False
#     if 'role' not in st.session_state:
#         st.session_state.role = None
#     if 'username' not in st.session_state:
#         st.session_state.username = None
    
#     # Title
#     st.title("Student Information System")
    
#     # Sidebar for login/register
#     with st.sidebar:
#         st.header("Authentication")
        
#         if not st.session_state.authenticated:
#             tab1, tab2 = st.tabs(["Login", "Register"])
            
#             with tab1:
#                 login_role = st.selectbox("Select Role", ["student", "admin"], key="login_role")
#                 login_username = st.text_input("Username", key="login_username")
#                 login_password = st.text_input("Password", type="password", key="login_password")
                
#                 if st.button("Login"):
#                     if authenticate(login_username, login_password, login_role):
#                         st.session_state.authenticated = True
#                         st.session_state.role = login_role
#                         st.session_state.username = login_username
#                         st.success(f"Logged in as {login_role}")
#                         st.rerun()
#                     else:
#                         st.error("Invalid username or password")
            
#             with tab2:
#                 if st.checkbox("I am a new student"):
#                     reg_username = st.text_input("Username", key="reg_username")
#                     reg_password = st.text_input("Password", type="password", key="reg_password")
#                     reg_confirm_password = st.text_input("Confirm Password", type="password", key="reg_confirm_password")
                    
#                     if st.button("Register"):
#                         if reg_password != reg_confirm_password:
#                             st.error("Passwords don't match")
#                         elif register_user(reg_username, reg_password, "student"):
#                             st.success("Registration successful! Please login.")
#                         else:
#                             st.error("Username already exists")
#         else:
#             st.success(f"Logged in as {st.session_state.role}: {st.session_state.username}")
#             if st.button("Logout"):
#                 st.session_state.authenticated = False
#                 st.session_state.role = None
#                 st.session_state.username = None
#                 st.rerun()
    
#     # Main content area
#     if not st.session_state.authenticated:
#         st.info("Please login to access the system")
#     else:
#         # Admin view
#         if st.session_state.role == "admin":
#             tab1, tab2, tab3 = st.tabs(["Recognize Student", "View All Students", "Search Student"])
            
#             with tab1:
#                 st.header("Recognize Student by Face")
                
#                 # Face recognition using webcam
#                 camera_input = st.camera_input("Take a picture of the student")
                
#                 if camera_input is not None:
#                     # Convert to OpenCV format
#                     bytes_data = camera_input.getvalue()
#                     img = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR)
                    
#                     with st.spinner("Processing face..."):
#                         face_encoding, error = extract_face_encoding(img)
                        
#                         if error:
#                             st.error(error)
#                         else:
#                             student_info, confidence = recognize_face(face_encoding)
                            
#                             if student_info:
#                                 name, roll_number, department, year = student_info
#                                 st.success(f"Student recognized with {(1-confidence)*100:.2f}% confidence!")
                                
#                                 # Get full student details
#                                 student = get_student_by_roll(roll_number)
#                                 if student:
#                                     st.subheader(f"Student Information: {name}")
#                                     col1, col2 = st.columns(2)
#                                     with col1:
#                                         st.write(f"**Roll Number:** {roll_number}")
#                                         st.write(f"**Department:** {department}")
#                                         st.write(f"**Year:** {year}")
#                                     with col2:
#                                         st.write(f"**Email:** {student[5] or 'Not provided'}")
#                                         st.write(f"**Phone:** {student[6] or 'Not provided'}")
#                                         st.write(f"**Registration Date:** {student[10]}")
                                    
#                                     st.write(f"**Address:** {student[7] or 'Not provided'}")
#                             else:
#                                 st.error("No matching student found in the database")
#                                 # Show image with face detection
#                                 rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
#                                 face_locations = face_recognition.face_locations(rgb_img)
                                
#                                 for (top, right, bottom, left) in face_locations:
#                                     cv2.rectangle(img, (left, top), (right, bottom), (0, 255, 0), 2)
                                
#                                 st.image(cv2.cvtColor(img, cv2.COLOR_BGR2RGB), 
#                                          caption="Face detected but not recognized")
            
#             with tab2:
#                 st.header("All Registered Students")
#                 students_df = get_all_students()
#                 st.dataframe(students_df)
                
#                 # Option to download as CSV
#                 if not students_df.empty:
#                     csv = students_df.to_csv(index=False).encode('utf-8')
#                     st.download_button(
#                         "Download Student Data as CSV",
#                         csv,
#                         "student_data.csv",
#                         "text/csv",
#                         key='download-csv'
#                     )
            
#             with tab3:
#                 st.header("Search Student")
#                 search_query = st.text_input("Enter Roll Number")
#                 if search_query:
#                     student = get_student_by_roll(search_query)
#                     if student:
#                         st.subheader(f"Student Information: {student[1]}")
#                         col1, col2 = st.columns(2)
#                         with col1:
#                             st.write(f"**Roll Number:** {student[2]}")
#                             st.write(f"**Department:** {student[3]}")
#                             st.write(f"**Year:** {student[4]}")
#                         with col2:
#                             st.write(f"**Email:** {student[5] or 'Not provided'}")
#                             st.write(f"**Phone:** {student[6] or 'Not provided'}")
#                             st.write(f"**Registration Date:** {student[10]}")
                        
#                         st.write(f"**Address:** {student[7] or 'Not provided'}")
#                     else:
#                         st.error("Student not found")
        
#         # Student view
#         else:
#             tab1, tab2 = st.tabs(["Register Information", "View Your Information"])
            
#             with tab1:
#                 st.header("Register Your Information")
                
#                 # Check if student is already registered
#                 conn = init_db()
#                 c = conn.cursor()
#                 c.execute("SELECT * FROM students WHERE username=?", (st.session_state.username,))
#                 existing_student = c.fetchone()
#                 conn.close()
                
#                 if existing_student:
#                     st.info("You have already registered your information. You can view it in the next tab.")
#                 else:
#                     st.subheader("Personal Information")
                    
#                     col1, col2 = st.columns(2)
#                     with col1:
#                         name = st.text_input("Full Name")
#                         roll_number = st.text_input("Roll Number")
#                         department = st.selectbox("Department", ["Computer Science", "Electrical Engineering", 
#                                                                "Mechanical Engineering", "Civil Engineering", 
#                                                                "Chemical Engineering", "Other"])
#                     with col2:
#                         year = st.selectbox("Year", [1, 2, 3, 4, 5])
#                         email = st.text_input("Email")
#                         phone = st.text_input("Phone Number")
                    
#                     address = st.text_area("Address")
                    
#                     st.subheader("Face Registration")
#                     st.info("Please take a clear photo of your face for registration. Make sure you are in a well-lit environment.")
                    
#                     face_image = st.camera_input("Take a picture")
                    
#                     face_encoding = None
#                     if face_image is not None:
#                         bytes_data = face_image.getvalue()
#                         img = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR)
                        
#                         with st.spinner("Processing face..."):
#                             face_encoding, error = extract_face_encoding(img)
                            
#                             if error:
#                                 st.error(error)
#                             else:
#                                 st.success("Face detected successfully!")
                    
#                     if st.button("Register Information"):
#                         if not name or not roll_number or not department:
#                             st.error("Name, Roll Number, and Department are required fields")
#                         elif face_encoding is None:
#                             st.error("Face registration is required. Please take a picture")
#                         else:
#                             if save_student(name, roll_number, department, year, email, 
#                                           phone, address, st.session_state.username, face_encoding):
#                                 st.success("Information registered successfully!")
                                
#                                 # Save face image to directory with roll number
#                                 if face_image is not None:
#                                     img_path = os.path.join("face_images", f"{roll_number}.jpg")
#                                     with open(img_path, "wb") as f:
#                                         f.write(face_image.getvalue())
#                             else:
#                                 st.error("Registration failed. Roll number may already exist.")
            
#             with tab2:
#                 st.header("Your Information")
                
#                 conn = init_db()
#                 c = conn.cursor()
#                 c.execute("SELECT * FROM students WHERE username=?", (st.session_state.username,))
#                 student = c.fetchone()
#                 conn.close()
                
#                 if student:
#                     st.subheader(f"Student Information: {student[1]}")
#                     col1, col2 = st.columns(2)
#                     with col1:
#                         st.write(f"**Roll Number:** {student[2]}")
#                         st.write(f"**Department:** {student[3]}")
#                         st.write(f"**Year:** {student[4]}")
#                     with col2:
#                         st.write(f"**Email:** {student[5] or 'Not provided'}")
#                         st.write(f"**Phone:** {student[6] or 'Not provided'}")
#                         st.write(f"**Registration Date:** {student[10]}")
                    
#                     st.write(f"**Address:** {student[7] or 'Not provided'}")
                    
#                     # Try to display face image if exists
#                     img_path = os.path.join("face_images", f"{student[2]}.jpg")
#                     if os.path.exists(img_path):
#                         st.subheader("Your Registered Face")
#                         st.image(img_path)
#                 else:
#                     st.info("You haven't registered your information yet. Please go to the Registration tab.")

# if __name__ == "__main__":
#     main()



import streamlit as st
import cv2
import numpy as np
import face_recognition
import os
import pickle
import hashlib
import sqlite3
from PIL import Image
from datetime import datetime
import pandas as pd
import io

# Initialize database
def init_db():
    conn = sqlite3.connect('student_database.db', check_same_thread=False)
    c = conn.cursor()
    
    # Create users table for authentication
    c.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT NOT NULL
    )
    ''')
    
    # Create students table
    c.execute('''
    CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        roll_number TEXT UNIQUE NOT NULL,
        department TEXT NOT NULL,
        year INTEGER NOT NULL,
        email TEXT,
        phone TEXT,
        address TEXT,
        username TEXT UNIQUE,
        face_encoding BLOB,
        registration_date TEXT,
        FOREIGN KEY(username) REFERENCES users(username)
    )
    ''')
    
    # Insert default admin if not exists
    c.execute("SELECT * FROM users WHERE username='admin' AND role='admin'")
    if not c.fetchone():
        hashed_pw = hashlib.sha256("admin123".encode()).hexdigest()
        c.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", 
                 ("admin", hashed_pw, "admin"))
    
    conn.commit()
    return conn

# Password hashing function
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# User authentication
def authenticate(username, password, role):
    conn = init_db()
    c = conn.cursor()
    hashed_pw = hash_password(password)
    c.execute("SELECT * FROM users WHERE username=? AND password=? AND role=?", 
             (username, hashed_pw, role))
    user = c.fetchone()
    conn.close()
    return user is not None

# Function to register new user
def register_user(username, password, role):
    conn = init_db()
    c = conn.cursor()
    try:
        hashed_pw = hash_password(password)
        c.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", 
                 (username, hashed_pw, role))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        conn.close()
        return False

# Function to save student data with face encoding
def save_student(name, roll_number, department, year, email, phone, address, username, face_encoding=None):
    conn = init_db()
    c = conn.cursor()
    
    # Convert face encoding to binary for storage
    encoding_blob = None
    if face_encoding is not None:
        encoding_blob = pickle.dumps(face_encoding)
    
    try:
        c.execute("""
        INSERT INTO students (name, roll_number, department, year, email, phone, address, username, face_encoding, registration_date) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (name, roll_number, department, year, email, phone, address, username, encoding_blob, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError as e:
        conn.close()
        return False

# Function to get all students
def get_all_students():
    conn = init_db()
    c = conn.cursor()
    c.execute("SELECT id, name, roll_number, department, year, email, phone FROM students")
    students = c.fetchall()
    conn.close()
    
    # Convert to DataFrame for nice display
    df = pd.DataFrame(students, columns=['ID', 'Name', 'Roll Number', 'Department', 'Year', 'Email', 'Phone'])
    return df

# Function to get student by roll number
def get_student_by_roll(roll_number):
    conn = init_db()
    c = conn.cursor()
    c.execute("SELECT * FROM students WHERE roll_number=?", (roll_number,))
    student = c.fetchone()
    conn.close()
    return student

# Function to retrieve all face encodings for comparison
def get_all_face_encodings():
    conn = init_db()
    c = conn.cursor()
    c.execute("SELECT id, name, roll_number, department, year, face_encoding FROM students WHERE face_encoding IS NOT NULL")
    students = c.fetchall()
    conn.close()
    
    # Create dictionary of {id: (encoding, student_info)}
    encodings_dict = {}
    for student in students:
        student_id, name, roll_number, department, year, encoding_blob = student
        if encoding_blob:
            face_encoding = pickle.loads(encoding_blob)
            encodings_dict[student_id] = (face_encoding, (name, roll_number, department, year))
    
    return encodings_dict

# Function to recognize face and return student info
def recognize_face(face_encoding):
    encodings_dict = get_all_face_encodings()
    
    if not encodings_dict:
        return None
    
    # Compare face with all stored faces
    best_match_id = None
    best_match_distance = 1.0  # Lower is better, using 0.6 as threshold
    
    for student_id, (encoding, _) in encodings_dict.items():
        # Compare faces, get distance
        face_distances = face_recognition.face_distance([encoding], face_encoding)
        distance = face_distances[0]
        
        if distance < best_match_distance and distance < 0.6:  # 0.6 is a good threshold
            best_match_distance = distance
            best_match_id = student_id
    
    if best_match_id:
        _, student_info = encodings_dict[best_match_id]
        return student_info, best_match_distance
    
    return None, None

# Function to extract face encoding from image
def extract_face_encoding(image):
    # Convert from BGR to RGB
    rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    
    # Find all faces in the image
    face_locations = face_recognition.face_locations(rgb_image)
    
    if not face_locations:
        return None, "No face detected in the image"
    
    if len(face_locations) > 1:
        return None, "Multiple faces detected. Please provide an image with only one face"
    
    # Get the encoding for the first face found
    face_encoding = face_recognition.face_encodings(rgb_image, face_locations)[0]
    return face_encoding, None

# Main application
def main():
    st.set_page_config(
        page_title="Adaptive Information Retrieval System", 
        layout="wide",
        initial_sidebar_state="expanded",
        menu_items={
            'About': "Adaptive Information Retrieval System with Face Recognition"
        }
    )
    
    # Custom CSS for better UI
    st.markdown("""
    <style>
    .main-header {
        font-family: 'Arial Black', sans-serif;
        background: linear-gradient(90deg, #3a7bd5, #00d2ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3rem !important;
        font-weight: 800 !important;
        margin-bottom: 1rem !important;
        text-align: center;}
                
    .sub-header {
        font-size: 1.8rem;
        color: #333;
        margin-top: 1rem;
        margin-bottom: 1rem;
    }
    .info-box {
        background-color: #f8f9fa;
        border-radius: 0.5rem;
        padding: 1.5rem;
        margin-bottom: 1rem;
        border-left: 4px solid #1E88E5;
    }
    .success-box {
        background-color: #f0f8f0;
        border-radius: 0.5rem;
        padding: 1.5rem;
        margin-bottom: 1rem;
        border-left: 4px solid #4CAF50;
    }
    .error-box {
        background-color: #fff8f8;
        border-radius: 0.5rem;
        padding: 1.5rem;
        margin-bottom: 1rem;
        border-left: 4px solid #F44336;
    }
    .card {
        border-radius: 0.5rem;
        padding: 1.5rem;
        background-color: white;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 1rem;
        transition: transform 0.3s ease;
    }
    .card:hover {
        transform: translateY(-5px);
    }
    .stButton>button {
        width: 100%;
        border-radius: 0.3rem;
        height: 2.5rem;
        font-weight: bold;
    }
    .stTextInput>div>div>input {
        border-radius: 0.3rem;
    }
    .st-emotion-cache-16txtl3 {
        padding: 1rem;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Initialize database connection
    conn = init_db()
    
    # Create directory for face images if not exists
    if not os.path.exists("face_images"):
        os.makedirs("face_images")
        
    # Session state
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'role' not in st.session_state:
        st.session_state.role = None
    if 'username' not in st.session_state:
        st.session_state.username = None
    
    # App logo and title
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<h1 class='main-header'>Adaptive Information Retrieval System</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #666;'>Facial Recognition Enabled</p>", unsafe_allow_html=True)
    
    # Sidebar for login/register
    with st.sidebar:
        st.markdown("<h2 style='text-align: center; color: #1E88E5;'>Authentication</h2>", unsafe_allow_html=True)
        st.markdown("<hr>", unsafe_allow_html=True)
        
        if not st.session_state.authenticated:
            tab1, tab2 = st.tabs(["🔑 Login", "📝 Register"])
            
            with tab1:
                st.markdown("<br>", unsafe_allow_html=True)
                login_role = st.selectbox("Select Role", ["student", "admin"], key="login_role")
                login_username = st.text_input("Username", key="login_username", 
                                              placeholder="Enter your username")
                login_password = st.text_input("Password", type="password", key="login_password",
                                             placeholder="Enter your password")
                
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("Login", key="login_button", use_container_width=True):
                    if not login_username or not login_password:
                        st.markdown("<div class='error-box'>Please fill all fields</div>", unsafe_allow_html=True)
                    elif authenticate(login_username, login_password, login_role):
                        st.session_state.authenticated = True
                        st.session_state.role = login_role
                        st.session_state.username = login_username
                        st.markdown("<div class='success-box'>Login successful! Redirecting...</div>", unsafe_allow_html=True)
                        st.rerun()
                    else:
                        st.markdown("<div class='error-box'>Invalid username or password</div>", unsafe_allow_html=True)
            
            with tab2:
                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown("<div class='info-box'>New students can register here</div>", unsafe_allow_html=True)
                reg_username = st.text_input("Choose Username", key="reg_username", 
                                          placeholder="Create a unique username")
                reg_password = st.text_input("Create Password", type="password", key="reg_password",
                                         placeholder="Create a secure password")
                reg_confirm_password = st.text_input("Confirm Password", type="password", 
                                                  key="reg_confirm_password",
                                                  placeholder="Repeat your password")
                
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("Register as Student", key="register_button", use_container_width=True):
                    if not reg_username or not reg_password or not reg_confirm_password:
                        st.markdown("<div class='error-box'>Please fill all fields</div>", unsafe_allow_html=True)
                    elif reg_password != reg_confirm_password:
                        st.markdown("<div class='error-box'>Passwords don't match</div>", unsafe_allow_html=True)
                    elif register_user(reg_username, reg_password, "student"):
                        st.markdown("<div class='success-box'>Registration successful! Please login.</div>", unsafe_allow_html=True)
                    else:
                        st.markdown("<div class='error-box'>Username already exists</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class='success-box'>
            <h3>Welcome!</h3>
            <p>You are logged in as <b>{st.session_state.role}</b></p>
            <p>Username: <b>{st.session_state.username}</b></p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Logout", type="primary", use_container_width=True):
                st.session_state.authenticated = False
                st.session_state.role = None
                st.session_state.username = None
                st.rerun()
                
            # Show current time
            st.markdown("<br><br>", unsafe_allow_html=True)
            st.markdown(f"<p style='color: #666; text-align: center;'>{datetime.now().strftime('%d %b %Y, %H:%M')}</p>", unsafe_allow_html=True)
    
    # Main content area
    if not st.session_state.authenticated:
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown("""
            <div class="card">
                <h3 style="color: #1E88E5;">Adaptive Information Retrieval System</h3>
                <p>A modern system for student information management using facial recognition technology.</p>
                <ul>
                    <li>Register student profiles with facial recognition</li>
                    <li>Retrieve student information using face identification</li>
                    <li>Secure authentication system</li>
                    <li>Easy administration and searchable database</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
            
        with col2:
            st.markdown("""
            <div class="card">
                <h3 style="color: #1E88E5;">How to Get Started</h3>
                <p>Follow these steps to begin using the system:</p>
                <ol>
                    <li>Login with your credentials or register as a new student</li>
                    <li>Students: Register your personal information and face</li>
                    <li>Admins: Use facial recognition to identify students</li>
                    <li>Access and manage student information seamlessly</li>
                </ol>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("<div class='info-box' style='text-align: center; margin-top: 2rem;'>Please login using the sidebar to access the system.</div>", unsafe_allow_html=True)
        
    else:
        # Admin view
        if st.session_state.role == "admin":
            st.markdown("<div style='background-color: #f0f8ff; padding: 1rem; border-radius: 0.5rem; margin-bottom: 1rem;'><h3 style='margin: 0; color: #1E88E5;'>Admin Dashboard</h3></div>", unsafe_allow_html=True)
            tab1, tab2, tab3 = st.tabs(["👤 Recognize Student", "📋 View All Students", "🔍 Search Student"])
            
            with tab1:
                st.markdown("<h3 class='sub-header'>Recognize Student by Face</h3>", unsafe_allow_html=True)
                
                st.markdown("""
                <div class="info-box">
                    <p><strong>Instructions:</strong> Take a clear picture of the student's face using the camera below. 
                    The system will attempt to recognize the student and display their information.</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Face recognition using webcam
                col1, col2 = st.columns([2, 1])
                with col1:
                    camera_input = st.camera_input("", key="recognize_camera")
                
                with col2:
                    st.markdown("""
                    <div style="padding: 1rem; height: 100%;">
                        <h4 style="color: #1E88E5;">Tips for Good Recognition</h4>
                        <ul>
                            <li>Ensure face is clearly visible</li>
                            <li>Good lighting on the face</li>
                            <li>Remove hats or sunglasses</li>
                            <li>Look directly at camera</li>
                        </ul>
                    </div>
                    """, unsafe_allow_html=True)
                
                if camera_input is not None:
                    # Convert to OpenCV format
                    bytes_data = camera_input.getvalue()
                    img = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR)
                    
                    with st.spinner("Processing face... Please wait"):
                        face_encoding, error = extract_face_encoding(img)
                        
                        if error:
                            st.markdown(f"<div class='error-box'>{error}</div>", unsafe_allow_html=True)
                        else:
                            student_info, confidence = recognize_face(face_encoding)
                            
                            if student_info:
                                name, roll_number, department, year = student_info
                                confidence_percentage = (1-confidence)*100
                                
                                # Get confidence level color based on percentage
                                if confidence_percentage >= 90:
                                    confidence_color = "#4CAF50"  # Green
                                elif confidence_percentage >= 75:
                                    confidence_color = "#FF9800"  # Orange
                                else:
                                    confidence_color = "#F44336"  # Red
                                
                                st.markdown(f"""
                                <div class='success-box'>
                                    <h3>Student Recognized!</h3>
                                    <p>Confidence: <span style="color: {confidence_color}; font-weight: bold;">
                                    {confidence_percentage:.2f}%</span></p>
                                </div>
                                """, unsafe_allow_html=True)
                                
                                # Get full student details
                                student = get_student_by_roll(roll_number)
                                if student:
                                    st.markdown(f"""
                                    <div class="card">
                                        <h3 style="color: #1E88E5; margin-top: 0;">Student Information: {name}</h3>
                                        <div style="display: flex; flex-wrap: wrap;">
                                            <div style="flex: 1; min-width: 250px;">
                                                <p><strong>Roll Number:</strong> {roll_number}</p>
                                                <p><strong>Department:</strong> {department}</p>
                                                <p><strong>Year:</strong> {year}</p>
                                            </div>
                                            <div style="flex: 1; min-width: 250px;">
                                                <p><strong>Email:</strong> {student[5] or 'Not provided'}</p>
                                                <p><strong>Phone:</strong> {student[6] or 'Not provided'}</p>
                                                <p><strong>Registration Date:</strong> {student[10]}</p>
                                            </div>
                                        </div>
                                        <p><strong>Address:</strong> {student[7] or 'Not provided'}</p>
                                    </div>
                                    """, unsafe_allow_html=True)
                            else:
                                st.markdown("<div class='error-box'>No matching student found in the database</div>", unsafe_allow_html=True)
                                
                                # Show image with face detection
                                rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                                face_locations = face_recognition.face_locations(rgb_img)
                                
                                for (top, right, bottom, left) in face_locations:
                                    cv2.rectangle(img, (left, top), (right, bottom), (0, 255, 0), 2)
                                
                                st.image(cv2.cvtColor(img, cv2.COLOR_BGR2RGB), 
                                         caption="Face detected but not recognized")
            
            with tab2:
                st.markdown("<h3 class='sub-header'>All Registered Students</h3>", unsafe_allow_html=True)
                
                students_df = get_all_students()
                
                # Stats about registered students
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.markdown(f"""
                    <div class="card" style="text-align: center; background-color: #e3f2fd;">
                        <h1 style="color: #1E88E5; font-size: 2.5rem; margin: 0;">{len(students_df)}</h1>
                        <p style="margin: 0;">Total Students</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    departments = students_df['Department'].value_counts()
                    top_dept = departments.index[0] if not departments.empty else "None"
                    st.markdown(f"""
                    <div class="card" style="text-align: center; background-color: #e8f5e9;">
                        <h2 style="color: #4CAF50; font-size: 1.3rem; margin: 0;">{top_dept}</h2>
                        <p style="margin: 0;">Largest Department</p>
                        <p style="margin: 0;"> .</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col3:
                    years = students_df['Year'].value_counts()
                    top_year = years.index[0] if not years.empty else "None"
                    st.markdown(f"""
                    <div class="card" style="text-align: center; background-color: #fff8e1;">
                        <h2 style="color: #FF9800; font-size: 1.8rem; margin: 0;">{top_year}</h2>
                        <p style="margin: 0;">Most Common Year</p>
                        <p style="margin: 0;"> .</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Search and filter
                st.markdown("<br>", unsafe_allow_html=True)
                col1, col2 = st.columns([1, 2])
                with col1:
                    search_term = st.text_input("Search by Name or Roll Number", placeholder="Enter search term...")
                with col2:
                    dept_filter = st.multiselect("Filter by Department", 
                                              options=sorted(students_df['Department'].unique()),
                                              default=[])
                
                # Apply filters
                filtered_df = students_df.copy()
                if search_term:
                    mask = (
                        filtered_df['Name'].str.contains(search_term, case=False) | 
                        filtered_df['Roll Number'].str.contains(search_term, case=False)
                    )
                    filtered_df = filtered_df[mask]
                
                if dept_filter:
                    filtered_df = filtered_df[filtered_df['Department'].isin(dept_filter)]
                
                # Show filtered dataframe with styling
                st.markdown("<div style='margin-top: 1rem;'>", unsafe_allow_html=True)
                st.dataframe(
                    filtered_df,
                    column_config={
                        "Name": st.column_config.TextColumn("Name", width="medium"),
                        "Roll Number": st.column_config.TextColumn("Roll Number", width="medium"),
                        "Department": st.column_config.TextColumn("Department", width="medium"),
                        "Year": st.column_config.NumberColumn("Year", format="%d"),
                        "Email": st.column_config.TextColumn("Email", width="medium"),
                        "Phone": st.column_config.TextColumn("Phone", width="medium")
                    },
                    hide_index=True,
                    use_container_width=True
                )
                st.markdown("</div>", unsafe_allow_html=True)
                
                # Option to download as CSV
                if not filtered_df.empty:
                    st.markdown("<br>", unsafe_allow_html=True)
                    col1, col2, col3 = st.columns([1, 1, 1])
                    with col2:
                        csv = filtered_df.to_csv(index=False).encode('utf-8')
                        st.download_button(
                            "📥 Download Student Data as CSV",
                            csv,
                            "student_data.csv",
                            "text/csv",
                            key='download-csv',
                            use_container_width=True
                        )
            
            with tab3:
                st.markdown("<h3 class='sub-header'>Search Student</h3>", unsafe_allow_html=True)
                
                col1, col2 = st.columns([3, 1])
                with col1:
                    search_query = st.text_input("Enter Student Roll Number", 
                                               placeholder="e.g., CS2023001", 
                                               key="detailed_search")
                with col2:
                    st.markdown(" ")
                    st.markdown(" ")

                    search_button = st.button("🔍 Search", use_container_width=True, key="search_btn")
                
                if search_query and (search_button or st.session_state.get('was_searched')):
                    st.session_state['was_searched'] = True
                    student = get_student_by_roll(search_query)
                    
                    if student:
                        # Try to get the student face image
                        img_path = os.path.join("face_images", f"{student[2]}.jpg")
                        has_face_image = os.path.exists(img_path)
                        
                        col1, col2 = st.columns([3, 1] if has_face_image else [1, 0])
                        
                        with col1:
                            st.markdown(f"""
                            <div class="card">
                                <h3 style="color: #1E88E5; margin-top: 0;">{student[1]}</h3>
                                <div style="display: flex; flex-wrap: wrap;">
                                    <div style="flex: 1; min-width: 200px;">
                                        <table style="width: 100%;">
                                            <tr>
                                                <td style="padding: 8px 0;"><strong>Roll Number:</strong></td>
                                                <td style="padding: 8px 0;">{student[2]}</td>
                                            </tr>
                                            <tr>
                                                <td style="padding: 8px 0;"><strong>Department:</strong></td>
                                                <td style="padding: 8px 0;">{student[3]}</td>
                                            </tr>
                                            <tr>
                                                <td style="padding: 8px 0;"><strong>Year:</strong></td>
                                                <td style="padding: 8px 0;">{student[4]}</td>
                                            </tr>
                                        </table>
                                    </div>
                                    <div style="flex: 1; min-width: 200px;">
                                        <table style="width: 100%;">
                                            <tr>
                                                <td style="padding: 8px 0;"><strong>Email:</strong></td>
                                                <td style="padding: 8px 0;">{student[5] or 'Not provided'}</td>
                                            </tr>
                                            <tr>
                                                <td style="padding: 8px 0;"><strong>Phone:</strong></td>
                                                <td style="padding: 8px 0;">{student[6] or 'Not provided'}</td>
                                            </tr>
                                            <tr>
                                                <td style="padding: 8px 0;"><strong>Registration:</strong></td>
                                                <td style="padding: 8px 0;">{student[10]}</td>
                                            </tr>
                                        </table>
                                    </div>
                                </div>
                                <p style="margin-top: 16px;"><strong>Address:</strong> {student[7] or 'Not provided'}</p>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        if has_face_image:
                            with col2:
                                st.image(img_path, width=150, caption="Registered Face")
                                
                                # Add option to verify face
                                verify_btn = st.button("Verify with Camera", key="verify_btn", use_container_width=True)
                                if verify_btn:
                                    st.session_state['verify_mode'] = True
                                    st.session_state['verify_roll'] = student[2]
                                    st.rerun()
                    else:
                        st.markdown("<div class='error-box'>Student not found. Please check the roll number and try again.</div>", unsafe_allow_html=True)
                
                # Verification mode
                if st.session_state.get('verify_mode'):
                    st.markdown("<div class='card'>", unsafe_allow_html=True)
                    st.markdown(f"<h4 style='color: #1E88E5;'>Verifying student with roll number: {st.session_state['verify_roll']}</h4>", unsafe_allow_html=True)
                    verify_camera = st.camera_input("", key="verify_camera")
                    
                    if verify_camera:
                        bytes_data = verify_camera.getvalue()
                        img = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR)
                        
                        with st.spinner("Verifying face..."):
                            face_encoding, error = extract_face_encoding(img)
                            
                            if error:
                                st.markdown(f"<div class='error-box'>{error}</div>", unsafe_allow_html=True)
                            else:
                                student_info, confidence = recognize_face(face_encoding)
                                
                                if student_info:
                                    name, roll_number, department, year = student_info
                                    confidence_percentage = (1-confidence)*100
                                    
                                    if roll_number == st.session_state['verify_roll']:
                                        st.markdown(f"""
                                        <div class='success-box'>
                                            <h3>✅ Identity Verified!</h3>
                                            <p>This is indeed {name} with {confidence_percentage:.2f}% confidence.</p>
                                        </div>
                                        """, unsafe_allow_html=True)
                                    else:
                                        st.markdown(f"""
                                        <div class='error-box'>
                                            <h3>❌ Identity Mismatch!</h3>
                                            <p>This appears to be {name} (Roll: {roll_number}), not the student you're verifying.</p>
                                        </div>
                                        """, unsafe_allow_html=True)
                                else:
                                    st.markdown("""
                                    <div class='error-box'>
                                        <h3>❌ Verification Failed</h3>
                                        <p>Could not match this face to any registered student.</p>
                                    </div>
                                    """, unsafe_allow_html=True)
                    
                    if st.button("Cancel Verification", key="cancel_verify"):
                        st.session_state.pop('verify_mode', None)
                        st.session_state.pop('verify_roll', None)
                        st.rerun()
                    
                    st.markdown("</div>", unsafe_allow_html=True) 
        
        # Student view
        else:
            st.markdown("<div style='background-color: #f0f8ff; padding: 1rem; border-radius: 0.5rem; margin-bottom: 1rem;'><h3 style='margin: 0; color: #1E88E5;'>Student Portal</h3></div>", unsafe_allow_html=True)
            tab1, tab2 = st.tabs(["📝 Register Information", "👤 View Your Information"])
            
            with tab1:
                st.markdown("<h3 class='sub-header'>Register Your Information</h3>", unsafe_allow_html=True)
                
                # Check if student is already registered
                conn = init_db()
                c = conn.cursor()
                c.execute("SELECT * FROM students WHERE username=?", (st.session_state.username,))
                existing_student = c.fetchone()
                conn.close()
                
                if existing_student:
                    st.markdown("""
                    <div class='info-box'>
                        <h3>Already Registered</h3>
                        <p>You have already registered your information. You can view your details in the next tab.</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if st.button("Go to My Information", use_container_width=True):
                        tab2.selectbox = True
                else:
                    st.markdown("""
                    <div class='info-box'>
                        <p>Please complete the form below to register your information. Fields marked with * are required.</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Create a form with nice UI
                    with st.form("registration_form"):
                        st.markdown("<h4 style='color: #1E88E5;'>Personal Information</h4>", unsafe_allow_html=True)
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            name = st.text_input("Full Name*", placeholder="Enter your full name")
                            roll_number = st.text_input("Roll Number*", placeholder="e.g., CS2023001")
                            department = st.selectbox("Department*", 
                                                   ["Computer Science", "Electrical Engineering", 
                                                    "Mechanical Engineering", "Civil Engineering", 
                                                    "Chemical Engineering", "Other"])
                        with col2:
                            year = st.selectbox("Year*", [1, 2, 3, 4, 5])
                            email = st.text_input("Email", placeholder="your.email@example.com")
                            phone = st.text_input("Phone Number", placeholder="+1 (123) 456-7890")
                        
                        address = st.text_area("Address", placeholder="Your full address")
                        
                        st.markdown("<br>", unsafe_allow_html=True)
                        st.markdown("<h4 style='color: #1E88E5;'>Face Registration</h4>", unsafe_allow_html=True)
                        st.markdown("""
                        <div style="background-color: #e3f2fd; padding: 10px; border-radius: 5px; margin-bottom: 15px;">
                            <p><strong>Tips for good face recognition:</strong></p>
                            <ul>
                                <li>Ensure your face is clearly visible</li>
                                <li>Use good lighting (natural light works best)</li>
                                <li>Remove glasses or hats that may obscure your face</li>
                                <li>Look directly at the camera</li>
                                <li>Maintain a neutral expression</li>
                            </ul>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        face_col1, face_col2 = st.columns([3, 2])
                        with face_col1:
                            face_image = st.camera_input("", key="registration_camera")
                            
                            # Process face if image captured
                            face_encoding = None
                            if face_image is not None:
                                bytes_data = face_image.getvalue()
                                img = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR)
                                
                                with st.spinner("Processing face..."):
                                    face_encoding, error = extract_face_encoding(img)
                                    
                                    if error:
                                        st.markdown(f"<div class='error-box'>{error}</div>", unsafe_allow_html=True)
                                    else:
                                        st.markdown("<div class='success-box'>Face detected successfully!</div>", unsafe_allow_html=True)
                                        
                                        # Draw face landmarks for visual feedback
                                        rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                                        face_locations = face_recognition.face_locations(rgb_img)
                                        
                                        for (top, right, bottom, left) in face_locations:
                                            # Draw rectangle around face
                                            cv2.rectangle(img, (left, top), (right, bottom), (0, 255, 0), 2)
                                            
                                            # Get landmarks
                                            face_landmarks = face_recognition.face_landmarks(rgb_img, [face_locations[0]])[0]
                                            
                                            # Draw landmarks
                                            for facial_feature in face_landmarks.keys():
                                                for point in face_landmarks[facial_feature]:
                                                    cv2.circle(img, point, 2, (0, 0, 255), -1)
                                        
                                        with face_col2:
                                            st.image(cv2.cvtColor(img, cv2.COLOR_BGR2RGB), 
                                                   caption="Face detected with landmarks", 
                                                   width=250)
                        
                        st.markdown("<br>", unsafe_allow_html=True)
                        submit_btn = st.form_submit_button("Register Information", use_container_width=True)
                        
                        if submit_btn:
                            if not name or not roll_number or not department:
                                st.markdown("<div class='error-box'>Name, Roll Number, and Department are required fields</div>", unsafe_allow_html=True)
                            elif face_encoding is None:
                                st.markdown("<div class='error-box'>Face registration is required. Please take a picture</div>", unsafe_allow_html=True)
                            else:
                                if save_student(name, roll_number, department, year, email, 
                                              phone, address, st.session_state.username, face_encoding):
                                    st.markdown("""
                                    <div class='success-box'>
                                        <h3>Registration Successful! ✅</h3>
                                        <p>Your information has been registered successfully. You can now view your details in the 'View Your Information' tab.</p>
                                    </div>
                                    """, unsafe_allow_html=True)
                                    
                                    # Save face image to directory with roll number
                                    if face_image is not None:
                                        img_path = os.path.join("face_images", f"{roll_number}.jpg")
                                        with open(img_path, "wb") as f:
                                            f.write(face_image.getvalue())
                                else:
                                    st.markdown("<div class='error-box'>Registration failed. Roll number may already exist.</div>", unsafe_allow_html=True)
            
            with tab2:
                st.markdown("<h3 class='sub-header'>Your Information</h3>", unsafe_allow_html=True)
                
                conn = init_db()
                c = conn.cursor()
                c.execute("SELECT * FROM students WHERE username=?", (st.session_state.username,))
                student = c.fetchone()
                conn.close()
                
                if student:
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        st.markdown(f"""
                        <div class="card">
                            <h3 style="color: #1E88E5; margin-top: 0;">Welcome, {student[1]}!</h3>
                            <p style="color: #666; margin-bottom: 20px;">Registered on {student[10]}</p>
                            
                            <div style="display: flex; flex-wrap: wrap;">
                                <div style="flex: 1; min-width: 200px;">
                                    <table style="width: 100%;">
                                        <tr>
                                            <td style="padding: 8px 0;"><strong>Roll Number:</strong></td>
                                            <td style="padding: 8px 0;">{student[2]}</td>
                                        </tr>
                                        <tr>
                                            <td style="padding: 8px 0;"><strong>Department:</strong></td>
                                            <td style="padding: 8px 0;">{student[3]}</td>
                                        </tr>
                                        <tr>
                                            <td style="padding: 8px 0;"><strong>Year:</strong></td>
                                            <td style="padding: 8px 0;">{student[4]}</td>
                                        </tr>
                                    </table>
                                </div>
                                <div style="flex: 1; min-width: 200px;">
                                    <table style="width: 100%;">
                                        <tr>
                                            <td style="padding: 8px 0;"><strong>Email:</strong></td>
                                            <td style="padding: 8px 0;">{student[5] or 'Not provided'}</td>
                                        </tr>
                                        <tr>
                                            <td style="padding: 8px 0;"><strong>Phone:</strong></td>
                                            <td style="padding: 8px 0;">{student[6] or 'Not provided'}</td>
                                        </tr>
                                    </table>
                                </div>
                            </div>
                            
                            <div style="margin-top: 20px;">
                                <strong>Address:</strong><br>
                                {student[7] or 'Not provided'}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Student ID Card
                        st.markdown("<h4 style='color: #1E88E5; margin-top: 25px;'>Student ID Card</h4>", unsafe_allow_html=True)
                        st.markdown(f"""
                        <div style="border: 2px solid #1E88E5; border-radius: 10px; padding: 15px; background: linear-gradient(135deg, #f0f8ff 0%, #e3f2fd 100%);">
                            <div style="display: flex; flex-wrap: wrap; align-items: center;">
                                <div style="flex: 3;">
                                    <h3 style="color: #1E88E5; margin: 0;">Student ID</h3>
                                    <h2 style="margin: 10px 0;">{student[1]}</h2>
                                    <p style="margin: 5px 0;"><strong>Roll Number:</strong> {student[2]}</p>
                                    <p style="margin: 5px 0;"><strong>Department:</strong> {student[3]}</p>
                                    <p style="margin: 5px 0;"><strong>Year:</strong> {student[4]}</p>
                                </div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                    with col2:
                        # Try to display face image if exists
                        img_path = os.path.join("face_images", f"{student[2]}.jpg")
                        if os.path.exists(img_path):
                            st.markdown("<div class='card' style='padding: 10px;'>", unsafe_allow_html=True)
                            st.markdown("<h4 style='text-align: center; color: #1E88E5;'>Your Registered Face</h4>", unsafe_allow_html=True)
                            st.image(img_path, use_column_width=True)
                            st.markdown("</div>", unsafe_allow_html=True)
                            
                            # Test face recognition
                            st.markdown("<br>", unsafe_allow_html=True)
                            if st.button("Test Face Recognition", use_container_width=True):
                                st.session_state['test_recognition'] = True
                                st.rerun()
                        
                    # Test face recognition mode
                    if st.session_state.get('test_recognition'):
                        st.markdown("<div class='card' style='margin-top: 20px;'>", unsafe_allow_html=True)
                        st.markdown("<h4 style='color: #1E88E5;'>Test Your Face Recognition</h4>", unsafe_allow_html=True)
                        st.markdown("<p>Take a picture to see if the system recognizes you correctly.</p>", unsafe_allow_html=True)
                        
                        test_camera = st.camera_input("", key="test_camera")
                        
                        if test_camera:
                            bytes_data = test_camera.getvalue()
                            img = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR)
                            
                            with st.spinner("Processing face..."):
                                face_encoding, error = extract_face_encoding(img)
                                
                                if error:
                                    st.markdown(f"<div class='error-box'>{error}</div>", unsafe_allow_html=True)
                                else:
                                    student_info, confidence = recognize_face(face_encoding)
                                    
                                    if student_info:
                                        name, roll_number, department, year = student_info
                                        confidence_percentage = (1-confidence)*100
                                        
                                        if roll_number == student[2]:
                                            st.markdown(f"""
                                            <div class='success-box'>
                                                <h3>✅ Recognition Successful!</h3>
                                                <p>You were correctly identified with {confidence_percentage:.2f}% confidence.</p>
                                            </div>
                                            """, unsafe_allow_html=True)
                                        else:
                                            st.markdown(f"""
                                            <div class='error-box'>
                                                <h3>❌ Recognition Mismatch!</h3>
                                                <p>The system identified you as {name} (Roll: {roll_number}), not as yourself.</p>
                                            </div>
                                            """, unsafe_allow_html=True)
                                    else:
                                        st.markdown("""
                                        <div class='error-box'>
                                            <h3>❌ Recognition Failed</h3>
                                            <p>The system could not match your face to any registered student.</p>
                                        </div>
                                        """, unsafe_allow_html=True)
                        
                        if st.button("Close Test", key="close_test"):
                            st.session_state.pop('test_recognition', None)
                            st.rerun()
                            
                        st.markdown("</div>", unsafe_allow_html=True)
                else:
                    st.markdown("""
                    <div class='info-box'>
                        <h3>No Information Found</h3>
                        <p>You haven't registered your information yet. Please go to the 'Register Information' tab to complete your profile.</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if st.button("Go to Registration", use_container_width=True):
                        tab1.selectbox = True

if __name__ == "__main__":
    main()