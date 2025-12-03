"use client"

import React from 'react'
import { useRouter } from 'next/navigation';
import { useData } from './context';
import { useEffect } from 'react';

const Page = () => {
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

export default Page
