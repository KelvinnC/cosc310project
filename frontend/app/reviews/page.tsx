"use client";

import React, { useState, useEffect, useCallback } from 'react';
import Link from 'next/link';
import { useData } from '../context';
import { apiFetch } from '../../lib/api';
import './reviews.css';

const FASTAPI_URL = "http://127.0.0.1:8000";
const REVIEWS_PER_PAGE = 20;

interface ReviewWithMovie {
  id: number;
  movieId: string;
  movieTitle: string;
  authorId: string;
  rating: number;
  reviewTitle: string;
  reviewBody: string;
  flagged: boolean;
  votes: number;
  date: string;
  visible: boolean;
}

interface PaginatedReviews {
  reviews: ReviewWithMovie[];
  total: number;
  page: number;
  per_page: number;
  total_pages: number;
}

const ReviewsPage = () => {
  const { accessToken } = useData();
  const [mounted, setMounted] = useState(false);
  const [reviews, setReviews] = useState<ReviewWithMovie[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [searchQuery, setSearchQuery] = useState("");
  const [debouncedSearch, setDebouncedSearch] = useState("");
  const [ratingFilter, setRatingFilter] = useState<string>("");
  const [sortBy, setSortBy] = useState<string>("movie");
  const [sortOrder, setSortOrder] = useState<string>("desc");
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [totalReviews, setTotalReviews] = useState(0);

  useEffect(() => {
    setMounted(true);
  }, []);

  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedSearch(searchQuery);
    }, 300);
    return () => clearTimeout(timer);
  }, [searchQuery]);

  const fetchReviews = useCallback(async () => {
    setLoading(true);
    setError("");

    try {
      const params = new URLSearchParams();
      params.append('page', currentPage.toString());
      params.append('per_page', REVIEWS_PER_PAGE.toString());
      
      if (debouncedSearch) {
        params.append('search', debouncedSearch);
      }
      if (ratingFilter) {
        params.append('rating', ratingFilter);
      }
      if (sortBy) {
        params.append('sort_by', sortBy);
        params.append('order', sortOrder);
      }
      
      const url = `${FASTAPI_URL}/reviews?${params.toString()}`;
      const response = await apiFetch(url);
      
      if (!response.ok) {
        const data = await response.json();
        setError(data.detail || "Failed to fetch reviews");
        return;
      }

      const data: PaginatedReviews = await response.json();
      const visibleReviews = data.reviews.filter(r => r.visible);
      setReviews(visibleReviews);
      setTotalPages(data.total_pages);
      setTotalReviews(data.total);
    } catch (err) {
      console.error("Failed to fetch reviews:", err);
      setError("Network error. Please try again.");
    } finally {
      setLoading(false);
    }
  }, [debouncedSearch, ratingFilter, sortBy, sortOrder, currentPage]);

  useEffect(() => {
    fetchReviews();
  }, [fetchReviews]);

  useEffect(() => {
    setCurrentPage(1);
  }, [debouncedSearch, ratingFilter, sortBy, sortOrder]);

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
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

  return (
    <div className="reviews-page">
      <div className="reviews-container">
        <div className="reviews-header">
          <h1>Reviews</h1>
          <div className="reviews-actions">
            <input
              type="text"
              placeholder="Search by title, body, or movie..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="search-input"
            />
            <select
              value={ratingFilter}
              onChange={(e) => setRatingFilter(e.target.value)}
              className="filter-select"
            >
              <option value="">All Ratings</option>
              <option value="1">1 Star</option>
              <option value="2">2 Stars</option>
              <option value="3">3 Stars</option>
              <option value="4">4 Stars</option>
              <option value="5">5 Stars</option>
            </select>
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
              className="filter-select"
            >
              <option value="movie">Sort: Movie</option>
              <option value="rating">Sort: Rating</option>
            </select>
            <select
              value={sortOrder}
              onChange={(e) => setSortOrder(e.target.value)}
              className="filter-select"
            >
              <option value="desc">Descending</option>
              <option value="asc">Ascending</option>
            </select>
            {mounted && accessToken && (
              <Link href="/reviews/new" className="action-button">
                + New Review
              </Link>
            )}
          </div>
        </div>

        {error && (
          <div className="error-container">
            <p className="error-message">Error: {error}</p>
          </div>
        )}

        <div className="reviews-list">
          {loading ? (
            <>
              <div className="skeleton skeleton-card"></div>
              <div className="skeleton skeleton-card"></div>
              <div className="skeleton skeleton-card"></div>
            </>
          ) : reviews.length === 0 ? (
            <div className="empty-state">
              <h3>No reviews found</h3>
              <p>
                {searchQuery 
                  ? "Try adjusting your search or filters"
                  : mounted && accessToken 
                    ? "Be the first to write a review!"
                    : "Login to write the first review!"}
              </p>
              {mounted && accessToken && (
                <Link href="/reviews/new" className="action-button back-link-margin">
                  Write a Review
                </Link>
              )}
            </div>
          ) : (
            reviews.map((review: ReviewWithMovie) => {
              return (
                <div key={review.id} className="review-card">
                  <div className="review-card-header">
                    <div>
                      <p className="review-card-movie">{review.movieTitle}</p>
                      <h3 className="review-card-title">{review.reviewTitle}</h3>
                    </div>
                    <span className="review-card-rating">{renderStars(review.rating)}</span>
                  </div>
                  <p className="review-card-body">{review.reviewBody}</p>
                  <div className="review-card-footer">
                    <span>{formatDate(review.date)} • {review.votes} votes</span>
                    <div className="review-card-actions">
                      <Link href={`/reviews/${review.id}`} className="review-card-link">
                        Read More
                      </Link>
                    </div>
                  </div>
                </div>
              );
            })
          )}
        </div>

        {totalPages > 1 && (
          <div className="pagination">
            <button
              onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
              disabled={currentPage === 1}
              className="pagination-button"
            >
              ← Previous
            </button>
            <span className="pagination-info">
              Page {currentPage} of {totalPages} ({totalReviews} reviews)
            </span>
            <button
              onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
              disabled={currentPage === totalPages}
              className="pagination-button"
            >
              Next →
            </button>
          </div>
        )}

        <div className="page-footer">
          <Link href="/" className="form-link">
            ← Back to Home
          </Link>
        </div>
      </div>
    </div>
  );
};

export default ReviewsPage;
