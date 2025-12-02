"use client";

import React, { useState, useEffect, useCallback } from 'react';
import Link from 'next/link';
import { useRouter, useParams } from 'next/navigation';
import { useData } from '../../context';
import { apiFetch } from '../../../lib/api';
import { getUserIdFromToken } from '../../../lib/auth';
import { collapseWhitespace } from '@/lib/utils';
import '../reviews.css';

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
  const [userHasFlagged, setUserHasFlagged] = useState(false);
  const [currentUserId, setCurrentUserId] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState("");
  const [comments, setComments] = useState<any>([])
  const [currentPost, setCurrentPost] = useState<string>("")
  const [refresh, setRefresh] = useState(false)

  const submitComment = async (e: any) => {
    e.preventDefault()
    if (currentPost == "") {
      alert("Comment cannot be empty")
      return
    }
    const response = await apiFetch(`${FASTAPI_URL}/reviews/${reviewId}/comments`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        "commentBody": currentPost
      })
    })
    if (response.ok) {
      setCurrentPost("")
      setRefresh(r => !r)
    }
  }

  useEffect(() => {
    const fetchAllComments = async () => {
      const response = await apiFetch(`${FASTAPI_URL}/reviews/${reviewId}/comments`,{
        method: 'GET'
      })
      if (!response.ok) {
        console.error("Error: Could not fetch comments")
      }
      const data = await response.json()
      setComments(data)
  }
  fetchAllComments()
  }, [refresh])

  useEffect(() => {
    setCurrentUserId(getUserIdFromToken(accessToken as string | null));
  }, [accessToken]);

  const fetchFlagStatus = useCallback(async () => {
    if (!accessToken) return;
    
    try {
      const response = await apiFetch(`${FASTAPI_URL}/reviews/${reviewId}/flag/status`);
      if (response.ok) {
        const data = await response.json();
        setUserHasFlagged(data.has_flagged);
      }
    } catch (err) {
      console.error("Failed to fetch flag status:", err);
    }
  }, [reviewId, accessToken]);

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

      if (reviewData.movieId) {
        const movieRes = await apiFetch(`${FASTAPI_URL}/movies/${reviewData.movieId}`);
        if (movieRes.ok) {
          const movies = await movieRes.json();
          if (movies.length > 0) {
            setMovie({ id: movies[0].id, title: movies[0].title });
          }
        }
      }
      
      fetchFlagStatus();
    } catch (err) {
      console.error("Failed to fetch review:", err);
      setError("Network error. Please try again.");
    } finally {
      setLoading(false);
    }
  }, [reviewId, fetchFlagStatus]);

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
        if (response.status === 401) {
          router.push('/login');
          return;
        }
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
      router.push('/login');
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
        if (response.status === 401) {
          router.push('/login');
          return;
        }
        const data = await response.json();
        const errorMessage = data.detail || "Failed to flag review";
        
        if (errorMessage.toLowerCase().includes("already flagged")) {
          setUserHasFlagged(true);
        } else {
          setError(errorMessage);
        }
        return;
      }

      setUserHasFlagged(true);
      setSuccessMessage("Review flagged successfully. Thank you for your report.");
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

  const renderStars = (rating: number) => {
    return (
      <span className="star-display">
        {[1, 2, 3, 4, 5].map((star) => (
          <span key={star} className={`star ${rating >= star ? 'filled' : ''}`}>★</span>
        ))}
      </span>
    );
  };

  const isAuthor = currentUserId && review && review.authorId === currentUserId;

  if (loading) {
    return (
      <div className="review-detail-page">
        <div className="review-detail-box skeleton skeleton-detail"></div>
      </div>
    );
  }

  if (error && !review) {
    return (
      <div className="review-detail-page">
        <div className="error-container detail-message">
          <p className="error-message">Error: {error}</p>
        </div>
        <Link href="/reviews" className="action-button back-link-margin">
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
          <Link href="/reviews" className="action-button back-link-margin">
            ← Back to Reviews
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="review-detail-page">
      {error && (
        <div className="error-container detail-message">
          <p className="error-message">Error: {error}</p>
        </div>
      )}
      {successMessage && (
        <div className="success-container detail-message">
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
          <span className="review-detail-rating">{renderStars(review.rating)}</span>
        </div>

        <p className="review-detail-body">{collapseWhitespace(review.reviewBody)}</p>
                        <div className="comments-section">
          <h2>Leave a Comment</h2>
          <form 
          className="comments-post"
          onSubmit={(e) => submitComment(e)}>
            <textarea className="comment-body"
            placeholder="What do you think of this review?"
            onChange={(e) => setCurrentPost(e.target.value)}
            value={currentPost}>
            </textarea>
            <button 
            className="submit-comment-btn">Submit Comment</button>
          </form>
          <h2>Comments</h2>
          <div className="comments-show">
            {comments.length > 0 ? (
              <div>
                {comments.map((comment: any, idx: any) => (
                  <div key={idx} className="comment">
                    <div className="comment-header">
                      <span>{comment["authorUsername"]}</span>
                      <span>{comment["date"].split("T")[0]}</span>
                    </div>
                    <span>{comment["commentBody"]}</span>
                  </div>
                ))}
             </div>
            ) : (
              <p>No comments to show</p>
            )}
          </div>
        </div>
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
          {accessToken && !isAuthor && !userHasFlagged && (
            <button
              onClick={handleFlag}
              className="action-button flag"
              disabled={flagging}
            >
              {flagging ? "Flagging..." : "Flag as Inappropriate"}
            </button>
          )}
          {accessToken && !isAuthor && userHasFlagged && (
            <span className="flagged-badge">
              You have flagged this review
            </span>
          )}
        </div>
      </div>

      <div className="page-footer">
        <Link href="/reviews" className="form-link">
          ← Back to Reviews
        </Link>
      </div>
    </div>
  );
};

export default ReviewDetailPage;
