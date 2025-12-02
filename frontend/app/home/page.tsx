"use client"

import React, { useState } from 'react'
import {useEffect} from 'react'
import { apiFetch } from '@/lib/api'
import { collapseWhitespace } from '@/lib/utils'
import './home.css'
import Link from 'next/link'
import { useRouter } from 'next/navigation'

const FASTAPI_URL = "http://127.0.0.1:8000"

const page = () => {
    const [userData, setUserData] = useState(null)
    const [battles, setBattles] = useState([])
    const [reviews, setReviews] = useState([])
    const [user, setUser] = useState(null)
    const [badges, setBadges] = useState([])
    const router = useRouter()

    useEffect(() => {
        const fetchUserData = async () => {
            const response = await apiFetch(`${FASTAPI_URL}/home`)
            if (response.status == 401) {
                router.push('/login')
                return
            }
            const data = await response.json()
            setUserData(data)
            setBattles(data["battles"])
            setReviews(data["reviews"])
            setUser(data["user"])
            setBadges(data["badges"] || [])
        }
        fetchUserData();
    }, [])

    const downloadData = async () => {
        const response = await apiFetch(`${FASTAPI_URL}/home/download`, {
            method: "GET"
        }
        )
        if (!response.ok) {
            console.log("Error: could not download data")
        }

        const blob = await response.blob()
        const url = window.URL.createObjectURL(blob)
        const a = document.createElement("a")
        a.href = url
        a.download = "dashboard.json"
        document.body.appendChild(a)
        a.click()
        a.remove()
        window.URL.revokeObjectURL(url)
    }

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
                        <span>Account created on {(user["created_at"] as string).split("T")[0]}</span>
                        {badges.length > 0 &&
                        <div className="badge-row">
                            {badges.map((badge, idx) => (
                                <span
                                  key={idx}
                                  className={`badge-pill ${badge["medalColor"] || ""}`}
                                  title={badge["description"] || ""}
                                >
                                  {badge["title"]}
                                </span>
                            ))}
                        </div>
                        }
                        <button type="submit" 
                        className="download-button"
                        onClick={downloadData}>Download my Data</button>
                    </div>
                </div>
                }
                <div>
                    <h1 className="review-container-title">Your Reviews</h1>
                    <div className="review-container">
                        {reviews.map((review, idx) => (
                            <div key={idx}>
                                <Link href={`/reviews/${review["id"]}`}>
                                <div className="review">
                                    <h2 className="review-title">{review["reviewTitle"]}</h2>
                                    <span>Posted on {review["date"]}</span>
                                    <span>Rating {review["rating"]} / 5</span>
                                    <span className="review-body">{collapseWhitespace(review["reviewBody"])}</span>
                                    <span className="review-votes">{review["votes"]} votes</span>
                                </div>
                                </Link>
                            </div>
                        ))}
                    </div>
                </div>
                <div>
                    <h1 className="review-container-title">Your Battles</h1>
                    <div className="review-container">
                        {battles.map((battle, idx) => (
                            <div key={idx}>
                                <Link href={`/battles/${battle["id"]}`}>
                                <div className="battle">
                                    <span>Battle {battle["id"]}</span>
                                    <span>
                                      Date: {battle["endedAt"] ? (battle["endedAt"] as string).split("T")[0] : "In progress"}
                                    </span>
                                    <span>Review {battle["review1Id"]} vs. {battle["review2Id"]}</span>
                                    <span className="winner-text">Winner: {battle["winnerId"]}</span>
                                    <span className="click-text">See battle →</span>
                                </div>
                                </Link>
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
