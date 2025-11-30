"use client";

import React, { useState, useEffect, useCallback } from 'react';
import './battles.css';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useData } from '../context';
import { apiFetch } from '../../lib/api';

const FASTAPI_URL = "http://127.0.0.1:8000";

interface Review {
  id: number;
  authorId: string;
  movieId: string;
  rating: number;
  reviewTitle: string;
  reviewBody: string;
  votes: number;
  date: string;
}

interface Movie {
  id: string;
  title: string;
}

interface Battle {
  id: string;
  review1Id: number;
  review2Id: number;
  winnerId: number | null;
  startedAt: string;
  endedAt: string | null;
}

const Page = () => {
  const router = useRouter();
  const { accessToken } = useData();
  const [battle, setBattle] = useState<Battle | null>(null);
  const [review1, setReview1] = useState<Review | null>(null);
  const [review2, setReview2] = useState<Review | null>(null);
  const [movie1, setMovie1] = useState<Movie | null>(null);
  const [movie2, setMovie2] = useState<Movie | null>(null);
  const [winnerMovie, setWinnerMovie] = useState<Movie | null>(null);
  const [selectedReviewId, setSelectedReviewId] = useState<number | null>(null);
  const [winningReview, setWinningReview] = useState<Review | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true); 
  const [submitting, setSubmitting] = useState(false);
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  const fetchMovie = async (movieId: string): Promise<Movie | null> => {
    try {
      const res = await apiFetch(`${FASTAPI_URL}/movies/${movieId}`);
      if (res.ok) {
        const movies = await res.json();
        if (movies.length > 0) {
          return { id: movies[0].id, title: movies[0].title };
        }
      }
    } catch (err) {
      // Silently fail - movie title is optional for display
      console.error("Failed to fetch movie:", err);
    }
    return null;
  };

  const createBattle = useCallback(async () => {
    setLoading(true);
    setError("");
    setWinningReview(null);
    setWinnerMovie(null);
    setSelectedReviewId(null);
    setMovie1(null);
    setMovie2(null);

    try {
      const response = await apiFetch(`${FASTAPI_URL}/battles`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        if (response.status === 401) {
          router.push('/login');
          return;
        }
        const data = await response.json();
        const errorMessage = data.detail || "Failed to create battle";
        setError(errorMessage);
        return;
      }

      const battleData: Battle = await response.json();
      setBattle(battleData);

      const [res1, res2] = await Promise.all([
        apiFetch(`${FASTAPI_URL}/reviews/${battleData.review1Id}`),
        apiFetch(`${FASTAPI_URL}/reviews/${battleData.review2Id}`)
      ]);

      const r1: Review | null = res1.ok ? await res1.json() : null;
      const r2: Review | null = res2.ok ? await res2.json() : null;

      setReview1(r1);
      setReview2(r2);

      const [m1, m2] = await Promise.all([
        r1?.movieId ? fetchMovie(r1.movieId) : Promise.resolve(null),
        r2?.movieId ? fetchMovie(r2.movieId) : Promise.resolve(null)
      ]);

      setMovie1(m1);
      setMovie2(m2);
    } catch (err) {
      console.error("Failed to create battle:", err);
      setError("Network error. Please try again.");
    } finally {
      setLoading(false);
    }
  }, [router]);

  useEffect(() => {
    if (!mounted) return;
    
    if (!accessToken) {
      router.push('/login');
      return;
    }
    createBattle();
  }, [mounted, accessToken, router, createBattle]);

  const submitVote = async () => {
    if (!battle || !selectedReviewId) {
      setError("Please select a review");
      return;
    }

    setSubmitting(true);
    setError("");

    try {
      const response = await apiFetch(`${FASTAPI_URL}/battles/${battle.id}/votes`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          winnerId: selectedReviewId
        })
      });

      if (!response.ok) {
        if (response.status === 401) {
          router.push('/login');
          return;
        }
        const data = await response.json();
        const errorMessage = data.detail || "Failed to submit vote";
        setError(errorMessage);
        return;
      }

      const winner: Review = await response.json();
      setWinningReview(winner);

      if (winner.movieId) {
        const movie = await fetchMovie(winner.movieId);
        setWinnerMovie(movie);
      }
    } catch (err) {
      console.error("Failed to submit vote:", err);
      setError("Network error. Please try again.");
    } finally {
      setSubmitting(false);
    }
  };

  const handleKeyDown = (reviewId: number) => (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      setSelectedReviewId(reviewId);
    }
  };

  if (!mounted || loading) {
    return (
      <div className="battles-page">
        <div className="battles-box">
          <h1>ReviewBattle</h1>
          <h2>Choose the Better Review</h2>
          <div className="reviews-container">
            <div className="review-card skeleton">
              <div className="skeleton-line skeleton-title"></div>
              <div className="skeleton-line skeleton-subtitle"></div>
              <div className="skeleton-line"></div>
              <div className="skeleton-line"></div>
              <div className="skeleton-line skeleton-short"></div>
            </div>
            <div className="vs-divider">VS</div>
            <div className="review-card skeleton">
              <div className="skeleton-line skeleton-title"></div>
              <div className="skeleton-line skeleton-subtitle"></div>
              <div className="skeleton-line"></div>
              <div className="skeleton-line"></div>
              <div className="skeleton-line skeleton-short"></div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (!accessToken) {
    return (
      <div className="battles-page">
        <div className="battles-box">
          <h1>ReviewBattle</h1>
          <p>Please <Link href="/login">login</Link> to participate in battles.</p>
        </div>
      </div>
    );
  }

  if (winningReview) {
    return (
      <div className="battles-page">
        <div className="battles-box result-box">
          <h1>ReviewBattle</h1>
          <h2>Winner!</h2>
          <div className="winner-card">
            {winnerMovie && <p className="review-movie">Movie: {winnerMovie.title}</p>}
            <h3 className="review-title">{winningReview.reviewTitle}</h3>
            <p className="review-rating">Rating: {winningReview.rating}/10</p>
            <p className="review-body">{winningReview.reviewBody}</p>
            <p className="review-votes">Total Votes: {winningReview.votes}</p>
          </div>
          <button className="battle-button" onClick={createBattle}>
            New Battle
          </button>
          <Link href="/" className="home-link">Back to Home</Link>
        </div>
      </div>
    );
  }

  return (
    <div className="battles-page">
      {error && (
        <div className="error-container">
          <p className="error-message">Error: {error}</p>
        </div>
      )}
      <div className="battles-box">
        <h1>ReviewBattle</h1>
        <h2>Choose the Better Review</h2>
        
        {battle && review1 && review2 ? (
          <>
            <div className="reviews-container">
              <div 
                className={`review-card ${selectedReviewId === review1.id ? 'selected' : ''}`}
                onClick={() => setSelectedReviewId(review1.id)}
                onKeyDown={handleKeyDown(review1.id)}
                tabIndex={0}
                role="button"
                aria-pressed={selectedReviewId === review1.id}
                aria-label={`Select review: ${review1.reviewTitle}`}
              >
                {movie1 && <p className="review-movie">{movie1.title}</p>}
                <h3 className="review-title">{review1.reviewTitle}</h3>
                <p className="review-rating">Rating: {review1.rating}/10</p>
                <p className="review-body">{review1.reviewBody}</p>
              </div>
              
              <div className="vs-divider">VS</div>
              
              <div 
                className={`review-card ${selectedReviewId === review2.id ? 'selected' : ''}`}
                onClick={() => setSelectedReviewId(review2.id)}
                onKeyDown={handleKeyDown(review2.id)}
                tabIndex={0}
                role="button"
                aria-pressed={selectedReviewId === review2.id}
                aria-label={`Select review: ${review2.reviewTitle}`}
              >
                {movie2 && <p className="review-movie">{movie2.title}</p>}
                <h3 className="review-title">{review2.reviewTitle}</h3>
                <p className="review-rating">Rating: {review2.rating}/10</p>
                <p className="review-body">{review2.reviewBody}</p>
              </div>
            </div>
            
            <button 
              className="battle-button"
              onClick={submitVote}
              disabled={!selectedReviewId || submitting}
            >
              {submitting ? "Submitting..." : "Submit Vote"}
            </button>
          </>
        ) : (
          <p>No reviews available for battle.</p>
        )}
        
        <Link href="/" className="home-link">Back to Home</Link>
      </div>
    </div>
  );
};

export default Page;
