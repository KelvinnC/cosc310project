'use client';

import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
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

// MATCHES THE JSON YOU FOUND
interface WatchlistRawResponse {
  id: number;
  authorId: string;
  movieIds: string[]; // We get IDs, not objects
}

const WatchlistPage = () => {
  // We will store the RESOLVED movies here, not the raw watchlist
  const [movies, setMovies] = useState<Movie[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const router = useRouter();

  useEffect(() => {
    const fetchWatchlistAndMovies = async () => {
      try {
        const token = localStorage.getItem("token");
        if (!token) { router.push('/login'); return; }

        // 1. Get Watchlist IDs
        const watchlistRes = await fetch(`${FASTAPI_URL}/watchlist`, {
          headers: { 'Authorization': `Bearer ${token}` }
        });

        if (watchlistRes.status === 401) {
            localStorage.removeItem('token');
            router.push('/login');
            return;
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
                const res = await fetch(`${FASTAPI_URL}/movies/${id}`);
                if (!res.ok) return null;
                
                let data = await res.json();

                // --- THE FIX: Handle Array Response ---
                // If the API returns [ {movie} ], grab the first item
                if (Array.isArray(data)) {
                    data = data.length > 0 ? data[0] : null;
                }
                // --------------------------------------
                
                // Validate the object has what we need
                // We check for 'id' because sometimes empty objects {} slip through
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