"use client";

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useData } from '../../context';
import { apiFetch } from '../../../lib/api';
import '../reviews.css';

const FASTAPI_URL = "http://127.0.0.1:8000";

interface MovieResult {
  movie_id: string;
  title: string;
  source: "local" | "tmdb";
  overview?: string;
  release_date?: string;
  poster_path?: string | null;
}

interface SearchAllResponse {
  local: MovieResult[];
  external: MovieResult[];
  source: "local" | "both" | "tmdb";
}

const getYear = (releaseDate?: string): string => {
  if (!releaseDate) return "";
  const year = releaseDate.split("-")[0];
  return year && year.length === 4 ? year : "";
};

const NewReviewPage = () => {
  const router = useRouter();
  const { accessToken } = useData();
  const [mounted, setMounted] = useState(false);
  
  const [movieId, setMovieId] = useState("");
  const [movieSearch, setMovieSearch] = useState("");
  const [movieResults, setMovieResults] = useState<MovieResult[]>([]);
  const [selectedMovie, setSelectedMovie] = useState<MovieResult | null>(null);
  const [rating, setRating] = useState(3);
  const [reviewTitle, setReviewTitle] = useState("");
  const [reviewBody, setReviewBody] = useState("");
  
  const [loading, setLoading] = useState(false);
  const [searchingMovies, setSearchingMovies] = useState(false);
  const [error, setError] = useState("");
  const [showMovieDropdown, setShowMovieDropdown] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  useEffect(() => {
    if (mounted && !accessToken) {
      router.push('/login');
    }
  }, [mounted, accessToken, router]);

  // Search movies when user types (using smart search with TMDb fallback)
  useEffect(() => {
    const searchMovies = async () => {
      if (selectedMovie) {
        setMovieResults([]);
        setShowMovieDropdown(false);
        return;
      }
      
      if (movieSearch.length < 2) {
        setMovieResults([]);
        return;
      }

      setSearchingMovies(true);
      try {
        const response = await apiFetch(
          `${FASTAPI_URL}/movies/search/all?title=${encodeURIComponent(movieSearch)}`
        );
        if (response.ok) {
          const data: SearchAllResponse = await response.json();
          // Combine local and external results
          const combinedResults: MovieResult[] = [...data.local, ...data.external];
          setMovieResults(combinedResults);
          setShowMovieDropdown(combinedResults.length > 0);
        }
      } catch {
      } finally {
        setSearchingMovies(false);
      }
    };

    const debounce = setTimeout(searchMovies, 300);
    return () => clearTimeout(debounce);
  }, [movieSearch, selectedMovie]);

  const selectMovie = (movie: MovieResult) => {
    setSelectedMovie(movie);
    setMovieId(movie.movie_id);
    setMovieSearch(movie.title);
    setShowMovieDropdown(false);
  };

  const validateForm = (): boolean => {
    if (!movieId) {
      setError("Please select a movie");
      return false;
    }
    if (reviewTitle.trim().length < 3) {
      setError("Title must be at least 3 characters");
      return false;
    }
    if (reviewTitle.trim().length > 100) {
      setError("Title must be less than 100 characters");
      return false;
    }
    if (reviewBody.trim().length < 50) {
      setError("Review body must be at least 50 characters");
      return false;
    }
    if (reviewBody.trim().length > 1000) {
      setError("Review body must be less than 1000 characters");
      return false;
    }
    setError("");
    return true;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) return;

    setLoading(true);
    setError("");

    try {
      const response = await apiFetch(`${FASTAPI_URL}/reviews`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          movieId,
          rating,
          reviewTitle: reviewTitle.trim(),
          reviewBody: reviewBody.trim()
        })
      });

      if (!response.ok) {
        if (response.status === 401) {
          router.push('/login');
          return;
        }
        const data = await response.json();
        setError(data.detail || "Failed to create review");
        return;
      }

      const newReview = await response.json();
      router.push(`/reviews/${newReview.id}`);
    } catch (err) {
      console.error("Failed to create review:", err);
      setError("Network error. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  if (!mounted) {
    return (
      <div className="review-form-page">
        <div className="review-form-box">
          <h1>Write a Review</h1>
          <p>Loading...</p>
        </div>
      </div>
    );
  }

  if (!accessToken) {
    return (
      <div className="review-form-page">
        <div className="review-form-box">
          <h1>Write a Review</h1>
          <p>Please <Link href="/login">login</Link> to write a review.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="review-form-page">
      {error && (
        <div className="error-container">
          <p className="error-message">Error: {error}</p>
        </div>
      )}
      <form className="review-form-box" onSubmit={handleSubmit}>
        <h1>Write a Review</h1>

        <div className="form-group movie-search-container">
          <label htmlFor="movie">Movie</label>
          <input
            id="movie"
            type="text"
            placeholder="Search for a movie..."
            value={movieSearch}
            onChange={(e) => {
              setMovieSearch(e.target.value);
              setSelectedMovie(null);
              setMovieId("");
            }}
            onFocus={() => movieResults.length > 0 && setShowMovieDropdown(true)}
            className="form-input"
            disabled={loading}
            autoComplete="off"
          />
          {showMovieDropdown && movieResults.length > 0 && (
            <div className="movie-dropdown">
              {movieResults.map((movie) => (
                <div
                  key={movie.movie_id}
                  onClick={() => selectMovie(movie)}
                  className="movie-dropdown-item"
                >
                  <span className="movie-title">
                    {movie.title}
                    {getYear(movie.release_date) && (
                      <span className="movie-year"> ({getYear(movie.release_date)})</span>
                    )}
                  </span>
                  {movie.source === "tmdb" && (
                    <span className="movie-source-badge">TMDb</span>
                  )}
                </div>
              ))}
            </div>
          )}
          <div className="helper-text-container">
            {searchingMovies && (
              <span className="helper-text">Searching...</span>
            )}
            {selectedMovie && (
              <span className="helper-text success">✓ {selectedMovie.title}</span>
            )}
          </div>
        </div>

        <div className="form-group">
          <label>Rating</label>
          <div className="star-rating">
            {[1, 2, 3, 4, 5].map((star) => (
              <button
                key={star}
                type="button"
                className={`star-button ${rating >= star ? 'filled' : ''}`}
                onClick={() => setRating(star)}
                disabled={loading}
                aria-label={`Rate ${star} star${star > 1 ? 's' : ''}`}
              >
                ★
              </button>
            ))}
            <span className="rating-value">{rating}/5</span>
          </div>
        </div>

        <div className="form-group">
          <label htmlFor="title">Review Title</label>
          <input
            id="title"
            type="text"
            placeholder="Enter a catchy title..."
            value={reviewTitle}
            onChange={(e) => setReviewTitle(e.target.value)}
            className="form-input"
            disabled={loading}
            maxLength={100}
          />
          <span className="char-count">{reviewTitle.length}/100</span>
        </div>

        <div className="form-group">
          <label htmlFor="body">Review</label>
          <textarea
            id="body"
            placeholder="Write your review (minimum 50 characters)..."
            value={reviewBody}
            onChange={(e) => setReviewBody(e.target.value)}
            className="form-textarea"
            disabled={loading}
            maxLength={1000}
          />
          <span className="char-count">{reviewBody.length}/1000</span>
        </div>

        <button
          type="submit"
          className="submit-button"
          disabled={loading || !movieId}
        >
          {loading ? "Publishing..." : "Publish Review"}
        </button>

        <div className="form-links">
          <Link href="/reviews" className="form-link">← Back to Reviews</Link>
        </div>
      </form>
    </div>
  );
};

export default NewReviewPage;
