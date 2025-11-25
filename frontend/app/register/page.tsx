"use client";

import React from 'react'
import './register.css'
import Link from 'next/link';
import { useState } from 'react';
import {redirect} from "next/navigation"

const FASTAPI_URL = "http://127.0.0.1:8000"

const page = () => {
  const [username, setUsername] = useState("")
  const [password, setPassword] = useState("")
  const [error, setError] = useState("")

  const submitRegistration = async () => {
    const response = await fetch(`${FASTAPI_URL}/users`, {
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
      let err_msg = `${response.status}: ${response.statusText}`
      setError(err_msg)
      return
    }
    redirect('/')
  }

  return (
    <div className="register-page">
      {error && (
        <div>
          <p style={{color: "red", fontSize: "16px"}}>Error {error}</p>
        </div>
      )}
      <form className="register-box"
      onSubmit={(e) => e.preventDefault()}>
        <h1>ReviewBattle</h1>
        <h2>Register</h2>
        <input type="text" 
        placeholder={username ? username : "username"} 
        onChange={(e) => setUsername(e.target.value)}
        className="register-textbox"></input>
        <input type="password" 
        placeholder={password ? password : "password"}
        onChange={(e) => setPassword(e.target.value)}
        className="register-textbox"></input>
        <button className="register-button" 
        type="submit"
        onClick={(e) => submitRegistration()}>Register</button>
        <p>Already have an account? <Link className="sign-in-link" href="/login">Sign in</Link> instead</p>
      </form>
    </div>
  )
}

export default page
