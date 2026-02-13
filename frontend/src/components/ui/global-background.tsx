"use client"

import ShaderDemo_ATC from "@/components/ui/atc-shader"

export function GlobalBackground() {
    return (
        <div className="fixed inset-0 z-[-1] pointer-events-none">
            <ShaderDemo_ATC />
            {/* Global Overlay for readability */}
            <div className="absolute inset-0 bg-black/70 backdrop-blur-[1px]" />
            <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,transparent_0%,black_100%)] opacity-80" />
        </div>
    )
}
