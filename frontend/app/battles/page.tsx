"use client";

import React, { useState, useEffect } from 'react';
import './battles.css';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useData } from '../context';
import { apiFetch } from '../../lib/api';

const FASTAPI_URL = "http://127.0.0.1:8000";

interface Battle {
  id: string;
}

const BattlesPage = () => {
  const router = useRouter();
  const { accessToken } = useData();
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  useEffect(() => {
    if (!mounted) return;
    
    if (!accessToken) {
      router.push('/login');
      return;
    }

    const createBattle = async () => {
      setLoading(true);
      setError("");

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
          setError(data.detail || "Failed to create battle");
          setLoading(false);
          return;
        }

        const battleData: Battle = await response.json();
        router.push(`/battles/${battleData.id}`);
      } catch (err) {
        console.error("Failed to create battle:", err);
        setError("Network error. Please try again.");
        setLoading(false);
      }
    };

    createBattle();
  }, [mounted, accessToken, router]);

  if (!mounted || loading) {
    return (
      <div className="battles-page">
        <div className="battles-box">
          <h1>ReviewBattle</h1>
          <h2>Creating Battle...</h2>
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
          <button className="battle-button" onClick={() => window.location.reload()}>
            Try Again
          </button>
          <Link href="/" className="home-link">Back to Home</Link>
        </div>
      </div>
    );
  }

  return null;
};

export default BattlesPage;
