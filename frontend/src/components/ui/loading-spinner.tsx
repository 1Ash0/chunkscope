"use client"

import { motion } from "framer-motion"
import { cn } from "@/lib/utils"

interface LoadingSpinnerProps {
    className?: string
    size?: "sm" | "md" | "lg" | "xl"
}

export function LoadingSpinner({ className, size = "md" }: LoadingSpinnerProps) {
    const sizeClasses = {
        sm: "w-4 h-4",
        md: "w-8 h-8",
        lg: "w-12 h-12",
        xl: "w-16 h-16"
    }

    return (
        <div className={cn("relative flex items-center justify-center", sizeClasses[size], className)}>
            {/* Outer Ring */}
            <motion.div
                className="absolute inset-0 border-2 border-transparent border-t-gold border-r-gold/30 rounded-full"
                animate={{ rotate: 360 }}
                transition={{ duration: 1.5, repeat: Infinity, ease: "linear" }}
            />

            {/* Middle Ring (Opposite direction) */}
            <motion.div
                className="absolute inset-1 border-2 border-transparent border-b-electric border-l-electric/30 rounded-full"
                animate={{ rotate: -360 }}
                transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
            />

            {/* Inner Core (Pulsing) */}
            <motion.div
                className="absolute w-[30%] h-[30%] bg-white rounded-full"
                animate={{ scale: [0.8, 1.2, 0.8], opacity: [0.5, 1, 0.5] }}
                transition={{ duration: 1.5, repeat: Infinity, ease: "easeInOut" }}
            />
        </div>
    )
}
