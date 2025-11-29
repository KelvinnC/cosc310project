"use client";

import React, { useState, useEffect, useCallback } from 'react';
import Link from 'next/link';
import { useRouter, useParams } from 'next/navigation';
import { useData } from '../../../context';
import { apiFetch } from '../../../../lib/api';
import '../../reviews.css';

// TODO: Use environment variable for production: process.env.NEXT_PUBLIC_API_URL
const FASTAPI_URL = "http://127.0.0.1:8000";

interface Review {
  id: number;
  movieId: string;
  authorId: string;
  rating: number;
  reviewTitle: string;
  reviewBody: string;
  flagged: boolean;
  votes: number;
  date: string;
  visible: boolean;
}

interface Movie {
  id: string;
  title: string;
}

const EditReviewPage = () => {
  const router = useRouter();
  const params = useParams();
  const reviewId = params.id as string;
  const { accessToken } = useData();
  const [mounted, setMounted] = useState(false);
  
  // Original review data
  const [originalReview, setOriginalReview] = useState<Review | null>(null);
  const [movie, setMovie] = useState<Movie | null>(null);
  
  // Form state
  const [rating, setRating] = useState(3);
  const [reviewTitle, setReviewTitle] = useState("");
  const [reviewBody, setReviewBody] = useState("");
  
  // UI state
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");
  const [currentUserId, setCurrentUserId] = useState<string | null>(null);

  useEffect(() => {
    setMounted(true);
  }, []);

  // Decode JWT to get current user ID
  useEffect(() => {
    const token = accessToken as string | null;
    if (token && typeof token === 'string') {
      try {
        const payload = JSON.parse(atob(token.split('.')[1]));
        setCurrentUserId(payload.user_id || payload.sub);
      } catch {
        // Invalid token
      }
    }
  }, [accessToken]);

  const fetchReview = useCallback(async () => {
    setLoading(true);
    setError("");

    try {
      const response = await apiFetch(`${FASTAPI_URL}/reviews/${reviewId}`);
      
      if (!response.ok) {
        if (response.status === 404) {
          setError("Review not found");
        } else {
          const data = await response.json();
          setError(data.detail || "Failed to fetch review");
        }
        return;
      }

      const reviewData: Review = await response.json();
      setOriginalReview(reviewData);
      
      // Populate form with existing values
      setRating(reviewData.rating);
      setReviewTitle(reviewData.reviewTitle);
      setReviewBody(reviewData.reviewBody);

      // Fetch movie info
      if (reviewData.movieId) {
        const movieRes = await apiFetch(`${FASTAPI_URL}/movies/${reviewData.movieId}`);
        if (movieRes.ok) {
          const movies = await movieRes.json();
          if (movies.length > 0) {
            setMovie({ id: movies[0].id, title: movies[0].title });
          }
        }
      }
    } catch (err) {
      console.error("Failed to fetch review:", err);
      setError("Network error. Please try again.");
    } finally {
      setLoading(false);
    }
  }, [reviewId]);

  useEffect(() => {
    if (mounted && !accessToken) {
      router.push('/login');
      return;
    }
    if (reviewId && mounted) {
      fetchReview();
    }
  }, [reviewId, mounted, accessToken, router, fetchReview]);

  // Check if user is the author
  useEffect(() => {
    if (originalReview && currentUserId && originalReview.authorId !== currentUserId) {
      setError("You can only edit your own reviews");
    }
  }, [originalReview, currentUserId]);

  const validateForm = (): boolean => {
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

    setSubmitting(true);
    setError("");

    try {
      const response = await apiFetch(`${FASTAPI_URL}/reviews/${reviewId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          rating,
          reviewTitle: reviewTitle.trim(),
          reviewBody: reviewBody.trim()
        })
      });

      if (!response.ok) {
        const data = await response.json();
        setError(data.detail || "Failed to update review");
        return;
      }

      router.push(`/reviews/${reviewId}`);
    } catch (err) {
      console.error("Failed to update review:", err);
      setError("Network error. Please try again.");
    } finally {
      setSubmitting(false);
    }
  };

  const isAuthor = currentUserId && originalReview && originalReview.authorId === currentUserId;

  if (!mounted || loading) {
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
          <p>Please <Link href="/login">login</Link> to edit reviews.</p>
        </div>
      </div>
    );
  }

  if (error && !originalReview) {
    return (
      <div className="review-form-page">
        <div className="error-container">
          <p className="error-message">Error: {error}</p>
        </div>
        <Link href="/reviews" className="action-button" style={{ marginTop: '16px' }}>
          ← Back to Reviews
        </Link>
      </div>
    );
  }

  if (!isAuthor) {
    return (
      <div className="review-form-page">
        <div className="error-container">
          <p className="error-message">Error: You can only edit your own reviews</p>
        </div>
        <Link href={`/reviews/${reviewId}`} className="action-button" style={{ marginTop: '16px' }}>
          ← Back to Review
        </Link>
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
        <h2>Edit Review</h2>

        <div className="form-group">
          <label>Movie</label>
          <input
            type="text"
            value={movie?.title || "Loading..."}
            className="form-input"
            disabled
            style={{ backgroundColor: '#e0e0e0' }}
          />
          <span style={{ fontSize: '12px', opacity: 0.8 }}>Movie cannot be changed</span>
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
              disabled={submitting}
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
            disabled={submitting}
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
            disabled={submitting}
            maxLength={1000}
          />
          <span className="char-count">{reviewBody.length}/1000</span>
        </div>

        <div style={{ display: 'flex', gap: '12px', width: '100%' }}>
          <button
            type="submit"
            className="submit-button"
            disabled={submitting}
            style={{ flex: 1 }}
          >
            {submitting ? "Saving..." : "Save Changes"}
          </button>
          <Link 
            href={`/reviews/${reviewId}`} 
            className="action-button secondary"
            style={{ 
              flex: 1, 
              display: 'flex', 
              alignItems: 'center', 
              justifyContent: 'center',
              height: '2.5rem',
              textDecoration: 'none'
            }}
          >
            Cancel
          </Link>
        </div>

        <div className="form-links">
          <Link href="/reviews" className="form-link">← Back to Reviews</Link>
        </div>
      </form>
    </div>
  );
};

export default EditReviewPage;
