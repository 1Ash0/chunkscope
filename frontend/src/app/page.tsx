"use client"

import ShaderDemo_ATC from "@/components/ui/atc-shader"
import { ArrowRight, Database, GitBranch, Github, Search, Sparkles } from "lucide-react"
import Link from "next/link"
import { PresetGallery } from "@/components/presets/PresetGallery"
import { useAuthStore } from "@/stores/useAuthStore"

export default function Home() {
    const { isAuthenticated, user } = useAuthStore()

    return (
        <main className="relative min-h-screen bg-transparent font-sans text-white overflow-hidden selection:bg-amber-500/30 selection:text-white">
            {/* Background Shader Component */}
            <ShaderDemo_ATC />

            {/* Gradient Overlay for Readability - Fading to black at the bottom */}
            <div className="fixed inset-0 z-0 bg-gradient-to-b from-transparent via-black/60 to-black pointer-events-none" />

            {/* Main Content Wrapper */}
            <div className="relative z-10 flex flex-col min-h-screen">

                {/* Navigation */}
                <header className="w-full h-16 border-b border-white/5 bg-black/10 backdrop-blur-sm sticky top-0 z-50">
                    <div className="container mx-auto px-6 h-full flex items-center justify-between">
                        <div className="flex items-center gap-2 font-bold tracking-tight text-white">
                            <span>ChunkScope</span>
                        </div>

                        <nav className="hidden md:flex items-center gap-8 text-sm font-medium text-zinc-400">
                            <Link href="#features" className="hover:text-white transition-colors">Features</Link>
                            <Link href="#docs" className="hover:text-white transition-colors">Docs</Link>
                            <Link href="https://github.com/1Ash0/chunkscope" className="hover:text-white transition-colors">GitHub</Link>
                        </nav>

                        <div className="flex items-center gap-4">
                            {isAuthenticated ? (
                                <Link href="/dashboard">
                                    <button className="hidden sm:flex text-xs font-semibold bg-white text-black px-4 py-2 rounded-full hover:bg-amber-50 transition-colors">
                                        Dashboard
                                    </button>
                                </Link>
                            ) : (
                                <div className="flex gap-2">
                                    <Link href="/login">
                                        <button className="text-xs font-medium text-zinc-300 hover:text-white px-3 py-2 transition-colors">
                                            Log In
                                        </button>
                                    </Link>
                                    <Link href="/get-started">
                                        <button className="hidden sm:flex text-xs font-semibold bg-white text-black px-4 py-2 rounded-full hover:bg-amber-50 transition-colors">
                                            Get Started
                                        </button>
                                    </Link>
                                </div>
                            )}
                        </div>
                    </div>
                </header>

                {/* Hero Section */}
                <section className="flex-1 flex flex-col items-center justify-center text-center px-4 py-24 md:py-32">

                    {/* Beta Badge with glowing dot - Gold/Amber */}
                    <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full border border-amber-500/20 bg-amber-900/20 backdrop-blur-sm text-xs font-medium text-amber-400 mb-8">
                        <span className="relative flex h-2 w-2">
                            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-amber-400 opacity-75"></span>
                            <span className="relative inline-flex rounded-full h-2 w-2 bg-amber-500"></span>
                        </span>
                        v0.1.0 Public Beta
                    </div>

                    {/* Headline - "The Inspect Element for RAG Pipelines" */}
                    <h1 className="max-w-5xl text-5xl md:text-7xl lg:text-8xl font-bold tracking-tighter mb-6 text-white drop-shadow-sm">
                        The Inspect Element <br /> for RAG Pipelines.
                    </h1>

                    {/* Subtext */}
                    <p className="max-w-2xl text-lg md:text-xl text-zinc-300 mb-10 leading-relaxed font-normal">
                        Deep dive into your vector embeddings. Visualize semantic chunks, debug retrieval quality, and optimize your knowledge graph in real-time.
                    </p>

                    {/* CTA Buttons - Primary White, Secondary Glass */}
                    <div className="flex flex-col sm:flex-row gap-4 w-full sm:w-auto px-6 sm:px-0">
                        <Link href="/visualizer" className="h-12 px-8 rounded-full bg-white text-black font-semibold hover:bg-zinc-200 transition-all flex items-center justify-center gap-2 group w-full sm:w-auto shadow-[0_0_20px_rgba(255,255,255,0.2)]">
                            Launch Visualizer
                            <ArrowRight className="h-4 w-4 group-hover:translate-x-1 transition-transform" />
                        </Link>
                        <Link href="/pipeline" className="h-12 px-8 rounded-full border border-white/10 bg-white/5 backdrop-blur-sm hover:bg-white/10 transition-colors font-medium text-white w-full sm:w-auto flex items-center justify-center">
                            Pipeline Builder
                        </Link>
                    </div>
                </section>

                {/* Feature Grid - Bento Style */}
                <section id="features" className="w-full py-24 border-t border-white/5 bg-black/50 backdrop-blur-sm">
                    <div className="container mx-auto px-6">
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                            <FeatureCard
                                icon={<Search className="h-5 w-5 text-amber-200" />}
                                title="Vector Visualization"
                                description="Debug vector distances and similarity scores with high-performance 2D projection."
                            />
                            <FeatureCard
                                icon={<Database className="h-5 w-5 text-amber-200" />}
                                title="Retrieval Debugging"
                                description="Visualize how documents are split and identify lost context or orphan chunks instantly."
                            />
                            <FeatureCard
                                icon={<GitBranch className="h-5 w-5 text-amber-200" />}
                                title="Knowledge Graph"
                                description="Trace the path of a query from retrieval to generation to pinpoint hallucination sources."
                            />
                        </div>
                    </div>
                </section>

                {/* Templates Section */}
                <section id="templates" className="w-full py-24 border-t border-white/5 bg-black/40">
                    <PresetGallery />
                </section>

                {/* Analysis CTA Section */}
                <section className="w-full py-24 border-t border-white/5 bg-gradient-to-b from-black/40 to-black/80 text-center">
                    <div className="container mx-auto px-6">
                        <div className="max-w-3xl mx-auto p-12 rounded-3xl border border-white/10 bg-white/5 backdrop-blur-xl relative overflow-hidden group">
                            <div className="absolute -top-24 -right-24 w-64 h-64 bg-amber-500/10 rounded-full blur-3xl group-hover:bg-amber-500/20 transition-all duration-500" />

                            <Sparkles className="h-12 w-12 text-amber-500 mx-auto mb-6" />
                            <h2 className="text-3xl md:text-4xl font-bold mb-4">Unsure about your configuration?</h2>
                            <p className="text-zinc-400 mb-8 text-lg">
                                Upload your document and let our AI analyzer recommend the optimal chunking strategy, embedding models, and retrieval parameters based on your content's structure.
                            </p>
                            <Link
                                href="/analyze"
                                className="inline-flex h-12 px-8 rounded-full bg-amber-500 text-black font-bold hover:bg-amber-600 transition-all hover:scale-105 active:scale-95 items-center gap-2"
                            >
                                Start Document Analysis
                                <ArrowRight className="h-4 w-4" />
                            </Link>
                        </div>
                    </div>
                </section>

                {/* Footer */}
                <footer className="w-full py-8 text-center border-t border-white/5 bg-black">
                    <div className="flex items-center justify-center gap-6 mb-4">
                        <Github className="h-5 w-5 text-zinc-500 hover:text-white transition-colors cursor-pointer" />
                    </div>
                    <p className="text-xs text-zinc-600 font-mono">
                        Designed for AI Engineers. Open Source.
                    </p>
                </footer>
            </div>
        </main>
    )
}

function FeatureCard({ icon, title, description }: { icon: React.ReactNode, title: string, description: string }) {
    return (
        <div className="p-8 rounded-xl border border-white/5 bg-white/5 hover:bg-white/[0.07] transition-colors group">
            <div className="mb-4 p-3 rounded-lg bg-zinc-900 border border-white/5 w-fit">
                {icon}
            </div>
            <h3 className="text-lg font-semibold mb-2 text-white tracking-tight">{title}</h3>
            <p className="text-zinc-400 leading-relaxed text-sm">
                {description}
            </p>
        </div>
    )
}
