"use client";

import Image from "next/image";
import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import { useParams } from "next/navigation";
import { apiFetch } from "@/lib/api";
import { friendlyAuthorName, getInitials } from "@/lib/utils";
import "./movie.css";

// --- Types ---

export type Review = {
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

export type Movie = {
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

// --- Constants ---

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || "http://127.0.0.1:8000";

// --- Hooks ---

function useMovie(movieId: string | null) {
  const [movie, setMovie] = useState<Movie | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!movieId) return;

    const controller = new AbortController();

    const loadMovie = async () => {
      setLoading(true);
      setError(null);
      try {
        const movieResponse = await apiFetch(`${API_BASE}/movies/${movieId}`, {
          signal: controller.signal,
        } as RequestInit);
        const moviePayload = await movieResponse.json();
        
        if (!movieResponse.ok) {
          throw new Error(moviePayload?.detail || "Failed to load movie");
        }

        // Handle case where API returns an array or a single object
        const movieData = Array.isArray(moviePayload) ? moviePayload[0] : null;
        if (!movieData) {
          throw new Error("Movie not found");
        }

        setMovie(movieData);
      } catch (err) {
        if (controller.signal.aborted) return;
        setError(err instanceof Error ? err.message : "Could not load movie");
      } finally {
        if (!controller.signal.aborted) setLoading(false);
      }
    };

    loadMovie();
    return () => controller.abort();
  }, [movieId]);

  return { movie, loading, error };
}

// --- Components ---

const MovieSkeleton = () => (
  <div className="movie-detail-card loading">
    <div className="poster-skeleton" />
    <div className="content-skeleton">
      <div className="line short" />
      <div className="line medium" />
      <div className="line full" />
    </div>
  </div>
);

const ErrorView = ({ error }: { error: string }) => (
  <div className="movie-detail-card error-card">
    <h1>Unable to load movie</h1>
    <p>{error}</p>
    <Link className="back-link" href="/movies">
      Back to movies
    </Link>
  </div>
);

const MovieHeader = ({ movie }: { movie: Movie }) => {
  const releaseYear = new Date(movie.release).getFullYear() || "-";

  return (
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
  );
};

const ReviewCard = ({ review }: { review: Review }) => {
  const initials = typeof review.authorId === "string" 
    ? getInitials(review.authorId) 
    : `U${review.authorId}`;
    
  return (
    <article className="review-card">
      <div className="avatar">{initials}</div>
      <div className="review-body">
        <div className="review-head">
          <div className="title-row">
            <Link href={`/reviews/${review.id}`} className="review-title">
              {review.reviewTitle}
            </Link>
            <span className="muted">
              {new Date(review.date).toLocaleDateString()}
            </span>
          </div>
          <span className="chip chip-rating">* {review.rating.toFixed(1)}</span>
        </div>
        <Link href={`/reviews/${review.id}`} className="review-text">
          {review.reviewBody}
        </Link>
        <div className="review-meta">
          <span>Helpful votes: {review.votes}</span>
          <span>Author: {friendlyAuthorName(review.authorId)}</span>
        </div>
      </div>
    </article>
  );
};

const ReviewsSection = ({ reviews }: { reviews: Review[] }) => {
  const visibleReviews = useMemo(
    () => reviews.filter((r) => r.visible !== false),
    [reviews]
  );

  return (
    <section className="reviews">
      <div className="reviews-header">
        <h2>Reviews</h2>
        <span className="muted">
          {visibleReviews.length ? `${visibleReviews.length} reviews` : "No reviews yet"}
        </span>
      </div>

      {visibleReviews.length === 0 ? (
        <div className="empty-reviews">Be the first to review this movie.</div>
      ) : (
        <div className="reviews-list">
          {visibleReviews.map((review) => (
            <ReviewCard key={review.id} review={review} />
          ))}
        </div>
      )}
    </section>
  );
};

// --- Main Page Component ---

export default function MovieByIdPage() {
  const params = useParams<{ id: string }>();
  const movieId = decodeURIComponent(params.id);
  
  const { movie, loading, error } = useMovie(movieId);

  const isLoading = loading || (!movie && !error);
  const isError = !!error || !movie;

  return (
    <div className="movie-page">
      <div className="movie-layout">
        {isLoading && <MovieSkeleton />}
        
        {isError && !isLoading && <ErrorView error={error || "Movie not found."} />}

        {!isLoading && !isError && movie && (
          <>
            <MovieHeader movie={movie} />
            <ReviewsSection reviews={movie.reviews || []} />
          </>
        )}
      </div>
    </div>
  );
}
