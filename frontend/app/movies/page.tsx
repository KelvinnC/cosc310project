"use client";

import Link from "next/link";
import { FormEvent, useState } from "react";
import { apiFetch } from "@/lib/api";
import "./movies.css";

type MovieSummary = {
  id: string;
  title: string;
};

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || "http://127.0.0.1:8000";

export default function MoviesIndexPage() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<MovieSummary[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleSearch = async (evt?: FormEvent) => {
    if (evt) {
      evt.preventDefault();
    }
    const term = query.trim();
    if (!term) {
      setResults([]);
      setError(null);
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await apiFetch(`${API_BASE}/movies/search?title=${encodeURIComponent(term)}`);
      const payload = await response.json();
      if (!response.ok) {
        throw new Error(payload?.detail || "Search failed");
      }
      const list: MovieSummary[] = Array.isArray(payload)
        ? payload.filter((m) => m?.id && m?.title)
        : [];
      setResults(list);
    } catch (err) {
      setResults([]);
      setError(err instanceof Error ? err.message : "Search failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="movies-page">
      <section className="movies-hero">
        <div className="hero-content">
          <p className="eyebrow">Discover</p>
          <h1>Find a movie by name</h1>
          <p className="lede">
            Search the library and jump straight to a film&apos;s page at <code>/movies/&lt;id&gt;</code>.
          </p>
          <form className="search-form" onSubmit={handleSearch}>
            <input
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Type a movie title..."
              aria-label="Search movies by title"
            />
            <button type="submit" disabled={loading}>
              {loading ? "Searching..." : "Search"}
            </button>
          </form>
          {error && <p className="error">{error}</p>}
        </div>
      </section>

      <section className="movies-results">
        {results.length === 0 && !error && !loading ? (
          <div className="empty">
            <p>Start searching to see results.</p>
          </div>
        ) : (
          <div className="grid">
            {results.map((movie) => (
              <Link key={movie.id} href={`/movies/${movie.id}`} className="movie-tile">
                <span className="movie-title">{movie.title}</span>
                <span className="movie-id">{movie.id}</span>
              </Link>
            ))}
          </div>
        )}
      </section>
    </div>
  );
}
