import streamlit as st
import pandas as pd
import hashlib
import os
import pickle

# Load users from CSV
def load_users():
    try:
        return pd.read_csv('users.csv')
    except (FileNotFoundError, pd.errors.EmptyDataError):
        return pd.DataFrame(columns=['username', 'email', 'password', 'profile_pic', 'sports', 'games', 'books', 'food', 'hobbies'])

# Save users to CSV
def save_users(users_df):
    users_df.to_csv('users.csv', index=False)

# Hash password
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Save chat messages
def save_chat(username1, username2, message):
    filename = f'chat_{username1}_{username2}.pkl' if username1 < username2 else f'chat_{username2}_{username1}.pkl'
    if not os.path.exists(filename):
        chat_history = []
    else:
        with open(filename, 'rb') as file:
            chat_history = pickle.load(file)
    chat_history.append(message)
    with open(filename, 'wb') as file:
        pickle.dump(chat_history, file)

# Load chat messages
def load_chat(username1, username2):
    filename = f'chat_{username1}_{username2}.pkl' if username1 < username2 else f'chat_{username2}_{username1}.pkl'
    if not os.path.exists(filename):
        return []
    else:
        with open(filename, 'rb') as file:
            chat_history = pickle.load(file)
    return chat_history

# Sign in / Sign up function
def signingin():
    st.title("Sign In / Sign Up")

    # File selection
    file_options = ['Sign Up', 'Sign In']
    selected_file = st.selectbox('Choose What To Do:', file_options)

    # Display content based on file selection
    if selected_file == 'Sign Up':
        display_signup()
    if selected_file == 'Sign In':
        display_signin()

# Sign up function
def display_signup():
    users_df = load_users()
    with st.form("User Sheet"):
        st.write("Fill Out Inputs Below")
        username = st.text_input("Username")
        email = st.text_input("Email")
        password = st.text_input("Password", type='password')
        confirm_password = st.text_input("Confirm Password", type='password')
        submitted = st.form_submit_button("Submit")
        
        if submitted:
            if password != confirm_password:
                st.write("Password does not match. Please ensure both passwords are the same.")
            elif username == '':
                st.write("Username cannot be empty.")
            elif username in users_df['username'].values:
                st.write("Username already exists. Please choose a different username.")
            else:
                hashed_password = hash_password(password)
                new_user = pd.DataFrame({
                    'username': [username],
                    'email': [email],
                    'password': [hashed_password],
                    'profile_pic': [None],
                    'sports': [None],
                    'games': [None],
                    'books': [None],
                    'food': [None],
                    'hobbies': [None]
                })
                users_df = pd.concat([users_df, new_user], ignore_index=True)
                save_users(users_df)
                st.write("Sign-up successful! Your username is:", username)

# Sign in function
def display_signin():
    users_df = load_users()
    with st.form("User Sheet"):
        st.write("Fill Out Inputs Below")
        username = st.text_input("Username")
        password = st.text_input("Password", type='password')
        submitted = st.form_submit_button("Submit")
        
        if submitted:
            hashed_password = hash_password(password)
            user_record = users_df[(users_df['username'] == username) & (users_df['password'] == hashed_password)]
            if not user_record.empty:
                st.session_state['logged_in'] = True
                st.session_state['username'] = username
                if 'friends' not in st.session_state:
                    st.session_state['friends'] = {}
                if username not in st.session_state['friends']:
                    st.session_state['friends'][username] = {'sent': [], 'received': [], 'friends': []}
                st.write("Logged In!")
            else:
                st.write("Invalid username or password.")

# Interests class
class Interests:
    def __init__(self, sports, games, books, food, hobbies):
        self.sports = sports
        self.games = games
        self.books = books
        self.food = food
        self.hobbies = hobbies
    
    def display(self):
        st.write("Favorite Sport:", self.sports)
        st.write("Favorite Game:", self.games)
        st.write("Favorite Book:", self.books)
        st.write("Favorite Food:", self.food)
        st.write("Other Hobbies:", ", ".join(self.hobbies))

# Collect interests
def give_int():
    with st.form("interests_form"):
        sport = st.text_input("Enter your favorite sport:")
        game = st.text_input("Enter your favorite game:")
        book = st.text_input("Enter your favorite book:")
        food = st.text_input("Enter your favorite food:")
        hobbies = st.text_input("Enter at least one other hobby (if more, separate by using commas):")
        profile_pic = st.file_uploader("Upload Profile Picture", type=["jpg", "png"])
        submitted = st.form_submit_button("Submit")

    if submitted:
        hobbies_list = hobbies.split(",")
        my_interests = Interests(sport, game, book, food, hobbies_list)
        users_df = load_users()
        
        profile_pic_path = None
        if profile_pic:
            profile_pic_path = f'profile_pics/{st.session_state["username"]}.png'
            os.makedirs('profile_pics', exist_ok=True)
            with open(profile_pic_path, 'wb') as file:
                file.write(profile_pic.getbuffer())
        
        users_df.loc[users_df['username'] == st.session_state['username'], ['sports', 'games', 'books', 'food', 'hobbies', 'profile_pic']] = [sport, game, book, food, hobbies, profile_pic_path]
        save_users(users_df)
        my_interests.display()

