import streamlit as st
import pandas as pd
import hashlib
import os
import pickle
import time

# Load users from CSV
def load_users():
    try:
        return pd.read_csv('users.csv')
    except (FileNotFoundError, pd.errors.EmptyDataError):
        return pd.DataFrame(columns=['username', 'email', 'password', 'profile_pic', 'color', 'sports', 'games', 'books', 'food', 'hobbies'])

# Save users to CSV
def save_users(users_df):
    users_df.to_csv('users.csv', index=False)

# Hash password
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Save chat messages
def save_chat(chat_id, message):
    filename = f'chat_{chat_id}.pkl'
    if not os.path.exists(filename):
        chat_history = []
    else:
        with open(filename, 'rb') as file:
            chat_history = pickle.load(file)
    chat_history.append(message)
    with open(filename, 'wb') as file:
        pickle.dump(chat_history, file)

# Load chat messages
def load_chat(chat_id):
    filename = f'chat_{chat_id}.pkl'
    if not os.path.exists(filename):
        return []
    else:
        with open(filename, 'rb') as file:
            chat_history = pickle.load(file)
    return chat_history

# Save friends data
def save_friends_data():
    with open('friends_data.pkl', 'wb') as file:
        pickle.dump(st.session_state['friends'], file)

# Load friends data
def load_friends_data():
    if os.path.exists('friends_data.pkl'):
        with open('friends_data.pkl', 'rb') as file:
            return pickle.load(file)
    return {}

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
                    'color': [None],
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
                    st.session_state['friends'] = load_friends_data()
                if username not in st.session_state['friends']:
                    st.session_state['friends'][username] = {'friends': [], 'chats': []}
                save_friends_data()
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
        color = st.color_picker("Pick a color for your profile:", "#00f900")
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
        
        users_df.loc[users_df['username'] == st.session_state['username'], ['sports', 'games', 'books', 'food', 'hobbies', 'profile_pic', 'color']] = [sport, game, book, food, hobbies, profile_pic_path, color]
        save_users(users_df)
        my_interests.display()

# Display profile
def display_profile():
    users_df = load_users()
    if st.session_state['username'] not in users_df['username'].values:
        st.write("User profile not found.")
        return

    user_data = users_df[users_df['username'] == st.session_state['username']].iloc[0]
    interests = Interests(
        user_data['sports'], 
        user_data['games'], 
        user_data['books'], 
        user_data['food'], 
        user_data['hobbies'].split(',') if pd.notna(user_data['hobbies']) else []
    )
    st.write(f"Profile of {st.session_state['username']}")
    if pd.notna(user_data['profile_pic']):
        st.image(user_data['profile_pic'])
    interests.display()

    if st.button("Delete Account", key="delete_account"):
        users_df = users_df[users_df['username'] != st.session_state['username']]
        save_users(users_df)
        st.session_state.clear()
        st.write("Your account has been deleted.")

# Display all profiles on home screen
def display_all_profiles():
    if 'logged_in' in st.session_state and st.session_state['logged_in']:
        users_df = load_users()
        for index, user in users_df.iterrows():
            color = user['color'] if pd.notna(user['color']) else "#FFFFFF"
            with st.container():
                st.markdown(f"""
                <div style='background-color:{color}; padding: 10px; border-radius: 5px;'>
                """, unsafe_allow_html=True)
                st.write(f"**Username:** {user['username']}")
                if pd.notna(user['profile_pic']):
                    st.image(user['profile_pic'])
                interests = Interests(user['sports'], user['games'], user['books'], user['food'], user['hobbies'].split(',') if pd.notna(user['hobbies']) else [])
                interests.display()
                friend_request(user['username'])
                st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.write("Please sign in first.")

# Friend request function
def friend_request(other_user):
    if other_user != st.session_state['username']:
        current_user = st.session_state['username']
        if 'friends' not in st.session_state:
            st.session_state['friends'] = {}

        if current_user not in st.session_state['friends']:
            st.session_state['friends'][current_user] = {'friends': [], 'chats': []}
        if other_user not in st.session_state['friends']:
            st.session_state['friends'][other_user] = {'friends': [], 'chats': []}

        current_user_friends = st.session_state['friends'][current_user]['friends']
        other_user_friends = st.session_state['friends'][other_user]['friends']

        if other_user not in current_user_friends:
            if st.button(f"Add {other_user} as friend", key=f"add_{other_user}"):
                current_user_friends.append(other_user)
                other_user_friends.append(current_user)

                chat_id = f"{min(current_user, other_user)}_and_{max(current_user, other_user)}"
                st.session_state['friends'][current_user]['chats'].append(chat_id)
                st.session_state['friends'][other_user]['chats'].append(chat_id)

                save_friends_data()
                st.write(f"Added {other_user} as a friend and started a chat.")

        if other_user in current_user_friends:
            if st.button(f"Remove {other_user} from friends", key=f"remove_{other_user}"):
                current_user_friends.remove(other_user)
                other_user_friends.remove(current_user)

                chat_id = f"{min(current_user, other_user)}_and_{max(current_user, other_user)}"
                st.session_state['friends'][current_user]['chats'].remove(chat_id)
                st.session_state['friends'][other_user]['chats'].remove(chat_id)

                chat_file = f'chat_{chat_id}.pkl'
                if os.path.exists(chat_file):
                    os.remove(chat_file)

                save_friends_data()
                st.write(f"Removed {other_user} from friends and deleted the chat.")

