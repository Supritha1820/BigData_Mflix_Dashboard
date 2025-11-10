#  🎬 MOVIE ANALYTICS DASHBOARD — Azure CosmosDB (MongoDB API)
import streamlit as st
import pandas as pd
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt
from pymongo import MongoClient

#  🌐 MongoDB Connection
uri = "mongodb+srv://Suprithamflix:Password2002@bigdata-mflix.mongocluster.cosmos.azure.com/?tls=true&authMechanism=SCRAM-SHA-256&retrywrites=false&maxIdleTimeMS=120000"
client = MongoClient(uri)
db = client["sample_mflix"]
collection = db["movies"]


# 📥 Data Loading
data = list(collection.find({}, {"_id": 0, "title": 1, "genres": 1, "year": 1, "imdb": 1}))
df = pd.DataFrame(data)

# Extract IMDb rating safely
df["imdb_rating"] = df["imdb"].apply(lambda x: x.get("rating") if isinstance(x, dict) and "rating" in x else None)
df.drop(columns=["imdb"], inplace=True, errors="ignore")

# Data Cleaning
df["year"] = pd.to_numeric(df["year"], errors="coerce")
df["imdb_rating"] = pd.to_numeric(df["imdb_rating"], errors="coerce")
df = df.dropna(subset=["year", "genres"])
df["year"] = df["year"].astype(int)
df["main_genre"] = df["genres"].apply(lambda x: x[0] if isinstance(x, list) and len(x) > 0 else None)

# 🎨 Streamlit Layout
st.set_page_config(page_title="🎬 Movie Analytics Dashboard", layout="wide")

# 🧾 Dashboard Header
st.title("🎥 Movie Analytics Dashboard")
st.markdown("#### Connected to **Azure CosmosDB (MongoDB API)** — `sample_mflix.movies`")
st.markdown("---")

# 🎯 Key Metrics
total_movies = len(df)
unique_genres = df["main_genre"].nunique()
avg_rating = round(df["imdb_rating"].mean(), 2)
latest_year = df["year"].max()
oldest_year = df["year"].min()

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("🎬 Total Movies", f"{total_movies:,}")
col2.metric("🎭 Unique Genres", unique_genres)
col3.metric("⭐ Average IMDb Rating", avg_rating)
col4.metric("📅 Year Range", f"{oldest_year} - {latest_year}")
col5.metric("💡 Data Source", "Azure CosmosDB")

st.markdown("---")

# Movie Count per Genre
st.subheader("🎭 Movie Count per Genre")

genre_counts = df["main_genre"].value_counts().reset_index()
genre_counts.columns = ["Genre", "Movie Count"]

fig_genre = px.bar(
    genre_counts.sort_values("Movie Count", ascending=False).head(15),
    x="Genre", y="Movie Count",
    color="Movie Count",
    color_continuous_scale="Blues",
    title="Top 15 Genres by Movie Count",
)
st.plotly_chart(fig_genre, use_container_width=True)
st.dataframe(genre_counts)

st.markdown("---")

#  Movies Released per Year
st.subheader("📅 Number of Movies Released per Year")

movies_per_year = df.groupby("year").size().reset_index(name="Movie Count")

fig_year = px.area(
    movies_per_year,
    x="year", y="Movie Count",
    title="Movies Released per Year",
    color_discrete_sequence=["#007BFF"],
)
st.plotly_chart(fig_year, use_container_width=True)
st.dataframe(movies_per_year.tail(10))

st.markdown("---")

# Average IMDb Rating Over Time
st.subheader("⭐ Average IMDb Rating Over Years")

rating_trends = df.groupby("year")["imdb_rating"].mean().reset_index()

fig_rating_trend = px.line(
    rating_trends,
    x="year", y="imdb_rating",
    markers=True,
    title="Average IMDb Rating Over Years",
    color_discrete_sequence=["#FF5733"],
)
st.plotly_chart(fig_rating_trend, use_container_width=True)
st.dataframe(rating_trends.tail(10))

st.markdown("---")

# Ratings by Genre × Year
st.subheader("⭐ Average IMDb Rating by Year — Top Genres")

top_genres = df["main_genre"].value_counts().nlargest(10).index.tolist()
df_top_genres = df[df["main_genre"].isin(top_genres)]

avg_rating_genre_year = df_top_genres.groupby(["year", "main_genre"])["imdb_rating"].mean().reset_index()

fig4, ax4 = plt.subplots(figsize=(12, 7))
sns.lineplot(
    data=avg_rating_genre_year,
    x="year",
    y="imdb_rating",
    hue="main_genre",
    marker="o",
    ax=ax4
)
ax4.set_title("Average IMDb Rating by Year — Top Genres", fontsize=13)
ax4.set_xlabel("Year")
ax4.set_ylabel("Avg IMDb Rating")
ax4.legend(title="Genre", bbox_to_anchor=(1.02, 1), loc="upper left")
st.pyplot(fig4)

st.dataframe(avg_rating_genre_year.pivot_table(index="year", columns="main_genre", values="imdb_rating").fillna("-").round(2).tail(10))

st.markdown("---")

# Top Rated Movies by Genre
st.subheader("🏆 Top Rated Movies by Genre")

top_movies = (
    df.groupby("main_genre")
    .apply(lambda x: x.nlargest(1, "imdb_rating")[["title", "year", "imdb_rating"]])
    .reset_index(drop=True)
    .dropna()
    .sort_values("imdb_rating", ascending=False)
)

st.dataframe(top_movies.head(20))
st.markdown("---")

# Genre Comparison 
st.subheader("🥧 Genre Distribution — Proportion of Movies per Genre")

fig_genre_pie = px.pie(
    genre_counts.head(15),  # Top 15 genres
    names="Genre",
    values="Movie Count",
    title="Top 15 Genres — Share of Total Movies",
    color_discrete_sequence=px.colors.qualitative.Pastel
)
fig_genre_pie.update_traces(textposition="inside", textinfo="percent+label")
st.plotly_chart(fig_genre_pie, use_container_width=True)


# Raw Data Preview
st.subheader("📘 Sample of Movie Data (20 Random Entries)")
st.dataframe(df.sample(20))
st.markdown("---")

st.caption("© 2025 Movie Analytics Dashboard | Data Source: Azure CosmosDB (MongoDB API)")
