"use client"

import { PresetGallery } from "@/components/presets/PresetGallery"
import { Navbar } from "@/components/layout/Navbar"
import ShaderDemo_ATC from "@/components/ui/atc-shader"

export default function PresetsPage() {
    return (
        <main className="relative min-h-screen bg-black font-sans text-white overflow-hidden selection:bg-amber-500/30 selection:text-white">
            {/* Reuse the shader background for consistency, but maybe subtler or just dark bg */}
            <div className="fixed inset-0 z-0 opacity-30 pointer-events-none">
                <ShaderDemo_ATC />
            </div>

            <div className="fixed inset-0 z-0 bg-black/80 pointer-events-none" />

            <div className="relative z-10 flex flex-col min-h-screen">
                <Navbar />

                <div className="flex-1 py-12">
                    <PresetGallery />
                </div>
            </div>
        </main>
    )
}
