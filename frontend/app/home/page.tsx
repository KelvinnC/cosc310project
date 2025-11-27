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
        )}
    </div>
  )
}

export default page
