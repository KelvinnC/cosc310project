'use client';

import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import './movies.css';

const FASTAPI_URL = "http://127.0.0.1:8000";

interface Movie {
  id: string;
  title: string;
  description: string;
  duration: number;
  genre: string;
  release: string;
  rating?: number;
}

const MoviesPage = () => {
  const [movies, setMovies] = useState<Movie[]>([]);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchMovies = async () => {
      try {
        const response = await fetch(`${FASTAPI_URL}/movies`);
        if (!response.ok) {
          throw new Error('Failed to fetch movies');
        }
        const data = await response.json();
        setMovies(data);
      } catch (err: any) {
        setError(err.message || 'Error fetching movies');
      }
    };
    fetchMovies();
  }, []);

  return (
    <div className="movies-page">
      <div className="movies-box">
        <h1>All Movies</h1>
        {error && <p style={{ color: 'red' }}>Error: {error}</p>}
        <div className="movies-grid">
          {movies.length > 0 ? (
            movies.map((movie) => (
              <Link
                key={movie.id}
                href={`/movies/${movie.id}`}
                className="movie-card"
              >
                <div className="movie-title">{movie.title}</div>
                <div className="movie-meta">
                  {new Date(movie.release).getFullYear()} • {movie.genre}
                  {movie.rating != null && ` • ⭐ ${movie.rating.toFixed(1)}`}
                </div>
              </Link>
            ))
          ) : (
            <p>No movies found.</p>
          )}
        </div>
      </div>
    </div>
  );
};

export default MoviesPage;
