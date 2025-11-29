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
        <Link href="/"><ul>Home</ul></Link>
        <Link href="/movies"><ul>Movies</ul></Link>
        <Link href="/reviews"><ul>Reviews</ul></Link>
        <Link href="/battles"><ul>Battles</ul></Link>
        {role && role === 'admin' && <Link href="/admin"><ul>Admin</ul></Link>}
        {accessToken && <Link href="/logout"><ul>Logout</ul></Link>}
        {!accessToken && <Link href="/login"><ul>Login</ul></Link>}
        {!accessToken && <Link href="/register"><ul>Register</ul></Link>}
      </nav>
    </div>
  )
}

export default Navbar
