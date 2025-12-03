"use client"

import React from 'react'
import { useRouter } from 'next/navigation'
import { useEffect } from 'react'
import { useData } from '../context'

const Page = () => {
    const router = useRouter()
    const {clearAccessToken} = useData() as any

    useEffect(() => {
        clearAccessToken()
        router.replace('/login')
    }, [clearAccessToken, router])

  return (
    <div>
        Logging out. Redirecting...
    </div>
  )
}

export default Page
