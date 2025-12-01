"use client";

import Image from "next/image";
import Link from "next/link";
import { use, useEffect, useMemo, useState } from "react";
import { apiFetch } from "@/lib/api";
import "./movie.css";

type Review = {
  id: number;
  movieId: string;
  authorId: number | string;
  rating: number;
  reviewTitle: string;
  reviewBody: string;
  votes: number;
  date: string;
  visible?: boolean;
};

type Movie = {
  id: string;
  title: string;
  description: string;
  duration: number;
  genre: string;
  release: string;
  rating?: number | null;
  reviews?: Review[];
  posterUrl?: string | null;
};

const FRIENDLY_NAMES = [
  "Alex Rivers",
  "Jordan Lee",
  "Taylor Morgan",
  "Casey Harper",
  "Sam Ellis",
  "Riley Brooks",
  "Quinn Parker",
  "Avery Chen",
  "Jamie Patel",
  "Morgan Blake",
];

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || "http://127.0.0.1:8000";

function friendlyAuthorName(authorId: number | string) {
  if (authorId === -1) return "Community";
  const str = String(authorId);
  let hash = 0;
  for (let i = 0; i < str.length; i += 1) {
    hash = (hash * 31 + str.charCodeAt(i)) >>> 0;
  }
  return FRIENDLY_NAMES[hash % FRIENDLY_NAMES.length];
}

export default function MovieByIdPage({ params }: { params: Promise<{ id: string }> }) {
  const resolved = use(params);
  const movieId = decodeURIComponent(resolved.id);

  const [movie, setMovie] = useState<Movie | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let mounted = true;

    const loadMovie = async () => {
      setLoading(true);
      setError(null);
      try {
        const movieResponse = await apiFetch(`${API_BASE}/movies/${movieId}`);
        const moviePayload = await movieResponse.json();
        if (!movieResponse.ok) {
          throw new Error(moviePayload?.detail || "Failed to load movie");
        }

        const movieData = Array.isArray(moviePayload) ? moviePayload[0] : null;
        if (!movieData) {
          throw new Error("Movie not found");
        }

        if (mounted) {
          setMovie(movieData);
        }
      } catch (err) {
        if (mounted) {
          setError(err instanceof Error ? err.message : "Could not load movie");
        }
      } finally {
        if (mounted) setLoading(false);
      }
    };

    loadMovie();
    return () => {
      mounted = false;
    };
  }, [movieId]);

  const visibleReviews = useMemo(
    () => (movie?.reviews || []).filter((r) => r.visible !== false),
    [movie]
  );

  const isLoading = loading || (!movie && !error);
  const isError = !!error || !movie;

  const releaseYear = movie ? new Date(movie.release).getFullYear() || "-" : "-";

  return (
    <div className="movie-page">
      <div className="movie-layout">
        {isLoading && (
          <div className="movie-detail-card loading">
            <div className="poster-skeleton" />
            <div className="content-skeleton">
              <div className="line short" />
              <div className="line medium" />
              <div className="line full" />
            </div>
          </div>
        )}

        {isError && !isLoading && (
          <div className="movie-detail-card error-card">
            <h1>Unable to load movie</h1>
            <p>{error || "Movie not found."}</p>
            <Link className="back-link" href="/movies">
              Back to movies
            </Link>
          </div>
        )}

        {!isLoading && !isError && movie && (
          <>
            <div className="movie-detail-card">
              <div className="poster">
                {movie.posterUrl ? (
                  <Image
                    src={movie.posterUrl}
                    alt={`${movie.title} poster`}
                    fill
                    className="poster-img"
                    sizes="240px"
                    priority
                  />
                ) : (
                  <div className="poster-fallback">Poster unavailable</div>
                )}
              </div>

              <div className="movie-content">
                <div className="chips">
                  <span className="chip chip-genre">{movie.genre}</span>
                  <span className="chip chip-muted">{releaseYear}</span>
                  <span className="chip chip-muted">{movie.duration} min</span>
                </div>
                <h1>{movie.title}</h1>
                <p className="movie-desc">{movie.description}</p>
                <div className="status-row" />
              </div>
            </div>

            <section className="reviews">
              <div className="reviews-header">
                <h2>Reviews</h2>
                <span className="muted">
                  {visibleReviews.length ? `${visibleReviews.length} comments` : "No comments yet"}
                </span>
              </div>

              {visibleReviews.length === 0 ? (
                <div className="empty-reviews">Be the first to review this movie.</div>
              ) : (
                <div className="reviews-list">
                  {visibleReviews.map((review) => {
                    const initials =
                      typeof review.authorId === "string"
                        ? review.authorId.slice(0, 2).toUpperCase()
                        : `U${review.authorId}`;
                    return (
                      <article key={review.id} className="review-card">
                        <div className="avatar">{initials}</div>
                        <div className="review-body">
                          <div className="review-head">
                            <div className="title-row">
                              <span className="review-title">{review.reviewTitle}</span>
                              <span className="muted">
                                {new Date(review.date).toLocaleDateString()}
                              </span>
                            </div>
                            <span className="chip chip-rating">* {review.rating.toFixed(1)}</span>
                          </div>
                          <p className="review-text">{review.reviewBody}</p>
                          <div className="review-meta">
                            <span>Helpful votes: {review.votes}</span>
                            <span>Author: {friendlyAuthorName(review.authorId)}</span>
                          </div>
                        </div>
                      </article>
                    );
                  })}
                </div>
              )}
            </section>
          </>
        )}
      </div>
    </div>
  );
}
