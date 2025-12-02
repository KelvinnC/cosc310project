'use client';

import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import './watchlist.css';

const FASTAPI_URL = "http://127.0.0.1:8000";

interface Movie {
  id: string;
  title: string;
  description?: string;
  duration?: number;
  genre?: string;
  release?: string;
  rating?: number;
}

interface Watchlist {
  id: string;
  author_id: string;
  movies: Movie[];
}

const WatchlistPage = () => {
  const [watchlist, setWatchlist] = useState<Watchlist | null>(null);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchWatchlist = async () => {
      try {
        const token = localStorage.getItem("token");

        const response = await fetch(`${FASTAPI_URL}/watchlist`, {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });

        if (!response.ok) {
          throw new Error('Failed to fetch watchlist');
        }

        const data = await response.json();
        setWatchlist(data);
      } catch (err: any) {
        setError(err.message || 'Error fetching watchlist');
      }
    };

    fetchWatchlist();
  }, []);

  return (
    <div className="watchlist-page">
      <div className="watchlist-box">
        <h1>My Watchlist</h1>

        {error && <p style={{ color: 'red' }}>Error: {error}</p>}

        <div className="watchlist-grid">
          {watchlist?.movies?.length ? (
            watchlist.movies.map((movie) => (
              <Link
                key={movie.id}
                href={`/movies/${movie.id}`}
                className="watchlist-card"
              >
                <div className="watchlist-title">{movie.title}</div>
                <div className="watchlist-meta">
                  {movie.release && new Date(movie.release).getFullYear()}
                  {movie.genre && ` • ${movie.genre}`}
                  {movie.rating != null && ` • ⭐ ${movie.rating.toFixed(1)}`}
                </div>
              </Link>
            ))
          ) : (
            <p>No movies in your watchlist.</p>
          )}
        </div>
      </div>
    </div>
  );
};

export default WatchlistPage;
