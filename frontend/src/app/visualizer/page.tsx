"use client"

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { useSearchParams, useRouter } from 'next/navigation'
import { ArrowLeft, Loader2, ArrowRight } from 'lucide-react'
import { pipelinesApi, documentsApi, chunksApi } from '@/lib/api'
import { useConfigStore, ChunkingMethod } from '@/stores/useConfigStore'
import { useChunkStore } from '@/stores/useChunkStore'
import { useAuthStore } from '@/stores/useAuthStore'
import { ChunkConfigPanel } from '@/components/visualizer/chunk-config-panel'
import { ChunkVisualizer } from '@/components/visualizer/chunk-visualizer'
import { ChunkDetailPanel } from '@/components/visualizer/chunk-detail-panel'
import ShaderDemo_ATC from '@/components/ui/atc-shader'
import { DEMO_PDF_URL, MOCK_CHUNKS } from '@/lib/mock-data'

import { AuthGuard } from '@/components/auth/AuthGuard'
import { getErrorMessage } from '@/lib/utils'

export default function VisualizerPage() {
    const { selectedChunk, setSelectedChunk } = useChunkStore()
    const searchParams = useSearchParams()
    const pipelineId = searchParams.get('pipeline_id')

    const [loading, setLoading] = useState(false)
    const [fetchingPipelines, setFetchingPipelines] = useState(false)
    const [pipelines, setPipelines] = useState<any[]>([])
    const [error, setError] = useState<string | null>(null)
    const [pdfUrl, setPdfUrl] = useState<string>(DEMO_PDF_URL)
    const [chunks, setChunks] = useState<any[]>(MOCK_CHUNKS)
    const [docName, setDocName] = useState<string>('Demo Document')
    const [documentId, setDocumentId] = useState<string | null>(null)

    const { setMethod, setChunkSize, setOverlap, setThreshold } = useConfigStore()

    const router = useRouter()
    const { isAuthenticated, user: authUser } = useAuthStore()

    useEffect(() => {
        if (pipelineId) {
            loadPipeline(pipelineId)
        } else if (isAuthenticated) {
            // Load the list of pipelines for the user to choose from
            loadPipelinesList()
        }
    }, [pipelineId, isAuthenticated])

    const loadPipelinesList = async () => {
        setFetchingPipelines(true)
        try {
            const response = await pipelinesApi.listPipelines()
            setPipelines(response.items || [])
        } catch (error) {
            console.error('Failed to fetch pipelines list:', error)
        } finally {
            setFetchingPipelines(false)
        }
    }

    const loadPipeline = async (id: string) => {
        setLoading(true)
        setError(null)
        try {
            console.log('Loading pipeline:', id)
            const pipeline = await pipelinesApi.getPipeline(id)

            const settings = pipeline.settings || {}
            const chunking = settings.chunking || {}

            // Sync with store
            if (chunking.method) setMethod(chunking.method as ChunkingMethod)
            if (chunking.chunk_size) setChunkSize(chunking.chunk_size)
            if (chunking.overlap) setOverlap(chunking.overlap)
            if (chunking.threshold) setThreshold(chunking.threshold)

            // Load actual document if linked
            if (settings.document_id) {
                setDocumentId(settings.document_id)
                const doc = await documentsApi.getDocument(settings.document_id)
                setDocName(doc.original_filename)

                const url = documentsApi.getDocumentContentUrl(settings.document_id)
                setPdfUrl(url)

                const vizData = await chunksApi.visualizeChunks(settings.document_id, {
                    method: chunking.method || 'fixed',
                    chunk_size: chunking.chunk_size || 500,
                    overlap: chunking.overlap || 50
                })
                setChunks(vizData.chunks)
            }
        } catch (error: any) {
            console.error('Failed to load pipeline:', error)
            setError(getErrorMessage(error.response?.data?.detail || error.message || 'Error loading pipeline'))
        } finally {
            setLoading(false)
        }
    }

    return (
        <AuthGuard requireAuth={false}>
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
                            <span className="text-[10px] text-green-400 font-mono">
                                {pipelineId ? `PIPELINE: ${pipelineId.slice(0, 8)}...` : 'DEMO PREVIEW'} • {docName}
                            </span>
                        </div>
                    </div>
                    <div className="text-xs text-neutral-500 font-mono hidden md:block">
                        Use scroll to zoom • Click to inspect
                    </div>
                </header>

                {/* Main Layout */}
                <main className="relative z-10 flex h-[calc(100vh-64px)] overflow-hidden">
                    {/* Left Sidebar: Config */}
                    <aside className="w-80 border-r border-white/10 bg-black/40 backdrop-blur-xl p-4 overflow-y-auto hidden md:block">
                        <ChunkConfigPanel documentId={documentId} />
                    </aside>

                    {/* Center: Canvas Area */}
                    <section className="flex-1 relative bg-neutral-900/50 flex flex-col min-w-0 overflow-hidden">
                        <div className="flex-1 relative m-4 rounded-xl border border-white/5 shadow-2xl bg-zinc-950 flex flex-col overflow-hidden">
                            {loading && (
                                <div className="absolute inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm">
                                    <div className="flex flex-col items-center gap-4">
                                        <Loader2 className="w-12 h-12 text-amber-500 animate-spin" />
                                        <p className="text-lg font-medium text-white tracking-widest uppercase">Initialzing...</p>
                                    </div>
                                </div>
                            )}

                            {/* No Pipeline Selected Overlay (for logged in users) */}
                            {!pipelineId && isAuthenticated && !loading && (
                                <div className="absolute inset-0 z-40 bg-zinc-950/90 flex items-center justify-center p-6">
                                    <div className="max-w-md w-full bg-zinc-900 border border-white/10 rounded-3xl p-8 shadow-2xl">
                                        <h2 className="text-2xl font-bold mb-2">Select a Workspace</h2>
                                        <p className="text-zinc-500 mb-8 text-sm">Choose a recent pipeline to visualize or start a new analysis.</p>

                                        <div className="space-y-3 max-h-60 overflow-y-auto mb-8 pr-2 custom-scrollbar">
                                            {fetchingPipelines ? (
                                                <div className="py-8 flex justify-center"><Loader2 className="animate-spin text-amber-500" /></div>
                                            ) : pipelines.length > 0 ? (
                                                pipelines.map(p => (
                                                    <button
                                                        key={p.id}
                                                        onClick={() => router.push(`/visualizer?pipeline_id=${p.id}`)}
                                                        className="w-full p-4 rounded-xl border border-white/5 bg-white/5 hover:bg-white/10 hover:border-white/20 transition-all text-left flex items-center justify-between group"
                                                    >
                                                        <div>
                                                            <div className="font-medium text-white group-hover:text-amber-500 transition-colors">{p.name}</div>
                                                            <div className="text-[10px] text-zinc-500 font-mono mt-1 uppercase italic">{p.status} • Updated {new Date(p.updated_at).toLocaleDateString()}</div>
                                                        </div>
                                                        <ArrowRight className="h-4 w-4 text-zinc-600 group-hover:text-white group-hover:translate-x-1 transition-all" />
                                                    </button>
                                                ))
                                            ) : (
                                                <div className="py-8 text-center text-zinc-500 italic text-sm">No personal pipelines found.</div>
                                            )}
                                        </div>

                                        <div className="flex flex-col gap-3">
                                            <Link href="/analyze" className="w-full h-12 rounded-full bg-amber-500 text-black font-bold flex items-center justify-center hover:bg-amber-600 transition-colors">
                                                Start New Analysis
                                            </Link>
                                            <button
                                                onClick={() => {
                                                    // Load demo data anyway if they insist
                                                    setDocName('Demo Document')
                                                    setChunks(MOCK_CHUNKS)
                                                }}
                                                className="text-xs text-zinc-500 hover:text-white transition-colors"
                                            >
                                                Continue with Demo Preview
                                            </button>
                                        </div>
                                    </div>
                                </div>
                            )}

                            <ChunkVisualizer
                                pdfUrl={pdfUrl}
                                initialChunks={chunks}
                                scale={1.2}
                            />
                        </div>
                    </section>

                    {selectedChunk && (
                        <ChunkDetailPanel
                            chunk={selectedChunk}
                            onClose={() => setSelectedChunk(null)}
                        />
                    )}
                </main>
            </div>
        </AuthGuard>
    )
}
