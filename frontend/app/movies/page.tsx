'use client';

import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import './movies.css';
import { apiFetch } from '../../lib/api';

const FASTAPI_URL = "http://127.0.0.1:8000";;

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
  // Optional: Track which movies are currently adding to prevent double clicks
  const [addingId, setAddingId] = useState<string | null>(null);

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

  const handleAddToWatchlist = async (e: React.MouseEvent, movie: Movie) => {
    e.preventDefault(); 
    e.stopPropagation();

    // 1. GET THE TOKEN (Assuming you store it in localStorage after login)
    const token = localStorage.getItem('token'); 
    
    if (!token) {
      alert("You must be logged in to use the watchlist.");
      return;
    }

    setAddingId(movie.id);

    try {
      // 2. CHANGE URL: Pass movieId as a Query Parameter to match backend signature
      // Backend expects: /watchlist/add?movieId=123
      const response = await apiFetch(`${FASTAPI_URL}/watchlist/add?movieId=${movie.id}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          // 3. ADD AUTH HEADER
          'Authorization': `Bearer ${token}` 
        },
        // 4. REMOVE BODY: Since data is in the URL, you don't need a body
        body: null, 
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to add to watchlist');
      }
      
      alert(`${movie.title} added to watchlist!`);
    } catch (err: any) {
      console.error(err);
      alert(err.message);
    } finally {
      setAddingId(null);
    }
  };

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
                style={{ position: 'relative' }} // Ensure relative positioning for button placement
              >
                <div className="movie-title">{movie.title}</div>
                <div className="movie-meta">
                  {new Date(movie.release).getFullYear()} • {movie.genre}
                  {movie.rating != null && ` • ⭐ ${movie.rating.toFixed(1)}`}
                </div>

                {/* WATCHLIST BUTTON */}
                <button
                  onClick={(e) => handleAddToWatchlist(e, movie)}
                  disabled={addingId === movie.id}
                  style={{
                    marginTop: '10px',
                    padding: '5px 10px',
                    backgroundColor: '#0070f3',
                    color: 'white',
                    border: 'none',
                    borderRadius: '4px',
                    cursor: 'pointer',
                    fontSize: '0.8rem',
                    zIndex: 10 // Ensure it sits above other elements
                  }}
                >
                  {addingId === movie.id ? 'Adding...' : '+ Watchlist'}
                </button>

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