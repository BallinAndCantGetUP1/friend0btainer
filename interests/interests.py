import streamlit as st
import pandas as pd

class Intrests:
    def __init__(self, sports, games, books, food, hobbys):
        self.sports = sports
        self.games = games
        self.books = books
        self.food = food
        self.hobbys = hobbys
    
    def inl(self):
        self.sports = str(self.sports) #zero intelect
        self.games = str(self.games)
        self.books = str(self.books)
        self.food = str(self.food)
        self.hobbys = str(self.hobbys)
        intrestl =[self.sports, self]
        
        data_df = pd.DataFrame(
    {
        "intrests": [
            [self.sports],
            [self.games],
            [self.books],
            [self.food],
            [self.hobbys],
        ],
    }
)

        st.data_editor(
            data_df,
            column_config={
                "sales": st.column_config.ListColumn(
                    "Sales (last 6 months)",
                    help="The sales volume in the last 6 months",
                    width="medium",
                 ),
             },
             hide_index=True,
)
