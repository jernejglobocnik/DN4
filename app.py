import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

st.set_page_config(
    page_title="MovieLens Analiza",
    page_icon="🎬",
    layout="wide"
)

st.title("🎬 MovieLens Analiza")

@st.cache_data
def load_data():
    data_path = 'podatki'
    if not os.path.exists(f'{data_path}/movies.csv'):
        st.error("Datoteka movies.csv ne obstaja. Prosimo, preverite pot do podatkov.")
        return None, None

    movies = pd.read_csv(f'{data_path}/movies.csv')
    ratings = pd.read_csv(f'{data_path}/ratings.csv')
    
    movies['genres'] = movies['genres'].str.split('|')
    movies['year'] = movies['title'].str.extract(r'\((\d{4})\)')
    
    return movies, ratings
movies, ratings = load_data()


st.sidebar.title("Navigacija")
page = st.sidebar.radio(
    "Izberite stran:",
    ["Analiza podatkov", "Primerjava filmov"]
)

if page == "Analiza podatkov":
    st.header("Analiza podatkov")
    if movies is not None and ratings is not None:
        avg_ratings = ratings.groupby('movieId').agg({
            'rating': ['mean', 'count']
        }).reset_index()
        avg_ratings.columns = ['movieId', 'avg_rating', 'num_ratings']
        avg_ratings = avg_ratings.merge(movies, on='movieId')
        
        min_ratings = st.slider("Minimalno število ocen:", 1, 1000, 10)
        selected_genre = st.selectbox("Izberi žanr:", ['Vsi'] + sorted(list(set([g for genres in movies['genres'] for g in genres]))))
        selected_year = st.selectbox("Izberi leto:", ['Vsa'] + sorted(movies['year'].dropna().unique().tolist()))
        filtered_ratings = avg_ratings[avg_ratings['num_ratings'] >= min_ratings]
        
        if selected_genre != 'Vsi':
            filtered_ratings = filtered_ratings[filtered_ratings['genres'].apply(lambda x: selected_genre in x)]
        
        if selected_year != 'Vsa':
            filtered_ratings = filtered_ratings[filtered_ratings['year'] == selected_year]

        top_movies = filtered_ratings.sort_values('avg_rating', ascending=False).head(10)
        st.write("### Top 10 filmov")
        for _, movie in top_movies.iterrows():
            st.write(f"**{movie['title']}** - Povprečna ocena: {movie['avg_rating']:.2f} ({movie['num_ratings']} ocen)")

else:
    st.header("Primerjava filmov")
    if movies is not None and ratings is not None:
        movie1 = st.selectbox("Izberi prvi film:", movies['title'].tolist())
        movie2 = st.selectbox("Izberi drugi film:", movies['title'].tolist())
        
        if movie1 and movie2:

            movie1_id = movies[movies['title'] == movie1]['movieId'].iloc[0]
            movie2_id = movies[movies['title'] == movie2]['movieId'].iloc[0]
            movie1_ratings = ratings[ratings['movieId'] == movie1_id]
            movie2_ratings = ratings[ratings['movieId'] == movie2_id]
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader(movie1)
                st.write(f"Povprečna ocena: {movie1_ratings['rating'].mean():.2f}")
                st.write(f"Število ocen: {len(movie1_ratings)}")
                st.write(f"Standardni odklon: {movie1_ratings['rating'].std():.2f}")
                fig, ax = plt.subplots()
                ax.hist(movie1_ratings['rating'], bins=10, range=(0.5, 5.5))
                ax.set_title("Histogram ocen")
                ax.set_xlabel("Ocena")
                ax.set_ylabel("Število")
                st.pyplot(fig)
            
            with col2:
                st.subheader(movie2)
                st.write(f"Povprečna ocena: {movie2_ratings['rating'].mean():.2f}")
                st.write(f"Število ocen: {len(movie2_ratings)}")
                st.write(f"Standardni odklon: {movie2_ratings['rating'].std():.2f}")
                fig, ax = plt.subplots()
                ax.hist(movie2_ratings['rating'], bins=10, range=(0.5, 5.5))
                ax.set_title("Histogram ocen")
                ax.set_xlabel("Ocena")
                ax.set_ylabel("Število")
                st.pyplot(fig)
            st.subheader("Povprečne letne ocene")
            movie1_yearly = movie1_ratings.copy()
            movie1_yearly['year'] = pd.to_datetime(movie1_yearly['timestamp'], unit='s').dt.year
            movie1_yearly_avg = movie1_yearly.groupby('year')['rating'].mean()
            movie2_yearly = movie2_ratings.copy()
            movie2_yearly['year'] = pd.to_datetime(movie2_yearly['timestamp'], unit='s').dt.year
            movie2_yearly_avg = movie2_yearly.groupby('year')['rating'].mean()
            fig, ax = plt.subplots()
            ax.plot(movie1_yearly_avg.index, movie1_yearly_avg.values, label=movie1)
            ax.plot(movie2_yearly_avg.index, movie2_yearly_avg.values, label=movie2)
            ax.set_title("Povprečne letne ocene")
            ax.set_xlabel("Leto")
            ax.set_ylabel("Povprečna ocena")
            ax.legend()
            st.pyplot(fig)
            st.subheader("Število ocen na leto")
            movie1_yearly_count = movie1_yearly.groupby('year').size()
            movie2_yearly_count = movie2_yearly.groupby('year').size()
            fig, ax = plt.subplots()
            ax.plot(movie1_yearly_count.index, movie1_yearly_count.values, label=movie1)
            ax.plot(movie2_yearly_count.index, movie2_yearly_count.values, label=movie2)
            ax.set_title("Število ocen na leto")
            ax.set_xlabel("Leto")
            ax.set_ylabel("Število ocen")
            ax.legend()
            st.pyplot(fig) 