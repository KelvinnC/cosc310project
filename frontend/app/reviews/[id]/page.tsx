"use client";

import React, { useState, useEffect, useCallback } from 'react';
import Link from 'next/link';
import { useRouter, useParams } from 'next/navigation';
import { useData } from '../../context';
import { apiFetch } from '../../../lib/api';
import '../reviews.css';

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

const ReviewDetailPage = () => {
  const router = useRouter();
  const params = useParams();
  const reviewId = params.id as string;
  const { accessToken } = useData();
  
  const [review, setReview] = useState<Review | null>(null);
  const [movie, setMovie] = useState<Movie | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [deleting, setDeleting] = useState(false);
  const [flagging, setFlagging] = useState(false);
  const [currentUserId, setCurrentUserId] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState("");

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
      setReview(reviewData);

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
    if (reviewId) {
      fetchReview();
    }
  }, [reviewId, fetchReview]);

  const handleDelete = async () => {
    if (!confirm("Are you sure you want to delete this review? This action cannot be undone.")) {
      return;
    }

    setDeleting(true);
    setError("");

    try {
      const response = await apiFetch(`${FASTAPI_URL}/reviews/${reviewId}`, {
        method: 'DELETE'
      });

      if (!response.ok && response.status !== 204) {
        const data = await response.json();
        setError(data.detail || "Failed to delete review");
        return;
      }

      router.push('/reviews');
    } catch (err) {
      console.error("Failed to delete review:", err);
      setError("Network error. Please try again.");
    } finally {
      setDeleting(false);
    }
  };

  const handleFlag = async () => {
    if (!accessToken) {
      setError("Please login to flag reviews");
      return;
    }

    setFlagging(true);
    setError("");
    setSuccessMessage("");

    try {
      const response = await apiFetch(`${FASTAPI_URL}/reviews/${reviewId}/flag`, {
        method: 'POST'
      });

      if (!response.ok) {
        const data = await response.json();
        setError(data.detail || "Failed to flag review");
        return;
      }

      setSuccessMessage("Review flagged successfully. Thank you for your report.");
      // Refresh review data
      fetchReview();
    } catch (err) {
      console.error("Failed to flag review:", err);
      setError("Network error. Please try again.");
    } finally {
      setFlagging(false);
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  const isAuthor = currentUserId && review && review.authorId === currentUserId;

  if (loading) {
    return (
      <div className="review-detail-page">
        <div className="review-detail-box skeleton" style={{ height: '400px' }}></div>
      </div>
    );
  }

  if (error && !review) {
    return (
      <div className="review-detail-page">
        <div className="error-container" style={{ maxWidth: '700px' }}>
          <p className="error-message">Error: {error}</p>
        </div>
        <Link href="/reviews" className="action-button" style={{ marginTop: '16px' }}>
          ← Back to Reviews
        </Link>
      </div>
    );
  }

  if (!review) {
    return (
      <div className="review-detail-page">
        <div className="empty-state">
          <h3>Review not found</h3>
          <Link href="/reviews" className="action-button" style={{ marginTop: '16px' }}>
            ← Back to Reviews
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="review-detail-page">
      {error && (
        <div className="error-container" style={{ maxWidth: '700px' }}>
          <p className="error-message">Error: {error}</p>
        </div>
      )}
      {successMessage && (
        <div className="success-container" style={{ maxWidth: '700px' }}>
          <p className="success-message">{successMessage}</p>
        </div>
      )}
      
      <div className="review-detail-box">
        <div className="review-detail-header">
          <div>
            {movie && (
              <p className="review-detail-movie">{movie.title}</p>
            )}
            <h1 className="review-detail-title">{review.reviewTitle}</h1>
          </div>
          <span className="review-detail-rating">{review.rating}/5</span>
        </div>

        <p className="review-detail-body">{review.reviewBody}</p>

        <div className="review-detail-meta">
          <span>{formatDate(review.date)}</span>
          <span>{review.votes} votes</span>
        </div>

        <div className="review-detail-actions">
          {isAuthor && (
            <>
              <Link href={`/reviews/${review.id}/edit`} className="action-button">
                Edit
              </Link>
              <button
                onClick={handleDelete}
                className="action-button danger"
                disabled={deleting}
              >
                {deleting ? "Deleting..." : "Delete"}
              </button>
            </>
          )}
          {accessToken && !isAuthor && !review.flagged && (
            <button
              onClick={handleFlag}
              className="action-button secondary"
              disabled={flagging}
            >
              {flagging ? "Flagging..." : "🚩 Flag as Inappropriate"}
            </button>
          )}
          {review.flagged && (
            <span style={{ color: '#ff9800', fontWeight: 500 }}>
              ⚠️ This review has been flagged
            </span>
          )}
        </div>
      </div>

      <div style={{ marginTop: '24px' }}>
        <Link href="/reviews" className="form-link" style={{ color: '#4292c6' }}>
          ← Back to Reviews
        </Link>
      </div>
    </div>
  );
};

export default ReviewDetailPage;
