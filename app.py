import streamlit as st
import pickle
import requests
import aiohttp
import asyncio
import gzip

movies = pickle.load(open('movies.pkl','rb'))

# Load the similarity matrix from the compressed file
with gzip.open('similarity.pkl.gz', 'rb') as f:
    similarity = pickle.load(f)


async def fetch_poster(session, movie_id):
    url = f'https://api.themoviedb.org/3/movie/{movie_id}?api_key=fb7bb23f03b6994dafc674c074d01761&language=en-US'
    try:
        async with session.get(url, timeout=10) as response:
            data = await response.json()
            return f"https://image.tmdb.org/t/p/w500{data.get('poster_path', '')}" or "https://via.placeholder.com/500x750?text=No+Image"
    except aiohttp.ClientError:
        return "https://via.placeholder.com/500x750?text=Error"

async def fetch_posters(movie_ids):
    async with aiohttp.ClientSession() as session:
        return await asyncio.gather(*(fetch_poster(session, mid) for mid in movie_ids))

def recommend(movie):
    movie_index = movies[movies['title'] == movie].index[0]
    distances = similarity[movie_index]
    movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:7]

    recommended_movies = []
    movie_ids = [movies.iloc[i[0]].movie_id for i in movies_list]
    recommended_movies_posters = asyncio.run(fetch_posters(movie_ids))

    for i in movies_list:
        recommended_movies.append(movies.iloc[i[0]].title)

    return recommended_movies, recommended_movies_posters

# Page configuration for a wide layout
st.set_page_config(layout="wide")

# Title with custom style and no top margin
st.markdown("""
<style>
    .title {
        text-align: center;
        color: #ff6347;
        margin-top: 0; /* Remove top margin */
        padding-top: 0; /* Remove top padding */
    }
    .stButton button {
        width: 150px; /* Adjust width of the button */
        padding: 0.5rem; /* Reduce padding size */
        display: block;
        margin: 0 auto; /* Center the button */
    }
    .footer {
        position: fixed;
        bottom: 0;
        width: 100%;
        text-align: center;
        padding: 10px;
        color: white;
        font-size: 14px;
        box-shadow: 0 -1px 5px rgba(0,0,0,0.1);
    }
    .footer a {
        color: white;
        text-decoration: none;
    }
    .footer a:hover {
        text-decoration: underline;
    }
</style>
<h1 class="title">Movie Recommender System</h1>
""", unsafe_allow_html=True)

# Centered layout with search bar and button
col1, col2, col3 = st.columns([3, 4, 3])

with col2:
    selected_movie_name = st.selectbox(
        "Select movie",
        (movies['title'].values),
        index=0
    )
    recommend_button_clicked = st.button("Recommend")

# Initialize posters and names before the button is clicked
posters = []
names = []

if recommend_button_clicked:
    names, posters = recommend(selected_movie_name)

# Only display if posters and names are available
if posters and names:
    num_columns = 6  # Set the number of posters per row
    for row in range((len(posters) + num_columns - 1) // num_columns):  # Calculate the number of rows needed
        cols = st.columns(num_columns)
        for i in range(num_columns):
            index = row * num_columns + i
            if index < len(posters):
                with cols[i]:
                    st.image(posters[index], caption=names[index], use_column_width=True)


# Footer
st.markdown("""
<div class="footer">
    Made by <strong>Ali Khurshid</strong><br>
    <a href="https://www.linkedin.com/in/ali-khurshid-60904426b/" target="_blank">LinkedIn</a> | 
    <a href="https://github.com/alikhere" target="_blank">GitHub</a>
</div>
""", unsafe_allow_html=True)