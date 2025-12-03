"use client"

import React from 'react'
import './Navbar.css'
import { useData } from '../context'
import Link from 'next/link'

const Navbar = () => {
    const {accessToken, role} = useData()
  return (
    <div className="navbar">
      <nav>
          <Link href="/"><span>Home</span></Link>
          <Link href="/movies"><span>Movies</span></Link>
          <Link href="/reviews"><span>Reviews</span></Link>
          <Link href="/battles"><span>Battles</span></Link>
          <Link href="/watchlist"><span>Watchlist</span></Link>
          {role && role === 'admin' && <Link href="/admin"><span>Admin</span></Link>}
          {accessToken && <Link href="/logout"><span>Logout</span></Link>}
          {!accessToken && <Link href="/login"><span>Login</span></Link>}
          {!accessToken && <Link href="/register"><span>Register</span></Link>}
      </nav>
    </div>
  )
}

export default Navbar
