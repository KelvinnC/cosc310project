"use client"

import React from 'react'
import { useRouter } from 'next/navigation';
import { useData } from './context';
import { useEffect } from 'react';

const page = () => {
    const router = useRouter()
    const {accessToken} = useData()

    useEffect(() => {
        if (!accessToken) {
            router.push("/login")
        } else {
            router.push("/home")
        }
    }, [accessToken, router])


    return (
        <div>
            Redirecting...
        </div>
    )
}

export default page
