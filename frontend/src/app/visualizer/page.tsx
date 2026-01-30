"use client"

import { useEffect } from 'react'
import { ChunkVisualizer } from '@/components/visualizer/chunk-visualizer'
import { ChunkConfigPanel } from '@/components/visualizer/chunk-config-panel'
import { ChunkDetailPanel } from '@/components/visualizer/chunk-detail-panel'
import { useChunkStore } from '@/stores/useChunkStore'
import { DEMO_PDF_URL, MOCK_CHUNKS } from '@/lib/mock-data'
import ShaderDemo_ATC from '@/components/ui/atc-shader'
import { ArrowLeft } from 'lucide-react'
import Link from 'next/link'

export default function VisualizerPage() {
    const { selectedChunk, setSelectedChunk } = useChunkStore()

    // In a real app, we would fetch chunks from API here.
    // For now, we inject the mock data.
    // Note: We don't auto-set chunks here because ChunkVisualizer 
    // accepts initialChunks prop which handles it.

    return (
        <div className="relative min-h-screen bg-black text-white overflow-hidden font-sans selection:bg-amber-500/30 selection:text-white">

            {/* Background: Subtle shader */}
            <div className="fixed inset-0 z-0 opacity-40">
                <ShaderDemo_ATC />
            </div>
            <div className="fixed inset-0 z-0 bg-black/80 pointer-events-none" />

            {/* Header */}
            <header className="relative z-20 h-16 border-b border-white/10 bg-black/40 backdrop-blur-md flex items-center px-6 justify-between">
                <div className="flex items-center gap-4">
                    <Link href="/" className="p-2 -ml-2 rounded-full hover:bg-white/10 transition-colors text-neutral-400 hover:text-white">
                        <ArrowLeft className="w-5 h-5" />
                    </Link>
                    <div className="flex flex-col">
                        <h1 className="text-sm font-semibold text-white tracking-wide uppercase">Chunk Visualizer</h1>
                        <span className="text-[10px] text-green-400 font-mono">LIVE PREVIEW • 1706.03762.pdf</span>
                    </div>
                </div>
                <div className="text-xs text-neutral-500 font-mono hidden md:block">
                    Use scroll to zoom • Click to inspect
                </div>
            </header>

            {/* Main Layout: Sidebar + Canvas */}
            <main className="relative z-10 flex h-[calc(100vh-64px)] overflow-hidden">

                {/* Left Sidebar: Config */}
                <aside className="w-80 border-r border-white/10 bg-black/40 backdrop-blur-xl p-4 overflow-y-auto hidden md:block">
                    <ChunkConfigPanel />
                </aside>

                {/* Center: Canvas Area */}
                <section className="flex-1 relative bg-neutral-900/50 overflow-hidden flex flex-col">
                    <div className="flex-1 relative m-4 rounded-xl overflow-hidden border border-white/5 shadow-2xl">
                        <ChunkVisualizer
                            pdfUrl={DEMO_PDF_URL}
                            initialChunks={MOCK_CHUNKS}
                            scale={1.2}
                        />
                    </div>
                </section>

                {/* Right Drawer: Detail Panel (conditionally rendered) */}
                {/* We use the AnimatePresence inside the component itself, or control it here.
            The component was built to handle its own exit animations via AnimatePresence 
            wrapping usually, but here we conditionally render it and let it handle entry/exit 
            if it was mounted. However, our component assumes it's always mounted or we handle opacity.
            
            Let's rely on the store state:
        */}
                {selectedChunk && (
                    <ChunkDetailPanel
                        chunk={selectedChunk}
                        onClose={() => setSelectedChunk(null)}
                    />
                )}
            </main>
        </div>
    )
}
