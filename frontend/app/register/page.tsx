"use client";

import React from 'react'
import './register.css'
import Link from 'next/link';

const page = () => {
  return (
    <div className="register-page">
      <form className="register-box"
      onSubmit={(e) => e.preventDefault()}>
        <h1>ReviewBattle</h1>
        <h2>Register</h2>
        <input type="text" placeholder="username" className="register-textbox"></input>
        <input type="text" placeholder="password" className="register-textbox"></input>
        <button className="register-button" type="submit">Register</button>
        <p>Already have an account? <Link className="sign-in-link" href="/login">Sign in</Link> instead</p>
      </form>
    </div>
  )
}

export default page
