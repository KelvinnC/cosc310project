"use client"

import React, { useState } from 'react'
import {useEffect} from 'react'
import { apiFetch } from '@/lib/api'
import './home.css'

const FASTAPI_URL = "http://127.0.0.1:8000"

const page = () => {
    const [userData, setUserData] = useState(null)
    const [battles, setBattles] = useState([])
    const [reviews, setReviews] = useState([])
    const [user, setUser] = useState(null)

    useEffect(() => {
        const fetchUserData = async () => {
            const response = await apiFetch(`${FASTAPI_URL}/home`)
            const data = await response.json()
            console.log(data)
            setUserData(data)
            setBattles(data["battles"])
            setReviews(data["reviews"])
            setUser(data["user"])
        }
        fetchUserData();
    }, [])

  return (
    <div className="user-dashboard">
        {userData && (
            <div>
                {user &&
                <div className="user-div">
                    <div className="user-container">
                        <h1 className="review-container-title">Hi {user["username"]}</h1>
                        <span>You've posted {reviews.length} reviews and participated in {battles.length} battles</span>
                        <span>Role: {user["role"]}</span>
                        <span>Warnings: {user['warnings']}</span>
                        <span>Account created on {user["created_at"]}</span>
                    </div>
                </div>
                }
                <div>
                    <h1 className="review-container-title">Your Reviews</h1>
                    <div className="review-container">
                        {reviews.map((review, idx) => (
                            <div key={idx} className="review">
                                <h2 className="review-title">{review["reviewTitle"]}</h2>
                                <span>Posted on {review["date"]}</span>
                                <span>Rating {review["rating"]} / 5</span>
                                <span className="review-body">{review["reviewBody"]}</span>
                                <span className="review-votes">{review["votes"]} votes</span>
                            </div>
                        ))}
                    </div>
                </div>
                <div>
                    <h1 className="review-container-title">Your Battles</h1>
                    <div className="review-container">
                        {battles.map((battle, idx) => (
                            <div key={idx} className="review">
                            </div>
                        ))}
                    </div>
                </div>
            </div>
        )}
    </div>
  )
}

export default page
