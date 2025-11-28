"use client"

import React, { useState } from 'react'
import {useEffect} from 'react'
import { apiFetch } from '@/lib/api'
import './admin.css'
import Link from 'next/link'
import { useRouter } from 'next/navigation'

const FASTAPI_URL = "http://127.0.0.1:8000"

const page = () => {
    const [adminData, setAdminData] = useState(null)
    const [totalUsers, setTotalUsers] = useState(0)
    const [warnedUsers, setWarnedUsers] = useState<any[]>([])
    const [bannedUsers, setBannedUsers] = useState<any[]>([])
    const [flaggedReviews, setFlaggedReviews] = useState<any[]>([])
    const router = useRouter()

    
    const warnUser = async (user_id: string) => {
        const response = await apiFetch(`${FASTAPI_URL}/users/${user_id}/warn`, {
            method: 'PATCH'
        })
        if (!response.ok) {
            console.log("Error warning user")
        }
    }

    const hideReview = async (review_id: string) => {
        const response = await apiFetch(`${FASTAPI_URL}/reviews/${review_id}/hide`, {
            method: 'PATCH'
        })
        if (!response.ok) {
            console.log("Error hiding review")
        }
    }

    const clearReviewFlags = async (review_id: string) => {
        const response = await apiFetch(`${FASTAPI_URL}/reviews/${review_id}/unflag`, {
            method: 'PATCH'
        })
        if (!response.ok) {
            console.log("Error unflagging review")
        }
    }

    const unwarnUser = async (user_id: string) => {
        const response = await apiFetch(`${FASTAPI_URL}/users/${user_id}/unwarn`, {
            method: 'PATCH'
        })
        if (!response.ok) {
            console.log("Error unwarning user")
        }
    }

    const toggleBan = async (user_id: string, user_active: boolean) => {
        const action = user_active ? "ban" : "unban"
        const response = await apiFetch(`${FASTAPI_URL}/users/${user_id}/${action}`, {
            method: 'PATCH'
        })
        if (!response.ok) {
            console.log("Error banning user")
        }
    }

    useEffect(() => {
        const fetchAdminData = async () => {
            const response = await apiFetch(`${FASTAPI_URL}/admin`)
            if (response.status == 401) {
                router.push('/login')
                return
            }
            const data = await response.json()
            setAdminData(data)
            setTotalUsers(data["total_users"])
            setWarnedUsers(data["warned_users"].filter((user: any) => user["active"]))
            setBannedUsers(data["banned_users"])
            setFlaggedReviews(data["flagged_reviews"])
            console.log(data)
        }
        fetchAdminData();
    }, [warnUser, unwarnUser, toggleBan])

  return (
    <div className="user-dashboard">
        {adminData && (
            <div>
                <div>
                    <h2 className="review-container-title">Total Users: {totalUsers}</h2>
                </div>
                <div>
                    <h1 className="review-container-title">Warned Users</h1>
                    <div className="review-container">
                        {warnedUsers.map((warnedUser, idx) => (
                            <div key={idx}>
                                <div className="review">
                                    <h2 className="review-title">{warnedUser["username"]}</h2>
                                    <span>Created on {(warnedUser["created_at"] as string).split("T")[0]}</span>
                                    <span>Role: {warnedUser["role"]}</span>
                                    <span>Warnings: {warnedUser["warnings"]}</span>
                                    <span>User is {warnedUser["active"] ? "active" : "banned"}</span>
                                    <div className="admin-actions-container">
                                        <button onClick={(e) => warnUser(warnedUser["id"])}>Warn</button>
                                        <button onClick={(e) => unwarnUser(warnedUser["id"])}>Unwarn</button>
                                        <button onClick={(e) => toggleBan(warnedUser["id"], warnedUser["active"])}>{warnedUser["active"] ? "Ban" : "Unban"}</button>
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
                <div>
                    <h1 className="review-container-title">Banned Users</h1>
                    <div className="review-container">
                        {bannedUsers.map((bannedUser, idx) => (
                            <div key={idx}>
                                <div className="review">
                                    <h2 className="review-title">{bannedUser["username"]}</h2>
                                    <span>Created on {(bannedUser["created_at"] as string).split("T")[0]}</span>
                                    <span>Role: {bannedUser["role"]}</span>
                                    <span>Warnings: {bannedUser["warnings"]}</span>
                                    <span>User is {bannedUser["active"] ? "active" : "banned"}</span>
                                    <div className="admin-actions-container">
                                        <button onClick={(e) => toggleBan(bannedUser["id"], bannedUser["active"])}>{bannedUser["active"] ? "Ban" : "Unban"}</button>
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
                <div>
                    <h1 className="review-container-title">Flagged Reviews</h1>
                    <div className="review-container">
                        {flaggedReviews.map((flaggedReview, idx) => (
                            <div key={idx}>
                                <div className="flagged-review">
                                    <h2 className="review-title">{flaggedReview["reviewTitle"]}</h2>
                                    <span>Author: {flaggedReview["authorId"]}</span>
                                    <span>Created: {flaggedReview["date"]}</span>
                                    <span>Rating: {flaggedReview["rating"]}</span>
                                    <span>Votes: {flaggedReview["votes"]}</span>
                                    <span>{flaggedReview["reviewBody"]}</span>
                                    <div className="admin-actions-container">
                                        <button onClick={(e) => hideReview(flaggedReview["id"])}>Hide Review </button>
                                        <button onClick={(e) => clearReviewFlags(flaggedReview["id"])}>Clear Flags</button>
                                    </div>
                                </div>
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
