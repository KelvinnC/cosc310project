"use client";

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useData } from '../../context';
import { apiFetch } from '../../../lib/api';
import '../reviews.css';

// TODO: Use environment variable for production: process.env.NEXT_PUBLIC_API_URL
const FASTAPI_URL = "http://127.0.0.1:8000";

interface MovieSummary {
  id: string;
  title: string;
}

const NewReviewPage = () => {
  const router = useRouter();
  const { accessToken } = useData();
  const [mounted, setMounted] = useState(false);
  
  // Form state
  const [movieId, setMovieId] = useState("");
  const [movieSearch, setMovieSearch] = useState("");
  const [movieResults, setMovieResults] = useState<MovieSummary[]>([]);
  const [selectedMovie, setSelectedMovie] = useState<MovieSummary | null>(null);
  const [rating, setRating] = useState(3);
  const [reviewTitle, setReviewTitle] = useState("");
  const [reviewBody, setReviewBody] = useState("");
  
  // UI state
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

  // Search movies when user types
  useEffect(() => {
    const searchMovies = async () => {
      if (movieSearch.length < 2) {
        setMovieResults([]);
        return;
      }

      setSearchingMovies(true);
      try {
        const response = await apiFetch(
          `${FASTAPI_URL}/movies/search?title=${encodeURIComponent(movieSearch)}`
        );
        if (response.ok) {
          const data = await response.json();
          setMovieResults(data);
          setShowMovieDropdown(true);
        }
      } catch {
        // Silently fail
      } finally {
        setSearchingMovies(false);
      }
    };

    const debounce = setTimeout(searchMovies, 300);
    return () => clearTimeout(debounce);
  }, [movieSearch]);

  const selectMovie = (movie: MovieSummary) => {
    setSelectedMovie(movie);
    setMovieId(movie.id);
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
          <h1>Review Battle</h1>
          <p>Loading...</p>
        </div>
      </div>
    );
  }

  if (!accessToken) {
    return (
      <div className="review-form-page">
        <div className="review-form-box">
          <h1>Review Battle</h1>
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
        <h1>Review Battle</h1>
        <h2>Write a Review</h2>

        <div className="form-group" style={{ position: 'relative' }}>
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
            <div style={{
              position: 'absolute',
              top: '100%',
              left: 0,
              right: 0,
              background: 'white',
              borderRadius: '8px',
              boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
              maxHeight: '200px',
              overflowY: 'auto',
              zIndex: 10
            }}>
              {movieResults.map((movie) => (
                <div
                  key={movie.id}
                  onClick={() => selectMovie(movie)}
                  style={{
                    padding: '10px 12px',
                    cursor: 'pointer',
                    color: '#333',
                    borderBottom: '1px solid #eee'
                  }}
                  onMouseEnter={(e) => e.currentTarget.style.backgroundColor = '#f5f5f5'}
                  onMouseLeave={(e) => e.currentTarget.style.backgroundColor = 'white'}
                >
                  {movie.title}
                </div>
              ))}
            </div>
          )}
          {searchingMovies && (
            <span style={{ fontSize: '12px', opacity: 0.8 }}>Searching...</span>
          )}
          {selectedMovie && (
            <span style={{ fontSize: '12px', color: '#90EE90' }}>✓ {selectedMovie.title}</span>
          )}
        </div>

        <div className="form-group">
          <label htmlFor="rating">Rating</label>
          <div className="rating-input">
            <input
              id="rating"
              type="range"
              min="1"
              max="5"
              step="0.5"
              value={rating}
              onChange={(e) => setRating(parseFloat(e.target.value))}
              disabled={loading}
            />
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
