import streamlit as st

class Intrests:
    def __init__(self, sports, games, books, food, hobbys):
        self.sports = sports
        self.games = games
        self.books = books
        self.food = food
        self.hobbys = hobbys


title = st.text_input("", "Life of Brian")
st.write("The current movie title is", title)