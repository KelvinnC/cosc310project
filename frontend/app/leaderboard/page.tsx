"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { apiFetch } from "@/lib/api";
import "./leaderboard.css";

type Review = {
  id: number;
  movieId: string;
  authorId: number | string;
  rating: number;
  reviewTitle: string;
  reviewBody: string;
  votes: number;
  date: string;
};

type MovieSummary = {
  id: string;
  title: string;
};

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || "http://127.0.0.1:8000";

export default function LeaderboardPage() {
  const [reviews, setReviews] = useState<Review[]>([]);
  const [movies, setMovies] = useState<MovieSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let mounted = true;
    const loadData = async () => {
      setLoading(true);
      setError(null);
      try {
        const [reviewRes, moviesRes] = await Promise.all([
          apiFetch(`${API_BASE}/leaderboard?limit=15`),
          apiFetch(`${API_BASE}/movies`),
        ]);

        const [reviewPayload, moviesPayload] = await Promise.all([
          reviewRes.json(),
          moviesRes.json(),
        ]);

        if (!reviewRes.ok) {
          throw new Error(reviewPayload?.detail || "Failed to load leaderboard");
        }
        if (!moviesRes.ok) {
          throw new Error(moviesPayload?.detail || "Failed to load movies");
        }

        if (mounted) {
          setReviews(Array.isArray(reviewPayload) ? reviewPayload : []);
          setMovies(
            Array.isArray(moviesPayload)
              ? moviesPayload.map((m: any) => ({ id: m.id, title: m.title }))
              : []
          );
        }
      } catch (err) {
        if (mounted) {
          setError(err instanceof Error ? err.message : "Could not load leaderboard");
        }
      } finally {
        if (mounted) setLoading(false);
      }
    };

    loadData();
    return () => {
      mounted = false;
    };
  }, []);

  const movieNameById = useMemo(() => {
    const map = new Map<string, string>();
    movies.forEach((m) => map.set(m.id, m.title));
    return map;
  }, [movies]);

  return (
    <div className="leaderboard-page">
      <div className="leaderboard-shell">
        <section className="leaderboard-hero">
          <h1>Top reviewers</h1>
          <p>Best and funniest reviews ranked by votes</p>
        </section>

        {loading ? (
          <div className="loading-card" />
        ) : error ? (
          <div className="error-box">{error}</div>
        ) : (
          <div className="board-card">
            <div className="board-header">
              <h2>Leaderboard</h2>
              <span className="muted">Sorted by votes, then recency</span>
            </div>

            {reviews.length === 0 ? (
              <div className="empty">No reviews have been ranked yet.</div>
            ) : (
              <div className="leaderboard-list">
                {reviews.map((review, idx) => (
                  <div key={review.id} className="entry">
                    <div className="rank-badge">#{idx + 1}</div>
                    <div className="entry-main">
                      <div className="entry-title">
                        <Link href={`/reviews/${review.id}`}>
                          {review.reviewTitle}
                        </Link>
                      </div>
                      <div className="entry-meta">
                        <span className="pill">★ {review.rating.toFixed(1)}</span>
                        <span className="pill">Movie: {movieNameById.get(review.movieId) || "Unknown"}</span>
                        <span className="pill">By {String(review.authorId)}</span>
                        <span className="pill">{new Date(review.date).toLocaleDateString()}</span>
                      </div>
                      {}
                    </div>
                    <div className="entry-votes">
                      <div className="score">{review.votes ?? 0}</div>
                      <div className="label">Funny votes</div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
