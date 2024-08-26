import streamlit as st
import pickle
import requests

movies = pickle.load(open("movies_list_with_ids.pkl", 'rb'))
cosine_sim = pickle.load(open("cosine_sim.pkl", 'rb'))
movies_list = movies["title"].tolist()

st.header("Movie Recommender System")

def fetch_poster(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=cafa598a8d61bdf5b31ca796fecf039f"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        poster_path = data.get('poster_path')
        if poster_path:
            full_path = f"https://image.tmdb.org/t/p/w500/{poster_path}"
        else:
            full_path = "https://via.placeholder.com/500x750?text=No+Poster+Available"
    except (requests.exceptions.RequestException, ValueError) as e:
        # Handle potential errors like network issues or invalid JSON
        print(f"Error fetching poster for movie ID {movie_id}: {e}")
        full_path = "https://via.placeholder.com/500x750?text=No+Poster+Available"
    return full_path


def recommend_movie(movie):
    idx = movies.index[movies["title"] == movie].tolist()[0]
    sim_score = sorted(list(enumerate(cosine_sim[idx])),
                       key=lambda x: x[1], reverse=True)
    sim_score = sim_score[1:11]
    rcm_movies = []
    rcm_poster = []
    for i in sim_score:
        movies_id = movies.iloc[i[0]]["movie_id"]
        rcm_movies.append(movies.iloc[i[0]]["title"])
        rcm_poster.append(fetch_poster(movies_id))

    return rcm_movies, rcm_poster

def main():
    select_value = st.selectbox("Select a movie", movies_list)

    if st.button("Show Recommendations"):
        movie_names, movie_posters = recommend_movie(select_value)

        st.write(f"**Recommendations for: {select_value}**")

        cols = st.columns(5)
        for i, col in enumerate(cols):
            if i < len(movie_names):
                with col:
                    st.image(movie_posters[i], caption=movie_names[i])
                    st.write(f"**{movie_names[i]}**")

if __name__ == "__main__":
    main()