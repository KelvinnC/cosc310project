"use client"

import { createContext, useContext, useEffect, useState } from "react"

const DataContext = createContext(null)

export function DataProvider({ children }) {
    const [accessToken, setAccessToken] = useState(() => {
        try {
            return localStorage.getItem("accessToken") || ""
        } catch (err) {
            return ""
        }
    })

    useEffect(() => {
        try {
            if (accessToken) {
                localStorage.setItem("accessToken", accessToken)
            } else {
                localStorage.removeItem("accessToken")
            }
        } catch (err) {
            
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
        clearAccessToken,
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