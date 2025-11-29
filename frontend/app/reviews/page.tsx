"use client";

import React, { useState, useEffect, useCallback } from 'react';
import Link from 'next/link';
import { useData } from '../context';
import { apiFetch } from '../../lib/api';
import './reviews.css';

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

const ReviewsPage = () => {
  const { accessToken } = useData();
  const [mounted, setMounted] = useState(false);
  const [reviews, setReviews] = useState<Review[]>([]);
  const [movies, setMovies] = useState<Map<string, Movie>>(new Map());
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [searchQuery, setSearchQuery] = useState("");
  const [ratingFilter, setRatingFilter] = useState<string>("");
  const [sortBy, setSortBy] = useState<string>("");
  const [sortOrder, setSortOrder] = useState<string>("desc");

  useEffect(() => {
    setMounted(true);
  }, []);

  const fetchMovieTitle = useCallback(async (movieId: string): Promise<Movie | null> => {
    try {
      const res = await apiFetch(`${FASTAPI_URL}/movies/${movieId}`);
      if (res.ok) {
        const data = await res.json();
        if (data.length > 0) {
          return { id: data[0].id, title: data[0].title };
        }
      }
    } catch {
      // Silently fail
    }
    return null;
  }, []);

  const fetchReviews = useCallback(async () => {
    setLoading(true);
    setError("");

    try {
      let url = `${FASTAPI_URL}/reviews`;
      const params = new URLSearchParams();
      
      if (ratingFilter) {
        params.append('rating', ratingFilter);
      }
      if (sortBy) {
        params.append('sort_by', sortBy);
        params.append('order', sortOrder);
      }
      
      if (params.toString()) {
        url += `?${params.toString()}`;
      }

      const response = await apiFetch(url);
      
      if (!response.ok) {
        const data = await response.json();
        setError(data.detail || "Failed to fetch reviews");
        return;
      }

      const reviewsData: Review[] = await response.json();
      
      // Filter visible reviews only
      const visibleReviews = reviewsData.filter(r => r.visible);
      setReviews(visibleReviews);

      // Fetch movie titles for all unique movieIds
      const uniqueMovieIds = [...new Set(visibleReviews.map(r => r.movieId))];
      const moviePromises = uniqueMovieIds.map(async (movieId) => {
        const movie = await fetchMovieTitle(movieId);
        return { movieId, movie };
      });

      const movieResults = await Promise.all(moviePromises);
      const movieMap = new Map<string, Movie>();
      movieResults.forEach(({ movieId, movie }) => {
        if (movie) {
          movieMap.set(movieId, movie);
        }
      });
      setMovies(movieMap);
    } catch (err) {
      console.error("Failed to fetch reviews:", err);
      setError("Network error. Please try again.");
    } finally {
      setLoading(false);
    }
  }, [ratingFilter, sortBy, sortOrder, fetchMovieTitle]);

  useEffect(() => {
    fetchReviews();
  }, [fetchReviews]);

  const filteredReviews = reviews.filter(review => {
    if (!searchQuery) return true;
    const query = searchQuery.toLowerCase();
    const movie = movies.get(review.movieId);
    return (
      review.reviewTitle.toLowerCase().includes(query) ||
      review.reviewBody.toLowerCase().includes(query) ||
      (movie && movie.title.toLowerCase().includes(query))
    );
  });

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  return (
    <div className="reviews-page">
      <div className="reviews-container">
        <div className="reviews-header">
          <h1>Reviews</h1>
          <div className="reviews-actions">
            <input
              type="text"
              placeholder="Search reviews..."
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
              <option value="">Sort By</option>
              <option value="rating">Rating</option>
              <option value="movie">Movie</option>
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
          ) : filteredReviews.length === 0 ? (
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
                <Link href="/reviews/new" className="action-button" style={{ marginTop: '16px' }}>
                  Write a Review
                </Link>
              )}
            </div>
          ) : (
            filteredReviews.map((review) => {
              const movie = movies.get(review.movieId);
              return (
                <div key={review.id} className="review-card">
                  <div className="review-card-header">
                    <div>
                      {movie && (
                        <p className="review-card-movie">{movie.title}</p>
                      )}
                      <h3 className="review-card-title">{review.reviewTitle}</h3>
                    </div>
                    <span className="review-card-rating">{review.rating}/5</span>
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

        <div style={{ textAlign: 'center', marginTop: '24px' }}>
          <Link href="/" className="form-link" style={{ color: '#4292c6' }}>
            ← Back to Home
          </Link>
        </div>
      </div>
    </div>
  );
};

export default ReviewsPage;
