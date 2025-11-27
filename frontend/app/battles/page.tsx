"use client";

import React, { useState, useEffect } from 'react';
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
  const [loading, setLoading] = useState(true); // Start true to avoid hydration mismatch
  const [submitting, setSubmitting] = useState(false);
  const [mounted, setMounted] = useState(false);

  // Handle hydration - wait for client-side mount
  useEffect(() => {
    setMounted(true);
  }, []);

  useEffect(() => {
    if (!mounted) return;
    
    if (!accessToken) {
      router.push('/login');
      return;
    }
    createBattle();
  }, [mounted, accessToken]);

  const createBattle = async () => {
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
        const data = await response.json();
        const errorMessage = data.detail || "Failed to create battle";
        setError(errorMessage);
        return;
      }

      const battleData: Battle = await response.json();
      setBattle(battleData);

      // Fetch both reviews
      const [res1, res2] = await Promise.all([
        apiFetch(`${FASTAPI_URL}/reviews/${battleData.review1Id}`),
        apiFetch(`${FASTAPI_URL}/reviews/${battleData.review2Id}`)
      ]);

      let r1: Review | null = null;
      let r2: Review | null = null;

      if (res1.ok) {
        r1 = await res1.json();
        setReview1(r1);
      }
      if (res2.ok) {
        r2 = await res2.json();
        setReview2(r2);
      }

      // Fetch movie names
      if (r1?.movieId) {
        const movieRes1 = await apiFetch(`${FASTAPI_URL}/movies/${r1.movieId}`);
        if (movieRes1.ok) {
          const movies = await movieRes1.json();
          if (movies.length > 0) {
            setMovie1({ id: movies[0].id, title: movies[0].title });
          }
        }
      }
      if (r2?.movieId) {
        const movieRes2 = await apiFetch(`${FASTAPI_URL}/movies/${r2.movieId}`);
        if (movieRes2.ok) {
          const movies = await movieRes2.json();
          if (movies.length > 0) {
            setMovie2({ id: movies[0].id, title: movies[0].title });
          }
        }
      }
    } catch (err) {
      setError("Network error. Please try again.");
    } finally {
      setLoading(false);
    }
  };

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
        const data = await response.json();
        const errorMessage = data.detail || "Failed to submit vote";
        setError(errorMessage);
        return;
      }

      const winner: Review = await response.json();
      setWinningReview(winner);

      // Fetch winner movie name
      if (winner.movieId) {
        const movieRes = await apiFetch(`${FASTAPI_URL}/movies/${winner.movieId}`);
        if (movieRes.ok) {
          const movies = await movieRes.json();
          if (movies.length > 0) {
            setWinnerMovie({ id: movies[0].id, title: movies[0].title });
          }
        }
      }
    } catch (err) {
      setError("Network error. Please try again.");
    } finally {
      setSubmitting(false);
    }
  };

  const handleNewBattle = () => {
    createBattle();
  };

  // Show loading state until mounted to avoid hydration mismatch
  if (!mounted || loading) {
    return (
      <div className="battles-page">
        <div className="battles-box">
          <h1>ReviewBattle</h1>
          <p>Loading battle...</p>
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
          <h2>🏆 Winner!</h2>
          <div className="winner-card">
            {winnerMovie && <p className="review-movie">Movie: {winnerMovie.title}</p>}
            <h3 className="review-title">{winningReview.reviewTitle}</h3>
            <p className="review-rating">Rating: {winningReview.rating}/10</p>
            <p className="review-body">{winningReview.reviewBody}</p>
            <p className="review-votes">Total Votes: {winningReview.votes}</p>
          </div>
          <button className="battle-button" onClick={handleNewBattle}>
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