# Chat function
def chat():
    friends = st.session_state['friends'].get(st.session_state['username'], {}).get('friends', [])
    chats = st.session_state['friends'].get(st.session_state['username'], {}).get('chats', [])

    if friends or chats:
        selected_friend = st.selectbox('Select a friend to chat with:', friends, key="select_friend")
        if selected_friend:
            chat_id = f"{min(st.session_state['username'], selected_friend)}_and_{max(st.session_state['username'], selected_friend)}"

            # Ensure chat state is initialized
            if 'chat_inputs' not in st.session_state:
                st.session_state['chat_inputs'] = {}
            if chat_id not in st.session_state['chat_inputs']:
                st.session_state['chat_inputs'][chat_id] = {"new_message": "", "reply_to": "None"}

            # Load chat history
            chat_history = load_chat(chat_id)

            # Display chat history
            for message in chat_history:
                if 'reply_to' in message:
                    st.write(f"{message['sender']}: {message['text']} ↪️ {message['reply_to']['sender']}: {message['reply_to']['text']}")
                else:
                    st.write(f"{message['sender']}: {message['text']}")

            # Chat input and reply selection
            new_message_key = f"new_message_{chat_id}"
            reply_to_key = f"reply_to_{chat_id}"

            st.session_state['chat_inputs'][chat_id]["new_message"] = st.text_input(
                "Enter a message:", value=st.session_state['chat_inputs'][chat_id]["new_message"], key=new_message_key
            )
            st.session_state['chat_inputs'][chat_id]["reply_to"] = st.selectbox(
                "Reply to:",
                ["None"] + [f"{msg['sender']}: {msg['text']}" for msg in chat_history],
                index=0 if st.session_state['chat_inputs'][chat_id]["reply_to"] == "None" else \
                ["None"] + [f"{msg['sender']}: {msg['text']}"].index(st.session_state['chat_inputs'][chat_id]["reply_to"]),
                key=reply_to_key
            )

            # Send message button
            if st.button("Send", key=f"send_message_{chat_id}"):
                new_message = st.session_state['chat_inputs'][chat_id]["new_message"]
                reply_to = st.session_state['chat_inputs'][chat_id]["reply_to"]

                message = {"sender": st.session_state['username'], "text": new_message}
                if reply_to != "None":
                    reply_index = ["None"] + [f"{msg['sender']}: {msg['text']}"].index(reply_to) - 1
                    message["reply_to"] = chat_history[reply_index]

                save_chat(chat_id, message)
                # Clear input after sending the message
                st.session_state['chat_inputs'][chat_id]["new_message"] = ""
                st.session_state['chat_inputs'][chat_id]["reply_to"] = "None"
                st.experimental_rerun()

            # Re-run the app every 0.5 seconds to update the chat dynamically
            time.sleep(0.5)
            st.experimental_rerun()
    else:
        st.write("No friends to chat with. Add some friends first.")

# Group chat creation function
def create_group_chat():
    friends = st.session_state['friends'].get(st.session_state['username'], {}).get('friends', [])
    group_name = st.text_input("Group Name", key="group_name")
    selected_friends = st.multiselect("Select friends to add to group:", friends, key="selected_friends")

    if st.button("Create Group Chat", key="create_group"):
        if group_name and selected_friends:
            group_id = f"group_{st.session_state['username']}_{group_name}"
            selected_friends.append(st.session_state['username'])
            for friend in selected_friends:
                st.session_state['friends'][friend]['chats'].append(group_id)
            save_friends_data()
            st.write("Group chat created!")
        else:
            st.write("Please enter a group name, and select at least one friend.")

# Sidebar navigation
sidebar_option = st.sidebar.radio("Navigation", ["Home", "Interests", "Sign In", "Profile", "Chat", "Create Group Chat"], key="sidebar_nav")
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
elif sidebar_option == "Create Group Chat":
    if 'logged_in' in st.session_state and st.session_state['logged_in']:
        create_group_chat()
    else:
        st.write("Please sign in first.")

# Apply custom styling
st.markdown("""
    <style>
    .sidebar .sidebar-content {
        background-color: #000;
    }
    .css-1d391kg {
        color: #fff;
    }
    .css-1v0mbdj {
        background-color: #00f;
    }
    </style>
    """, unsafe_allow_html=True)
