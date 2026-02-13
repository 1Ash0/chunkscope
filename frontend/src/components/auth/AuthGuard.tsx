"use client"

import { useEffect } from "react"
import { useRouter, usePathname } from "next/navigation"
import { useAuthStore } from "@/stores/useAuthStore"
import { Loader2 } from "lucide-react"

interface AuthGuardProps {
    children: React.ReactNode
    fallback?: React.ReactNode
    requireAuth?: boolean
}

export function AuthGuard({ children, fallback, requireAuth = true }: AuthGuardProps) {
    const { isAuthenticated, isLoading, checkAuth } = useAuthStore()
    const router = useRouter()
    const pathname = usePathname()

    useEffect(() => {
        const verify = async () => {
            await checkAuth()
        }
        verify()
    }, [checkAuth])

    useEffect(() => {
        if (!isLoading && requireAuth && !isAuthenticated) {
            // Save the attempted URL to redirect back after login
            const searchParams = new URLSearchParams()
            searchParams.set("from", pathname)
            router.push(`/login?${searchParams.toString()}`)
        }
    }, [isLoading, isAuthenticated, requireAuth, router, pathname])

    if (isLoading) {
        return (
            <div className="min-h-screen bg-black flex flex-col items-center justify-center text-white">
                <Loader2 className="h-10 w-10 animate-spin text-amber-500 mb-4" />
                <p className="text-zinc-500 animate-pulse font-mono text-xs uppercase tracking-widest">Verifying Identity</p>
            </div>
        )
    }

    if (requireAuth && !isAuthenticated) {
        return fallback || null
    }

    return <>{children}</>
}
