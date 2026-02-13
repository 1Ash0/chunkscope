"use client"

import React from "react"
import Link from "next/link"
import { useRouter } from "next/navigation"
import { useAuthStore } from "@/stores/useAuthStore"
import { useConfigStore } from "@/stores/useConfigStore"
import { analyzerApi } from "@/lib/api"
import { motion } from "framer-motion"
import ShaderDemo_ATC from "@/components/ui/atc-shader"
import { ArrowRight, Database, Github, Search, Eye, GitBranch, Layers, Zap, Cpu } from "lucide-react"
import { Button } from "@/components/ui/button"
import { DocumentSelectionModal } from "@/components/presets/DocumentSelectionModal"
import { useToast } from "@/components/ui/use-toast"
import { AnimatePresence } from "framer-motion"

export default function Home() {
    const { isAuthenticated } = useAuthStore()
    const router = useRouter()
    const { toast } = useToast()
    const fileInputRef = React.useRef<HTMLInputElement>(null)
    const [isAnalyzing, setIsAnalyzing] = React.useState(false)
    const setSelectedDocId = useConfigStore((state) => state.setSelectedDocId)
    const [isUploadModalOpen, setIsUploadModalOpen] = React.useState(false)

    const [mousePos, setMousePos] = React.useState({ x: 0, y: 0 })

    const handleFileSelect = () => {
        if (!isAuthenticated) {
            router.push("/login")
            return
        }
        fileInputRef.current?.click()
    }

    const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0]
        if (!file) return

        setIsAnalyzing(true)
        try {
            const result = await analyzerApi.analyzeDocument(file)
            setSelectedDocId(result.document_id)
            router.push(`/visualizer?docId=${result.document_id}`)
        } catch (error) {
            console.error("Analysis failed:", error)
        } finally {
            setIsAnalyzing(false)
        }
    }

    const handleVisualize = (docId: string) => {
        setSelectedDocId(docId)
        router.push(`/visualizer?docId=${docId}`)
    }

    const handleUploadSuccess = (docId: string) => {
        setIsUploadModalOpen(false)
        toast({
            title: "Document Ready",
            description: "Opening in visualizer...",
        })
        handleVisualize(docId)
    }

    const handleMouseMove = (e: React.MouseEvent) => {
        const { clientX, clientY } = e
        const x = (clientX / window.innerWidth - 0.5) * 20
        const y = (clientY / window.innerHeight - 0.5) * 20
        setMousePos({ x, y })
    }

    return (
        <main
            onMouseMove={handleMouseMove}
            className="relative min-h-screen bg-black text-white font-sans overflow-x-hidden selection:bg-orange-500/30 selection:text-orange-200"
        >
            {/* Hidden File Input */}
            <input
                type="file"
                ref={fileInputRef}
                className="hidden"
                onChange={handleFileChange}
                accept=".pdf,.txt,.md"
            />

            {/* Fixed Background - ATC Shader */}
            <div className="fixed inset-0 z-0 pointer-events-none">
                <ShaderDemo_ATC />
                {/* Lighter overlay to let shader pop, with a gradient fade at bottom */}
                <div className="absolute inset-0 bg-black/60 backdrop-blur-[1px]" />
                <div className="absolute inset-0 bg-gradient-to-b from-transparent via-transparent to-black" />
            </div>

            {/* Navigation */}
            <nav className="fixed top-0 w-full z-50 border-b border-white/5 bg-black/40 backdrop-blur-md">
                <div className="container mx-auto px-6 h-16 flex items-center justify-between">
                    <div className="flex items-center gap-3">
                        <div className="w-6 h-6 bg-gradient-to-br from-orange-500 to-amber-700 rounded-md flex items-center justify-center shadow-lg shadow-orange-900/20">
                            <Layers className="text-white w-3 h-3" />
                        </div>
                        <span className="text-[10px] font-black tracking-[0.2em] text-white/90 uppercase">ChunkScope</span>
                    </div>

                    <div className="flex items-center gap-6">
                        <Link href="https://github.com/1Ash0/chunkscope" className="text-zinc-500 hover:text-white transition-colors">
                            <Github className="w-4 h-4" />
                        </Link>
                        <Link
                            href={isAuthenticated ? "/dashboard" : "/login"}
                            className="px-4 py-1.5 bg-transparent border border-white/20 text-white text-[9px] uppercase font-black rounded-full hover:bg-white/10 hover:scale-105 transition-all shadow-[0_0_10px_rgba(255,255,255,0.1)] tracking-widest"
                        >
                            {isAuthenticated ? "Dashboard" : "Get Started"}
                        </Link>
                    </div>
                </div>
            </nav>

            {/* Content Container - z-10 floats above shader */}
            <div className="relative z-10 flex flex-col items-center">

                {/* Hero Section */}
                <section className="min-h-screen flex flex-col items-center justify-center px-4 pt-32 pb-40 w-full max-w-5xl mx-auto text-center relative">
                    <motion.div
                        style={{
                            x: mousePos.x,
                            y: mousePos.y,
                        }}
                        initial={{ opacity: 0, y: 30 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.8, ease: "easeOut" }}
                        className="space-y-12"
                    >
                        {/* Status Badge */}
                        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-white/5 border border-white/10 backdrop-blur-md text-[8px] font-black tracking-[0.4em] uppercase text-zinc-500 mb-4 shadow-[0_0_20px_rgba(255,255,255,0.02)]">
                            <span className="w-1 h-1 rounded-full bg-orange-500 animate-pulse" />
                            Public Beta v0.1.0
                        </div>

                        {/* Title - Balanced Typography & Blending */}
                        <div className="relative group">
                            <div className="absolute -inset-8 rounded-full bg-orange-500/5 opacity-0 group-hover:opacity-100 blur-3xl transition-opacity pointer-events-none" />
                            <h1 className="relative text-5xl md:text-[6.5rem] font-heading font-black tracking-[-0.04em] text-white leading-[0.85] mix-blend-plus-lighter drop-shadow-[0_0_40px_rgba(255,255,255,0.1)]">
                                THE INSPECT<br />
                                <span className="text-white/20 tracking-tighter">ELEMENT</span> FOR <span className="text-transparent bg-clip-text bg-gradient-to-r from-orange-400 to-amber-600 drop-shadow-[0_0_30px_rgba(245,183,0,0.4)]">RAG</span>
                            </h1>
                        </div>

                        {/* Subtitle */}
                        <p className="text-sm md:text-base text-zinc-400 max-w-lg mx-auto font-medium leading-relaxed tracking-wide opacity-80">
                            Deep dive into your <span className="text-white italic underline decoration-orange-500/30 underline-offset-4">vector space</span>. Visualize semantic chunks, debug retrieval quality, and optimize your knowledge graph with forensic precision.
                        </p>

                        {/* Quick Analyze Component - High Interactivity */}
                        <div className="max-w-md mx-auto p-1 bg-white/5 backdrop-blur-3xl border border-white/5 rounded-2xl group transition-all relative overflow-hidden shadow-2xl">
                            {/* Scanning Animation Ring - Subtler */}
                            <motion.div
                                animate={{
                                    rotate: 360,
                                }}
                                transition={{
                                    duration: 6,
                                    repeat: Infinity,
                                    ease: "linear",
                                }}
                                className="absolute -inset-full bg-gradient-to-t from-transparent via-orange-500/5 to-transparent opacity-0 group-hover:opacity-100 pointer-events-none"
                            />

                            <div className="flex items-center gap-2 p-2 relative z-10">
                                <div
                                    onClick={handleFileSelect}
                                    className="flex-1 flex items-center gap-3 px-4 py-3 bg-black/40 rounded-xl border border-white/5 text-left text-zinc-500 text-[9px] font-black uppercase tracking-widest cursor-pointer hover:bg-neutral-900/40 transition-colors group-hover:text-zinc-300"
                                >
                                    <Search className="w-3.5 h-3.5 text-orange-500/70" />
                                    <span>{isAnalyzing ? "Processing Analysis..." : "Select Document to Analyze..."}</span>
                                </div>
                                <Button
                                    onClick={handleFileSelect}
                                    disabled={isAnalyzing}
                                    className="bg-orange-500 hover:bg-orange-400 text-black font-black text-[9px] uppercase tracking-widest h-11 px-8 rounded-xl shadow-[0_0_40px_rgba(245,183,0,0.4)] transition-all active:scale-95"
                                >
                                    {isAnalyzing ? "..." : "Analyze"}
                                </Button>
                            </div>
                        </div>

                        {/* CTAs */}
                        <div className="flex flex-col sm:flex-row gap-5 justify-center pt-8">
                            <Link
                                href={isAuthenticated ? "/visualizer" : "/login"}
                                className="group relative px-10 py-3.5 bg-white/5 backdrop-blur-md border border-white/10 text-white rounded-full font-black text-[9px] uppercase tracking-[0.25em] hover:bg-white/10 active:scale-95 transition-all flex items-center justify-center gap-3 hover:border-orange-500/40 shadow-lg"
                            >
                                <Eye className="w-3.5 h-3.5 text-orange-400" />
                                Launch Visualizer
                            </Link>
                            <Link
                                href={isAuthenticated ? "/pipeline" : "/login"}
                                className="group relative px-10 py-3.5 bg-white/5 backdrop-blur-md border border-white/10 text-white rounded-full font-black text-[9px] uppercase tracking-[0.25em] hover:bg-white/10 active:scale-95 transition-all flex items-center justify-center gap-3 hover:border-purple-500/40 shadow-lg"
                            >
                                <Cpu className="w-3.5 h-3.5 text-purple-400" />
                                Pipeline Builder
                            </Link>
                        </div>
                    </motion.div>

                    {/* Scroll Indicator - Bottom Fixed and further away */}
                    <div className="absolute bottom-12 flex flex-col items-center gap-3 pointer-events-none w-full">
                        <span className="text-[7px] font-black uppercase tracking-[0.5em] text-zinc-700 animate-pulse">Scan Below</span>
                        <motion.div
                            animate={{ y: [0, 10, 0] }}
                            transition={{ duration: 2.5, repeat: Infinity, ease: "easeInOut" }}
                            className="w-[1px] h-10 bg-gradient-to-b from-orange-500 to-transparent opacity-40"
                        />
                    </div>
                </section>

                {/* Features / Toolkit Section */}
                <section className="w-full max-w-6xl mx-auto px-6 py-12 md:py-16">
                    <div className="text-center mb-10 space-y-2">
                        <h2 className="text-3xl md:text-4xl font-bold tracking-tight text-white">
                            Universal Toolkit
                        </h2>
                        <p className="text-zinc-500 max-w-lg mx-auto text-sm font-normal">
                            High-density forensic tools for modern RAG architectures.
                        </p>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
                        {/* Analyzer Card */}
                        <Link href={isAuthenticated ? "/analyze" : "/login"}>
                            <motion.div
                                whileHover={{ scale: 1.02 }}
                                whileTap={{ scale: 0.98 }}
                                className="group relative p-5 rounded-xl bg-white/5 backdrop-blur-lg border border-white/10 overflow-hidden hover:border-blue-500/50 transition-all cursor-pointer h-full flex flex-col"
                            >
                                <div className="absolute inset-0 bg-gradient-to-br from-blue-500/10 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
                                <div className="relative z-10 flex flex-col h-full">
                                    <div className="w-10 h-10 rounded-lg bg-blue-500/10 flex items-center justify-center mb-4 ring-1 ring-blue-500/20 group-hover:ring-blue-500/50 transition-all">
                                        <Search className="w-5 h-5 text-blue-400" />
                                    </div>
                                    <h3 className="text-lg font-bold text-white mb-2 tracking-tight">Analyzer</h3>
                                    <p className="text-zinc-400 text-xs leading-relaxed mb-4 flex-grow font-light">
                                        Inspect token overlaps and semantic density in real-time.
                                    </p>
                                    <div className="flex items-center text-[10px] font-bold text-blue-400 uppercase tracking-widest group-hover:translate-x-1 transition-transform">
                                        Go to Tool <ArrowRight className="w-3 h-3 ml-2" />
                                    </div>
                                </div>
                            </motion.div>
                        </Link>

                        {/* Visualizer Card */}
                        <div className="group">
                            <motion.div
                                whileHover={{ scale: 1.02 }}
                                whileTap={{ scale: 0.98 }}
                                className="group relative p-6 rounded-[2rem] bg-white/[0.03] backdrop-blur-xl border border-white/10 overflow-hidden hover:border-orange-500/50 transition-all cursor-pointer h-full flex flex-col justify-between"
                            >
                                <div className="absolute top-0 right-0 w-32 h-32 bg-orange-500/5 blur-3xl rounded-full -mr-16 -mt-16 opacity-50 transition-opacity group-hover:opacity-80" />

                                <div className="relative z-10">
                                    <div className="w-12 h-12 rounded-2xl bg-orange-500/10 flex items-center justify-center mb-6 ring-1 ring-orange-500/20 group-hover:scale-110 transition-transform">
                                        <Database className="w-6 h-6 text-orange-400" />
                                    </div>
                                    <h3 className="text-xl font-bold text-white mb-2 tracking-tight uppercase">Visualizer</h3>
                                    <p className="text-zinc-400 text-xs leading-relaxed mb-6 font-light opacity-80">
                                        3D spatial map of embedding clusters to identify semantics gaps.
                                    </p>
                                </div>

                                <div className="flex items-center gap-4 relative z-10">
                                    <button
                                        onClick={() => {
                                            if (!isAuthenticated) {
                                                router.push("/login")
                                            } else {
                                                router.push("/visualizer")
                                            }
                                        }}
                                        className="flex items-center text-[10px] font-black text-orange-400 uppercase tracking-[0.2em] group-hover:translate-x-1 transition-all"
                                    >
                                        Launch <ArrowRight className="w-4 h-4 ml-2" />
                                    </button>
                                    <button
                                        onClick={(e) => {
                                            e.stopPropagation()
                                            if (!isAuthenticated) {
                                                router.push("/login")
                                            } else {
                                                setIsUploadModalOpen(true)
                                            }
                                        }}
                                        className="px-4 py-2 rounded-xl bg-zinc-900 border border-white/5 text-[9px] font-black text-zinc-500 hover:text-white hover:bg-zinc-800 hover:border-white/10 transition-all uppercase tracking-widest"
                                    >
                                        Upload New
                                    </button>
                                </div>
                            </motion.div>
                        </div>

                        {/* Builder Card */}
                        <Link href={isAuthenticated ? "/pipeline" : "/login"}>
                            <motion.div
                                whileHover={{ scale: 1.02 }}
                                whileTap={{ scale: 0.98 }}
                                className="group relative p-5 rounded-xl bg-white/5 backdrop-blur-lg border border-white/10 overflow-hidden hover:border-purple-500/50 transition-all cursor-pointer h-full flex flex-col"
                            >
                                <div className="absolute inset-0 bg-gradient-to-br from-purple-500/10 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
                                <div className="relative z-10 flex flex-col h-full">
                                    <div className="w-10 h-10 rounded-lg bg-purple-500/10 flex items-center justify-center mb-4 ring-1 ring-purple-500/20 group-hover:ring-purple-500/50 transition-all">
                                        <GitBranch className="w-5 h-5 text-purple-400" />
                                    </div>
                                    <h3 className="text-lg font-bold text-white mb-2 tracking-tight">Builder</h3>
                                    <p className="text-zinc-400 text-xs leading-relaxed mb-4 flex-grow font-light">
                                        Construct and benchmark custom chunking pipelines instantly.
                                    </p>
                                    <div className="flex items-center text-[10px] font-bold text-purple-400 uppercase tracking-widest group-hover:translate-x-1 transition-transform">
                                        Go to Tool <ArrowRight className="w-3 h-3 ml-2" />
                                    </div>
                                </div>
                            </motion.div>
                        </Link>
                    </div>
                </section>

                {/* Technical Specs / Minimal Stats */}
                <section className="w-full max-w-4xl mx-auto px-6 py-10 border-t border-white/5">
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-center divide-x divide-white/5">
                        <div className="p-2">
                            <div className="text-xl font-mono font-bold text-white mb-0.5"><span className="text-gold">&lt;</span> 50ms</div>
                            <div className="text-[9px] font-medium uppercase tracking-widest text-zinc-600">Latency</div>
                        </div>
                        <div className="p-2">
                            <div className="text-xl font-mono font-bold text-white mb-0.5">100%</div>
                            <div className="text-[9px] font-medium uppercase tracking-widest text-zinc-600">Visual Fidelity</div>
                        </div>
                        <div className="p-2">
                            <div className="text-xl font-mono font-bold text-white mb-0.5">WebGL</div>
                            <div className="text-[9px] font-medium uppercase tracking-widest text-zinc-600">Engine</div>
                        </div>
                        <div className="p-2">
                            <div className="text-xl font-mono font-bold text-white mb-0.5">Auto</div>
                            <div className="text-[9px] font-medium uppercase tracking-widest text-zinc-600">Optimize</div>
                        </div>
                    </div>
                </section>

                {/* Final CTA */}
                <section className="w-full py-16 flex flex-col items-center text-center space-y-4">
                    <h2 className="text-3xl md:text-4xl font-heading font-bold tracking-tighter text-white">
                        Build Smarter RAG.
                    </h2>
                    <Link
                        href={isAuthenticated ? "/dashboard" : "/login"}
                        className="px-8 py-2.5 bg-[#F5B700] text-black text-xs font-bold rounded-full hover:scale-105 active:scale-95 transition-transform shadow-[0_0_30px_rgba(245,183,0,0.2)]"
                    >
                        Enter Terminal
                    </Link>
                    <p className="text-zinc-600 text-[9px] tracking-widest uppercase mt-4">
                        © 2025 ChunkScope
                    </p>
                </section>

                <AnimatePresence>
                    {isUploadModalOpen && (
                        <DocumentSelectionModal
                            isOpen={isUploadModalOpen}
                            onClose={() => setIsUploadModalOpen(false)}
                            onSuccess={handleUploadSuccess}
                            onUseDemo={() => {
                                toast({ title: "Demo Mode", description: "Demo document selected. Entering visualizer..." })
                                handleVisualize("demo-id")
                            }}
                            presetName="Visualizer"
                        />
                    )}
                </AnimatePresence>
            </div>
        </main>
    )
}
