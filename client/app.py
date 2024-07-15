import streamlit as st
import json
from grpc_client import sign_up, login

# Paths to the data files
users_file = 'data/users.json'
posts_file = 'data/posts.json'

# Load data
def load_data(file):
    with open(file, 'r') as f:
        return json.load(f)

# Save data
def save_data(file, data):
    with open(file, 'w') as f:
        json.dump(data, f, indent=4)

# Initialize session state
if 'username' not in st.session_state:
    st.session_state['username'] = None

def login_page():
    st.title("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        response = login(username, password)
        if response.success:
            st.session_state['username'] = username
            st.success("Logged in successfully!")
        else:
            st.error(response.message)

def sign_up_page():
    st.title("Sign Up")
    email = st.text_input("Email")
    username = st.text_input("Username")
    name = st.text_input("Name")
    password = st.text_input("Password", type="password")
    if st.button("Sign Up"):
        response = sign_up(email, username, name, password)
        if response.success:
            st.success("Sign Up successful! Please log in.")
        else:
            st.error(response.message)

def home():
    st.title("Home")
    users = load_data(users_file)
    posts = load_data(posts_file)
    user = next(user for user in users if user['username'] == st.session_state['username'])
    
    st.subheader("Your Feed")
    for post in posts:
        if post['username'] in user['following']:
            st.write(f"**{post['username']}**: {post['content']}")

    st.subheader("Create Post")
    new_post = st.text_area("What's on your mind?")
    if st.button("Post"):
        posts.append({"username": st.session_state['username'], "content": new_post})
        save_data(posts_file, posts)
        st.success("Posted!")

def profile():
    st.title("Profile")
    users = load_data(users_file)
    user = next(user for user in users if user['username'] == st.session_state['username'])
    
    st.subheader(f"Username: {user['username']}")
    st.subheader("Following")
    for followed_user in user['following']:
        st.write(followed_user)

    st.subheader("Follow new users")
    all_usernames = [user['username'] for user in users]
    new_follow = st.selectbox("Select user to follow", [user for user in all_usernames if user not in user['following'] and user != st.session_state['username']])
    if st.button("Follow"):
        user['following'].append(new_follow)
        save_data(users_file, users)
        st.success(f"Followed {new_follow}")

if st.session_state['username'] is None:
    page = st.sidebar.selectbox("Select page", ["Login", "Sign Up"])
    if page == "Login":
        login_page()
    elif page == "Sign Up":
        sign_up_page()
else:
    st.sidebar.title(f"Logged in as {st.session_state['username']}")
    if st.sidebar.button("Logout"):
        st.session_state['username'] = None
    page = st.sidebar.selectbox("Select page", ["Home", "Profile"])
    if page == "Home":
        home()
    elif page == "Profile":
        profile()
