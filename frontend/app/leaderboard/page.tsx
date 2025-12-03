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

type Achievement = {
  category: "most_reviews" | "most_votes" | "most_battles";
  userId: string;
  username: string;
  value: number;
  label: string;
  position: number;
  medalColor?: string;
  tieBreakDate?: string;
};

type MovieSummary = {
  id: string;
  title: string;
};

type TopMovie = {
  id: string;
  title: string;
  rating: number;
  release: string;
  posterUrl?: string;
};

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || "http://127.0.0.1:8000";

export default function LeaderboardPage() {
  const [reviews, setReviews] = useState<Review[]>([]);
  const [movies, setMovies] = useState<MovieSummary[]>([]);
  const [achievements, setAchievements] = useState<Achievement[]>([]);
  const [topMovies, setTopMovies] = useState<TopMovie[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let mounted = true;
    const loadData = async () => {
      setLoading(true);
      setError(null);
      try {
        const [reviewRes, moviesRes, achievementsRes, topMoviesRes] = await Promise.all([
          apiFetch(`${API_BASE}/leaderboard?limit=15`),
          apiFetch(`${API_BASE}/movies`),
          apiFetch(`${API_BASE}/achievements`),
          apiFetch(`${API_BASE}/movies?sort_by=rating&order=desc`),
        ]);

        const [reviewPayload, moviesPayload, achievementsPayload, topMoviesPayload] = await Promise.all([
          reviewRes.json(),
          moviesRes.json(),
          achievementsRes.json(),
          topMoviesRes.json(),
        ]);

        if (!reviewRes.ok) throw new Error(reviewPayload?.detail || "Failed to load leaderboard");
        if (!moviesRes.ok) throw new Error(moviesPayload?.detail || "Failed to load movies");
        if (!achievementsRes.ok) throw new Error(achievementsPayload?.detail || "Failed to load achievements");
        if (!topMoviesRes.ok) throw new Error(topMoviesPayload?.detail || "Failed to load top movies");

        if (mounted) {
          setReviews(Array.isArray(reviewPayload) ? reviewPayload : []);
          setMovies(
            Array.isArray(moviesPayload)
              ? moviesPayload.map((m: any) => ({ id: m.id, title: m.title }))
              : []
          );
          setAchievements(Array.isArray(achievementsPayload) ? achievementsPayload : []);
          setTopMovies(
            Array.isArray(topMoviesPayload)
              ? topMoviesPayload.slice(0, 10).map((m: any) => ({
                  id: m.id,
                  title: m.title,
                  rating: m.rating ?? 0,
                  release: m.release,
                  posterUrl: m.posterUrl,
                }))
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
          <h1>Leaderboard</h1>
          <p>The Best of the Best</p>
        </section>

        {loading ? (
          <div className="loading-card" />
        ) : error ? (
          <div className="error-box">{error}</div>
        ) : (
          <>
            <div className="leaderboard-grid-container">
              <div className="board-card">
                <div className="board-header">
                  <h2>Top Reviews</h2>
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
                            <span className="pill">Author: {String(review.authorId)}</span>
                            <span className="pill">{new Date(review.date).toLocaleDateString()}</span>
                          </div>
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

              <div className="board-card">
                <div className="board-header">
                  <h2>Top movies</h2>
                  <span className="muted">Aggregated from all reviews</span>
                </div>
                {topMovies.length === 0 ? (
                  <div className="empty">No movies have been rated yet.</div>
                ) : (
                  <div className="leaderboard-list">
                    {topMovies.map((movie, idx) => (
                      <div key={movie.id} className="entry">
                        <div className="rank-badge">#{idx + 1}</div>
                        <div className="entry-main">
                                                  <div className="entry-title">
                                                    <Link href={`/movies/${movie.id}`}>
                                                      {movie.title}
                                                    </Link>
                                                  </div>                          <div className="entry-meta">
                            <span className="pill">Avg Rating: ★ {movie.rating.toFixed(1)}</span>
                            {movie.release && (
                              <span className="pill">Released: {new Date(movie.release).getFullYear()}</span>
                            )}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>

            <div className="achievements-section">
              <div className="board-card achievements-card">
                <div className="board-header">
                  <h2>Top users</h2>
                  <span className="muted">Category leaders earn dashboard badges</span>
                </div>
                {achievements.length === 0 ? (
                  <div className="empty">No achievements yet.</div>
                ) : (
                  <div className="achievements-grid">
                    {achievements.map((ach) => {
                      const unit =
                        ach.category === "most_reviews"
                          ? "reviews"
                          : ach.category === "most_votes"
                          ? "votes"
                          : "battles";
                      return (
                        <div key={`${ach.category}-${ach.position}`} className="achievement">
                          <div className={`medal ${ach.medalColor || ""}`}>#{ach.position}</div>
                          <div className="achievement-body">
                            <div className="title">{ach.label}</div>
                            <div className="winner">{ach.username}</div>
                            <div className="value">
                              {ach.value.toLocaleString()} {unit}
                            </div>
                            {ach.tieBreakDate && (
                              <div className="muted">
                                Last activity {new Date(ach.tieBreakDate).toLocaleDateString()}
                              </div>
                            )}
                          </div>
                        </div>
                      );
                    })}
                  </div>
                )}
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
