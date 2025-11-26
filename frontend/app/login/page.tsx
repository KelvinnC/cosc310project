"use client";

import React from 'react'
import './login.css'
import Link from 'next/link';
import { useState } from 'react';
import { useRouter } from 'next/navigation';

const FASTAPI_URL = "http://127.0.0.1:8000"

const Page = () => {
  const router = useRouter();
  const [username, setUsername] = useState("")
  const [password, setPassword] = useState("")
  const [error, setError] = useState("")
  const [loading, setLoading] = useState(false)

  const validateForm = () => {
    if (!username.trim()) {
      setError("Username is required")
      return false
    }
    if (username.trim().length < 3) {
      setError("Username must be at least 3 characters")
      return false
    }
    if (!password) {
      setError("Password is required")
      return false
    }
    if (password.length < 6) {
      setError("Password must be at least 6 characters")
      return false
    }
    setError("")
    return true
  }

  const submitLogin = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!validateForm()) {
      return
    }

    setLoading(true)
    setError("")

    try {
      const response = await fetch(`${FASTAPI_URL}/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          username,
          password
        })
      })
      const data = await response.json()
      if (!response.ok) {
        const errorMessage = data.detail || data.message || response.statusText || "Registration failed"
        setError(errorMessage)
        return
      }
      router.push('/')
    } catch (err) {
      setError("Network error. Please try again.")
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="login-page">
      {error && (
        <div className="error-container">
          <p className="error-message">Error: {error}</p>
        </div>
      )}
      <form className="login-box"
      onSubmit={submitLogin}>
        <h1>ReviewBattle</h1>
        <h2>Login</h2>
        <div className="form-group">
          <label htmlFor="username">Username</label>
          <input 
            id="username"
            type="text" 
            placeholder="Enter username" 
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            className="login-textbox"
            disabled={loading}
            required
          />
        </div>
        <div className="form-group">
          <label htmlFor="password">Password</label>
          <input 
            id="password"
            type="password" 
            placeholder="Enter password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="login-textbox"
            disabled={loading}
            required
          />
        </div>
        <button 
          className="login-button" 
          type="submit"
          disabled={loading}
        >
          {loading ? "Logging in..." : "Login"}
        </button>
        <p>No account? <Link className="register-link" href="/register">Register</Link> instead</p>
      </form>
    </div>
  )
}

export default Page