'use client';

import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import './watchlist.css';
import { apiFetch } from '../../lib/api'; // Ensure this path is correct

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

interface WatchlistRawResponse {
  id: number;
  authorId: string;
  movieIds: string[];
}

const WatchlistPage = () => {
  const [movies, setMovies] = useState<Movie[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const router = useRouter();

  useEffect(() => {
    const fetchWatchlistAndMovies = async () => {
      try {
        // 1. Get Watchlist IDs using apiFetch
        // apiFetch handles the Authorization header automatically
        const watchlistRes = await apiFetch(`${FASTAPI_URL}/watchlist`);

        // Handle Session Expiry
        if (watchlistRes.status === 401) {
            router.push('/login');
            return;
        }

        if (!watchlistRes.ok) {
            throw new Error('Failed to load watchlist');
        }

        const watchlistData: WatchlistRawResponse = await watchlistRes.json();

        if (!watchlistData.movieIds || watchlistData.movieIds.length === 0) {
            setMovies([]);
            setLoading(false);
            return;
        }

        // 2. Fetch Details
        const moviePromises = watchlistData.movieIds.map(async (id) => {
            try {
                // Using apiFetch here too for consistency, though movies might be public
                const res = await apiFetch(`${FASTAPI_URL}/movies/${id}`);
                
                if (!res.ok) return null;
                
                let data = await res.json();

                // Handle Array Response
                if (Array.isArray(data)) {
                    data = data.length > 0 ? data[0] : null;
                }
                
                if (!data || !data.id) return null; 

                return data;
            } catch (e) {
                return null;
            }
        });

        const moviesResults = await Promise.all(moviePromises);
        const validMovies = moviesResults.filter((m): m is Movie => m !== null);
        
        setMovies(validMovies);

      } catch (err: any) {
        console.error(err);
        setError(err.message || "Error loading watchlist");
      } finally {
        setLoading(false);
      }
    };

    fetchWatchlistAndMovies();
  }, [router]);

  if (loading) {
    return <div className="watchlist-page"><p>Loading watchlist...</p></div>;
  }

  return (
    <div className="watchlist-page">
      <div className="watchlist-box">
        <h1>My Watchlist</h1>

        {error && <p style={{ color: 'red' }}>Error: {error}</p>}

        <div className="watchlist-grid">
          {movies.length > 0 ? (
            movies.map((movie) => (
              <Link
                key={movie.id}
                href={`/movies/${movie.id}`}
                className="watchlist-card"
              >
                <div className="watchlist-title">{movie.title}</div>
                <div className="watchlist-meta">
                  {movie.release ? new Date(movie.release).getFullYear() : 'N/A'}
                  {movie.genre && ` • ${movie.genre}`}
                  {movie.rating != null && ` • ⭐ ${movie.rating.toFixed(1)}`}
                </div>
              </Link>
            ))
          ) : (
            <div style={{ textAlign: 'center', width: '100%' }}>
                <p>No movies in your watchlist.</p>
                <Link href="/movies" style={{ color: 'white', textDecoration: 'underline' }}>
                    Browse movies to add some!
                </Link>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default WatchlistPage;