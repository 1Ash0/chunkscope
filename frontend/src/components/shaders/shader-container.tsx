"use client"

import { Suspense } from 'react'
import dynamic from 'next/dynamic'
import { Canvas } from '@react-three/fiber'
import { usePerformanceMonitor } from '@/lib/hooks/use-performance-monitor'
import { useMobile } from '@/lib/hooks/use-mobile'
import { ShaderErrorBoundary } from '@/components/feedback/shader-error-boundary'

// Loading fallback
const LoadingFallback = () => (
    <div className="absolute inset-0 bg-background flex items-center justify-center">
        <div className="text-primary/50 text-sm font-mono animate-pulse">Initializing Neural Interface...</div>
    </div>
)

// Mobile/Low-power fallback
const GradientFallback = () => (
    <div className="absolute inset-0 bg-gradient-to-br from-slate-900 to-slate-950" />
)

interface ShaderContainerProps {
    children: React.ReactNode
    fallback?: React.ReactNode
}

const Scene = ({ children }: { children: React.ReactNode }) => {
    return (
        <Canvas
            dpr={[1, 2]} // Clamp pixel ratio for performance
            gl={{
                antialias: false, // Disable MSAA for performance on high-res screens
                powerPreference: "high-performance",
                alpha: true
            }}
            camera={{ position: [0, 0, 10], fov: 45 }}
            resize={{ scroll: false }} // Don't re-render on scroll
            className="absolute inset-0"
        >
            <Suspense fallback={null}>
                {children}
            </Suspense>
        </Canvas>
    )
}

export function ShaderContainer({ children, fallback }: ShaderContainerProps) {
    const isMobile = useMobile()
    const { fps } = usePerformanceMonitor()

    // Auto-degrade if performance is poor (sustainable < 20fps)
    const isLowPerf = fps < 20 && fps > 0

    if (isMobile) {
        return <>{fallback || <GradientFallback />}</>
    }

    return (
        <div className="fixed inset-0 z-0 pointer-events-none">
            <ShaderErrorBoundary fallback={fallback || <GradientFallback />}>
                {isLowPerf && (
                    <div className="absolute top-2 right-2 z-50 bg-black/50 text-red-400 text-xs p-1 rounded font-mono">
                        Low Performance Mode
                    </div>
                )}
                <Suspense fallback={<LoadingFallback />}>
                    <Scene>
                        {children}
                    </Scene>
                </Suspense>
            </ShaderErrorBoundary>
        </div>
    )
}
