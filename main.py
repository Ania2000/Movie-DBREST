from fastapi import FastAPI, HTTPException
import requests

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello World"}

@app.get("/sum")
def add(x: int = 0, y: int = 10):
    return x + y


@app.get("/subtract")
def subtract(x: int = 0, y: int = 10):
    return x - y


@app.get("/multiply")
def multiply(x: int = 0, y: int = 10):
    return x * y

@app.get("/geocode")
def geocode(lat: float, lon: float):
        url = "https://nominatim.openstreetmap.org/reverse"
        params = {
            "format": "json",
            "lat": lat,
            "lon": lon,
            "zoom": 18,
            "addressdetails": 1
        }

        try:
            response = requests.get(
                url,
                params=params,
                headers={"User-Agent": "Mozilla/5.0 (FastAPI app)"},
                timeout=10
            )
            response.raise_for_status()

            return {
                "latitude": 50.0680275,
                "longitude": 19.9098668,
                "nominatim_response": response.json() }

        except requests.RequestException as e:
            raise HTTPException(status_code=502, detail=str(e))


import sqlite3

@app.get('/movies')
def get_movies():
    db = sqlite3.connect("movies.db")
    cursor = db.cursor()
    rows = cursor.execute("SELECT * FROM movies").fetchall()
    output = []
    for row in rows:
        movie = {
            "id": row[0],
            "title": row[1],
            "year": row[2],
            "actors": row[3]
        }
        output.append(movie)

    db.close()
    return output



@app.get('/movies/{movie_id}')
def get_single_movie(movie_id:int):
    db = sqlite3.connect("movies.db")
    cursor = db.cursor()
    row = cursor.execute("SELECT * FROM movies WHERE id=?",(movie_id,)).fetchone()

    db.close()
    if row is None:
        raise HTTPException(status_code=404, detail="Movie not found")

    movie = {
    "id": row[0],
    "title": row[1],
    "year": row[2],
    "actors": row[3]
}

    return movie

from typing import Any

conn = sqlite3.connect("movies.db", check_same_thread=False)
cursor = conn.cursor()

@app.post("/movies")
def add_movie(params: dict[str, Any]):
    title = params.get("title")
    year = params.get("year")
    actors = params.get("actors")

    cursor.execute(
        """
        INSERT INTO movies (title, year, actors)
        VALUES (?, ?, ?)
        """,
        (title, year, actors)
    )
    conn.commit()

    if cursor.rowcount == 0:
        raise HTTPException(status_code=500, detail="Movie was not inserted")

    movie_id = cursor.lastrowid
    return {"message": "Movie added successfully", "id": movie_id}


@app.put("/movies/{movie_id}")
def update_movie(movie_id: int, params: dict[str, Any]):
    title = params.get("title")
    year = params.get("year")
    actors = params.get("actors")

    if title is None or year is None or actors is None:
        raise HTTPException(status_code=400, detail="Missing title/year/actors")

    cursor.execute(
        """
        UPDATE movies
        SET title = ?, year = ?, actors = ?
        WHERE id = ?
        """,
        (title, year, actors, movie_id)
    )
    conn.commit()

    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="Movie not found")

    return {"message": "Movie updated successfully", "id": movie_id}

@app.delete("/movies/{movie_id}")
def delete_movie(movie_id: int):
    cursor.execute("DELETE FROM movies WHERE id = ?", (movie_id,))
    conn.commit()

    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="Movie not found")

    return {"message": "Movie deleted successfully", "id": movie_id}


@app.delete("/movies")
def delete_all_movies():
    cursor.execute("DELETE FROM movies")
    conn.commit()

    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="No movies to delete")

    return {"message": "All movies deleted"}
