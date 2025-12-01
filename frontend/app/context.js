"use client"

import { createContext, useContext, useEffect, useState } from "react"
import decodeToken from "../lib/decodeToken"

const DataContext = createContext(null)

export function DataProvider({ children }) {
    const [accessToken, setAccessToken] = useState(() => {
        try {
            return localStorage.getItem("accessToken") || ""
        } catch (err) {
            return ""
        }
    })
    const [role, setRole] = useState(() => {
        try {
            const token = localStorage.getItem("accessToken")
            if (token) {
                const payload = decodeToken(token)
                return payload?.role || null
            }
        } catch (err) {
                return null
        }
    })

    useEffect(() => {
        try {
            if (accessToken) {
                localStorage.setItem("accessToken", accessToken)
                const payload = decodeToken(accessToken)
                setRole(payload?.role || null)
            } else {
                localStorage.removeItem("accessToken")
                setRole(null)
            }
        } catch (err) {
            console.error('Error in accessToken effect:', err)
        }
    }, [accessToken])

    const saveAccessToken = (token) => {
        setAccessToken(token)
    }

    const clearAccessToken = () => {
        setAccessToken("")
    }

    const value = {
        accessToken,
        setAccessToken: saveAccessToken,
        clearAccessToken, role
    }

    return <DataContext.Provider value={value}>{children}</DataContext.Provider>
}

export function useData() {
    const ctx = useContext(DataContext)
    if (!ctx) {
        throw new Error("useData must be used inside a DataProvider")
    }
    return ctx
}