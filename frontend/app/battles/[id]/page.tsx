"use client";

import React, { useState, useEffect, useCallback } from 'react';
import '../battles.css';
import Link from 'next/link';
import { useRouter, useParams } from 'next/navigation';
import { useData } from '../../context';
import { apiFetch } from '../../../lib/api';

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

const BattleDetailPage = () => {
  const router = useRouter();
  const params = useParams();
  const battleId = params.id as string;
  const { accessToken } = useData();
  
  const [battle, setBattle] = useState<Battle | null>(null);
  const [review1, setReview1] = useState<Review | null>(null);
  const [review2, setReview2] = useState<Review | null>(null);
  const [movie1, setMovie1] = useState<Movie | null>(null);
  const [movie2, setMovie2] = useState<Movie | null>(null);
  const [winnerMovie, setWinnerMovie] = useState<Movie | null>(null);
  const [losingReview, setLosingReview] = useState<Review | null>(null);
  const [loserMovie, setLoserMovie] = useState<Movie | null>(null);
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
    } catch {
    }
    return null;
  };

  const fetchBattle = useCallback(async () => {
    setLoading(true);
    setError("");

    try {
      const response = await apiFetch(`${FASTAPI_URL}/battles/${battleId}`);

      if (!response.ok) {
        if (response.status === 401) {
          router.push('/login');
          return;
        }
        if (response.status === 404) {
          setError("Battle not found");
          return;
        }
        const data = await response.json();
        setError(data.detail || "Failed to load battle");
        return;
      }

      const battleData: Battle = await response.json();
      setBattle(battleData);

      if (battleData.winnerId) {
        const loserId = battleData.winnerId === battleData.review1Id 
          ? battleData.review2Id 
          : battleData.review1Id;

        const [winnerRes, loserRes] = await Promise.all([
          apiFetch(`${FASTAPI_URL}/reviews/${battleData.winnerId}`),
          apiFetch(`${FASTAPI_URL}/reviews/${loserId}`)
        ]);

        if (winnerRes.ok) {
          const winner: Review = await winnerRes.json();
          setWinningReview(winner);
          if (winner.movieId) {
            const movie = await fetchMovie(winner.movieId);
            setWinnerMovie(movie);
          }
        }

        if (loserRes.ok) {
          const loser: Review = await loserRes.json();
          setLosingReview(loser);
          if (loser.movieId) {
            const movie = await fetchMovie(loser.movieId);
            setLoserMovie(movie);
          }
        }
      } else {
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
      }
    } catch (err) {
      console.error("Failed to fetch battle:", err);
      setError("Network error. Please try again.");
    } finally {
      setLoading(false);
    }
  }, [battleId, router]);

  useEffect(() => {
    if (!mounted) return;
    
    if (!accessToken) {
      router.push('/login');
      return;
    }
    
    if (battleId) {
      fetchBattle();
    }
  }, [mounted, accessToken, battleId, router, fetchBattle]);

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
        setError(data.detail || "Failed to submit vote");
        return;
      }

      const winner: Review = await response.json();
      setWinningReview(winner);

      if (winner.movieId) {
        const movie = await fetchMovie(winner.movieId);
        setWinnerMovie(movie);
      }

      const loser = review1?.id === winner.id ? review2 : review1;
      const loserMov = review1?.id === winner.id ? movie2 : movie1;
      setLosingReview(loser);
      setLoserMovie(loserMov);
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
          <h2>Loading Battle...</h2>
          <div className="battle-reviews-container">
            <div className="battle-review-card skeleton">
              <div className="skeleton-line skeleton-title"></div>
              <div className="skeleton-line skeleton-subtitle"></div>
              <div className="skeleton-line"></div>
              <div className="skeleton-line"></div>
              <div className="skeleton-line skeleton-short"></div>
            </div>
            <div className="vs-divider">VS</div>
            <div className="battle-review-card skeleton">
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

  if (error) {
    return (
      <div className="battles-page">
        <div className="battles-box">
          <h1>ReviewBattle</h1>
          <div className="error-container">
            <p className="error-message">Error: {error}</p>
          </div>
          <Link href="/battles" className="battle-button">Start New Battle</Link>
          <Link href="/" className="home-link">Back to Home</Link>
        </div>
      </div>
    );
  }

  if (winningReview) {
    return (
      <div className="battles-page">
        <div className="battles-box result-box">
          <h1>ReviewBattle</h1>
          
          <h2 className="result-label winner-label">Winner</h2>
          <Link href={`/reviews/${winningReview.id}`} className="result-card winner-card">
            {winnerMovie && <p className="review-movie">{winnerMovie.title}</p>}
            <h3 className="battle-review-title">{winningReview.reviewTitle}</h3>
            <p className="review-rating">Rating: {winningReview.rating}/10</p>
            <p className="battle-review-body">{winningReview.reviewBody}</p>
            <p className="battle-review-votes">Total Votes: {winningReview.votes}</p>
            <span className="card-link-hint">View full review →</span>
          </Link>

          {losingReview && (
            <>
              <h2 className="result-label loser-label">Loser</h2>
              <Link href={`/reviews/${losingReview.id}`} className="result-card loser-card">
                {loserMovie && <p className="review-movie">{loserMovie.title}</p>}
                <h3 className="battle-review-title">{losingReview.reviewTitle}</h3>
                <span className="card-link-hint">View full review →</span>
              </Link>
            </>
          )}

          <Link href="/battles" className="battle-button">New Battle</Link>
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
            <div className="battle-reviews-container">
              <div 
                className={`battle-review-card ${selectedReviewId === review1.id ? 'selected' : ''}`}
                onClick={() => setSelectedReviewId(review1.id)}
                onKeyDown={handleKeyDown(review1.id)}
                tabIndex={0}
                role="button"
                aria-pressed={selectedReviewId === review1.id}
                aria-label={`Select review: ${review1.reviewTitle}`}
              >
                {movie1 && <p className="review-movie">{movie1.title}</p>}
                <h3 className="battle-review-title">{review1.reviewTitle}</h3>
                <p className="review-rating">Rating: {review1.rating}/10</p>
                <p className="battle-review-body">{review1.reviewBody}</p>
              </div>
              
              <div className="vs-divider">VS</div>
              
              <div 
                className={`battle-review-card ${selectedReviewId === review2.id ? 'selected' : ''}`}
                onClick={() => setSelectedReviewId(review2.id)}
                onKeyDown={handleKeyDown(review2.id)}
                tabIndex={0}
                role="button"
                aria-pressed={selectedReviewId === review2.id}
                aria-label={`Select review: ${review2.reviewTitle}`}
              >
                {movie2 && <p className="review-movie">{movie2.title}</p>}
                <h3 className="battle-review-title">{review2.reviewTitle}</h3>
                <p className="review-rating">Rating: {review2.rating}/10</p>
                <p className="battle-review-body">{review2.reviewBody}</p>
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

export default BattleDetailPage;
