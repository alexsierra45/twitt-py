import streamlit as st
from grpc_client import delete_post, exists_user, repost, sign_up, login, create_post, get_user_posts, follow_user, unfollow_user, get_following


def login_page():
    st.title("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        token = login(username, password)
        if token:
            st.session_state['username'] = username
            st.session_state['token'] = token
            st.success("Logged in successfully")
            st.experimental_rerun()
        else:
            st.error("Login failed")

def sign_up_page():
    st.title("Sign Up")
    email = st.text_input("Email", key="signup_email")
    username = st.text_input("Username", key="signup_username")
    name = st.text_input("Name", key="signup_name")
    password = st.text_input("Password", type="password", key="signup_password")
    if st.button("Sign Up"):
        if sign_up(email, username, name, password):
            st.success("Account created successfully")
        else:
            st.error("Sign up failed. Please try again.")

async def home():
    st.title("Home")
    st.subheader("Your Feed")
    token = st.session_state['token']
    posts = await get_user_posts(st.session_state['username'], token)
    if posts:
        for post in posts:
            col1, col2 = st.columns([4, 1])
            with col1:
                if post.original_post_id:
                    st.write(f"**{post.user_id}**: {post.content} (Reposted)")
                else:
                    st.write(f"**{post.user_id}**: {post.content}")
            with col2:
                if st.button("Delete", key=f"delete_{post.post_id}"):
                    if delete_post(post.post_id, token):
                        st.success("Post deleted successfully")
                        st.experimental_rerun()
                    else:
                        st.error("Failed to delete post")
    else:
        st.write("No posts available.")

    st.subheader("Create Post")
    new_post = st.text_area("What's on your mind?", key="new_post")
    if st.button("Post"):
        if create_post(st.session_state['username'], new_post, token):
            st.success("Posted successfully")
            st.experimental_rerun()
        else:
            st.error("Failed to create post")

async def following():
    token = st.session_state['token']
    current_user =  st.session_state['username']
    st.title("Following Page")
    st.subheader(f"Username: {current_user}")

    st.subheader("Following these users")
    following_users = await get_following(current_user, token)
    
    if following_users:
        for user in following_users:
            col1, col2 = st.columns([3, 1])  # Dos columnas, una para el nombre y otra para el botón de unfollow
            with col1:
                st.write(user)  # Mostrar el nombre del usuario
            with col2:
                if st.button(f"Unfollow", key=f"unfollow_{user}"):  # Botón de Unfollow
                    if unfollow_user(current_user, user, token):
                        st.success(f"Unfollowed {user} successfully")
                        st.experimental_rerun()  # Refrescar la página para actualizar la lista
                    else:
                        st.error(f"Failed to unfollow {user}")

            # Obtener las publicaciones del usuario
            posts = await get_user_posts(user, token)

            # Mostrar las publicaciones debajo del usuario
            if posts:
                st.subheader(f"Posts by {user}:")
                for post in posts:
                    st.write(f"**{post.user_id}**: {post.content}")
                    if st.button(f"Repost", key=f"repost_{post.post_id}"):
                        if repost(current_user, post.post_id, token):
                            st.success("Post reposted successfully")
                            st.experimental_rerun()
                        else:
                            st.error("Failed to repost post")
            else:
                st.write(f"No posts available for {user}.")


    else:
        st.write("You are not following anyone.")

    st.subheader("Follow new users")
    search_username = st.text_input("Search for a user by username")

    if search_username:
        if exists_user(search_username, token):  
            if search_username in following_users:
                st.write(f"You are already following {search_username}")
            else:    
                col1, col2 = st.columns([3, 1])  # Create two columns for search results
                with col1:
                    st.write(f"User found: {search_username}")
                with col2:
                    if st.button(f"Follow {search_username}"):
                        if follow_user(current_user, search_username, token):
                            st.success(f"Followed {search_username} successfully")
                            st.experimental_rerun()
                        else:
                            st.error(f"Failed to follow {search_username}")
                    
                posts = await get_user_posts(search_username, token)

                # Mostrar las publicaciones debajo del usuario
                if posts:
                    st.subheader(f"Posts by {search_username}:")
                    for post in posts:
                        st.write(f"**{post.user_id}**: {post.content}")
                        if st.button(f"Repost", key=f"repost_{post.post_id}"):
                            if repost(current_user, post.post_id, token):
                                st.success("Post reposted successfully")
                                st.experimental_rerun()
                            else:
                                st.error("Failed to repost post")
                else:
                    st.write(f"No posts available for {user}.") 
        else:              
            st.write("User not found")

def logout():
    st.session_state['username'] = None
    st.experimental_rerun()


async def run():
    if 'username' not in st.session_state:
        st.session_state['username'] = None

    if st.session_state['username'] is None:
        page = st.sidebar.selectbox("Select page", ["Login", "Sign Up"])
        if page == "Login":
            login_page()
        elif page == "Sign Up":
            sign_up_page()
    else:
        st.sidebar.title(f"Logged in as {st.session_state['username']}")
        if st.sidebar.button("Logout"):
            logout()
        page = st.sidebar.selectbox("Select page", ["Home", "Following"])
        if page == "Home":
            await home()
        elif page == "Following":
            await following()
