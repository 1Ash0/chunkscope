"use client"

import { useState, useEffect } from 'react'

const MOBILE_BREAKPOINT = 768

export function useMobile() {
    const [isMobile, setIsMobile] = useState<boolean>(false)

    useEffect(() => {
        // Initial check
        const checkMobile = () => {
            setIsMobile(window.innerWidth < MOBILE_BREAKPOINT)
        }

        checkMobile()

        // Event listener
        const handleResize = () => {
            checkMobile()
        }

        window.addEventListener('resize', handleResize)

        return () => {
            window.removeEventListener('resize', handleResize)
        }
    }, [])

    return isMobile
}
