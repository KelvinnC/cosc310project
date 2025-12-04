'use client';

import React, { useEffect, useMemo, useState } from 'react';
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
  const [searchQuery, setSearchQuery] = useState('');
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

  const filteredMovies = useMemo(() => {
    const query = searchQuery.trim().toLowerCase();
    const filtered = query
      ? movies.filter((movie) => {
          const title = movie.title?.toLowerCase() || '';
          const description = movie.description?.toLowerCase() || '';
          const genre = movie.genre?.toLowerCase() || '';
          return (
            title.includes(query) ||
            description.includes(query) ||
            genre.includes(query)
          );
        })
      : movies;

    return [...filtered].sort((a, b) => a.title.localeCompare(b.title));
  }, [movies, searchQuery]);

  const handleAddToWatchlist = async (e: React.MouseEvent, movie: Movie) => {
    e.preventDefault(); 
    e.stopPropagation();

    setAddingId(movie.id);

    try {
      // 1. URL: Keep it clean (no query parameters)
      const response = await apiFetch(`${FASTAPI_URL}/watchlist/add`, {
        method: 'POST',
        headers: {
          // 2. HEADER: Required so the backend knows to parse the body as JSON
          'Content-Type': 'application/json', 
        },
        // 3. BODY: Send the ID as a JSON string
        body: JSON.stringify({ movie_id: movie.id }), 
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        let errorMessage = 'Failed to add to watchlist';
        
        if (typeof errorData.detail === 'string') {
            errorMessage = errorData.detail;
        } else if (Array.isArray(errorData.detail)) {
            errorMessage = errorData.detail[0]?.msg || JSON.stringify(errorData.detail);
        } else if (errorData.detail) {
            errorMessage = JSON.stringify(errorData.detail);
        }
        
        throw new Error(errorMessage);
      }
      
      const title = typeof movie.title === 'string' ? movie.title : 'Movie';
      alert(`${title} added to watchlist!`);
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
        <input
          type="text"
          className="movies-search-input"
          placeholder="Search by title, description, or genre..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
        />
        {error && <p style={{ color: 'red' }}>Error: {error}</p>}
        <div className="movies-grid">
          {filteredMovies.length > 0 ? (
            filteredMovies.map((movie) => (
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