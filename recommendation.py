import db
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import StandardScaler
from sklearn.metrics.pairwise import linear_kernel
import numpy as np
import pickle

# Check missing values
# tables = ['movies', 'ratings', 'users']
# for table in tables:
#     df = db.select_table(table)
#     check = db.check_missing_values(df, table)
#     print(check)
#     print()

# Load data
movies_df = db.select_table("movies")
ratings_df = db.select_table("ratings")

# Merge DataFrames on movie_id
merged_df = pd.merge(movies_df, ratings_df, on="movie_id")

# Calculate average rating and round to 1 decimal place
data = merged_df.groupby(['title', 'genres'], as_index=False).agg({'rating': 'mean'})
data.rename(columns={'rating': 'rating_avg'}, inplace=True)
data["rating_avg"] = data["rating_avg"].round(1)

# Clean genres column
data["genres"] = data["genres"].apply(lambda title: title.replace("|", " ").replace("-", ""))

# Vectorize genres using TF-IDF
vectorizer = TfidfVectorizer()
tfidf_matrix = vectorizer.fit_transform(data["genres"])

# Normalize the ratings
scaler = StandardScaler()
ratings_scaler = scaler.fit_transform(data[['rating_avg']])

# Combine genres and ratings into a single feature matrix
combined_features = np.hstack((tfidf_matrix.toarray(), ratings_scaler))

# Compute the cosine similarity matrix for combined features
cosine_sim = linear_kernel(combined_features, combined_features)

def recommend_movie(title, cosine_sim=cosine_sim):
    idx = data.index[data["title"] == title].tolist()[0]
    sim_score = sorted(list(enumerate(cosine_sim[idx])),
                       key=lambda x: x[1], reverse=True)
    sim_score = sim_score[1:11]
    movie_indices = [i[0] for i in sim_score]
    return data.iloc[movie_indices]


# Recommend movies
movie = "Toy Story (1995)"
rcm_movie = recommend_movie(movie)
print(rcm_movie[["title", "genres", "rating_avg"]])

# pickle.dump(data, open("movies_list.pkl", "wb"))
# pickle.dump(cosine_sim, open("cosine_sim.pkl", "wb"))
# pickle.load(open('movies_list.pkl', 'rb'))