# Display profile
def display_profile():
    users_df = load_users()
    user_data = users_df[users_df['username'] == st.session_state['username']].iloc[0]
    interests = Interests(user_data['sports'], user_data['games'], user_data['books'], user_data['food'], user_data['hobbies'].split(',') if pd.notna(user_data['hobbies']) else [])
    st.write(f"Profile of {st.session_state['username']}")
    if pd.notna(user_data['profile_pic']):
        st.image(user_data['profile_pic'])
    interests.display()

    if st.button("Delete Account"):
        users_df = users_df[users_df['username'] != st.session_state['username']]
        save_users(users_df)
        st.session_state.clear()
        st.write("Your account has been deleted.")

# Display all profiles on home screen
def display_all_profiles():
    if 'logged_in' in st.session_state and st.session_state['logged_in']:
        users_df = load_users()
        for index, user in users_df.iterrows():
            with st.container():
                st.markdown("---")  # Adds a horizontal line for separation
                st.write(f"**Username:** {user['username']}")
                if pd.notna(user['profile_pic']):
                    st.image(user['profile_pic'])
                interests = Interests(user['sports'], user['games'], user['books'], user['food'], user['hobbies'].split(',') if pd.notna(user['hobbies']) else [])
                interests.display()
                friend_request(user['username'])
    else:
        st.write("Please sign in first.")

# Friend request function
def friend_request(other_user):
    if other_user != st.session_state['username']:
        current_user = st.session_state['username']
        if 'friends' not in st.session_state:
            st.session_state['friends'] = {}

        if current_user not in st.session_state['friends']:
            st.session_state['friends'][current_user] = {'sent': [], 'received': [], 'friends': []}
        if other_user not in st.session_state['friends']:
            st.session_state['friends'][other_user] = {'sent': [], 'received': [], 'friends': []}

        if other_user not in st.session_state['friends'][current_user]['sent'] and other_user not in st.session_state['friends'][current_user]['friends']:
            if st.button(f"Send Friend Request to {other_user}", key=f"send_{other_user}"):
                st.session_state['friends'][current_user]['sent'].append(other_user)
                st.session_state['friends'][other_user]['received'].append(current_user)
                st.write(f"Friend request sent to {other_user}")

        if current_user in st.session_state['friends'][other_user]['received']:
            if st.button(f"Accept Friend Request from {other_user}", key=f"accept_{other_user}"):
                st.session_state['friends'][current_user]['friends'].append(other_user)
                st.session_state['friends'][other_user]['friends'].append(current_user)
                st.session_state['friends'][current_user]['received'].remove(other_user)
                st.session_state['friends'][other_user]['sent'].remove(current_user)
                st.write(f"Friend request accepted from {other_user}")

# Chat function
def chat():
    friends = st.session_state['friends'].get(st.session_state['username'], {}).get('friends', [])
    if friends:
        friend = st.selectbox('Select a friend to chat with:', friends)
        chat_history = load_chat(st.session_state['username'], friend)
        for message in chat_history:
            st.write(f"{message['sender']}: {message['text']}")
        new_message = st.text_input("Enter a message:", key="new_message")
        if st.button("Send", key="send_message"):
            message = {"sender": st.session_state['username'], "text": new_message}
            save_chat(st.session_state['username'], friend, message)
            st.experimental_rerun()
    else:
        st.write("No friends to chat with. Send some friend requests!")

# Sidebar navigation
sidebar_option = st.sidebar.radio("Navigation", ["Home", "Interests", "Sign In", "Profile", "Chat"])
if sidebar_option == "Interests":
    if 'logged_in' in st.session_state and st.session_state['logged_in']:
        give_int()
    else:
        st.write("Please sign in first.")
elif sidebar_option == "Home":
    st.write('Welcome to the Home page! Use this tool to help you find friends.')
    display_all_profiles()
elif sidebar_option == "Sign In":
    st.session_state['username'] = ''
    signingin()
elif sidebar_option == "Profile":
    if 'logged_in' in st.session_state and st.session_state['logged_in']:
        display_profile()
    else:
        st.write("Please sign in first.")
elif sidebar_option == "Chat":
    if 'logged_in' in st.session_state and st.session_state['logged_in']:
        chat()
    else:
        st.write("Please sign in first.")