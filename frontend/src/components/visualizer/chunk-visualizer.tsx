"use client"

import { useRef, useEffect, useState, useCallback, useMemo } from 'react'
import { Document, Page, pdfjs } from 'react-pdf'
import { useDebouncedCallback } from 'use-debounce'
import { useChunkStore, Chunk } from '@/stores/useChunkStore'
import { generateDistinctColors, isPointInRect } from '@/lib/chunk-utils'
import { Loader2, AlertCircle } from 'lucide-react'

// Initialize PDF.js worker
// Important: This must match the pdfjs-dist version installed
// Hardcoded to 3.11.174 to match react-pdf@7.7.3 dependency
pdfjs.GlobalWorkerOptions.workerSrc = `https://unpkg.com/pdfjs-dist@3.11.174/build/pdf.worker.min.js`;

interface ChunkVisualizerProps {
    pdfUrl: string
    initialChunks?: Chunk[]
    scale?: number
    onPageChange?: (page: number) => void
}

export function ChunkVisualizer({
    pdfUrl,
    initialChunks = [],
    scale = 1.0,
    onPageChange
}: ChunkVisualizerProps) {
    // --- Refs & State ---
    const canvasRef = useRef<HTMLCanvasElement>(null)
    const containerRef = useRef<HTMLDivElement>(null)

    const [numPages, setNumPages] = useState<number>(0)
    const [currentPage, setCurrentPage] = useState<number>(1)
    const [pdfDimensions, setPdfDimensions] = useState<{ width: number, height: number } | null>(null)
    const [isPdfLoaded, setIsPdfLoaded] = useState(false)

    // --- Store Access ---
    const {
        chunks,
        setChunks,
        hoveredChunk,
        selectedChunk,
        setHoveredChunk,
        setSelectedChunk
    } = useChunkStore()


    // --- Auth Token Handling ---
    const fileProp = useMemo(() => {
        const token = typeof window !== 'undefined' ? localStorage.getItem('token') : null
        if (token) {
            return {
                url: pdfUrl,
                httpHeaders: { Authorization: `Bearer ${token}` },
                withCredentials: true
            }
        }
        return pdfUrl
    }, [pdfUrl])

    // --- Initialization ---
    useEffect(() => {
        if (initialChunks.length > 0) {
            setChunks(initialChunks)
        }
    }, [initialChunks, setChunks])

    // --- Color Generation (Memoized) ---
    // We generate colors once based on chunk count to keep them stable
    const chunkColors = useMemo(() => {
        return generateDistinctColors(chunks.length > 0 ? chunks.length : 100)
    }, [chunks.length])

    // --- Canvas Drawing Logic ---
    const drawOverlay = useCallback(() => {
        const canvas = canvasRef.current
        if (!canvas || !pdfDimensions) return

        const ctx = canvas.getContext('2d', { alpha: true })
        if (!ctx) return

        // 1. Setup Canvas Dimensions
        // We match the canvas size to the rendered PDF size
        // Note: react-pdf renders at (original_width * scale) in CSS pixels
        // We need to handle Device Pixel Ratio for sharp rendering
        const dpr = window.devicePixelRatio || 1
        const displayWidth = pdfDimensions.width
        const displayHeight = pdfDimensions.height

        // Set physical pixel size
        canvas.width = displayWidth * dpr
        canvas.height = displayHeight * dpr

        // Set logical CSS size
        canvas.style.width = `${displayWidth}px`
        canvas.style.height = `${displayHeight}px`

        // Scale context to match dpr
        ctx.scale(dpr, dpr)

        // Clear previous frame
        ctx.clearRect(0, 0, displayWidth, displayHeight)

        // 2. Filter Chunks for Current Page
        // Check for either single bbox OR list of bboxes
        const pageChunks = chunks.filter(c =>
            (c.bbox?.page === currentPage) ||
            (c.bboxes?.some(b => b.page === currentPage))
        )

        // 3. Draw Chunks
        pageChunks.forEach((chunk, index) => {
            const color = chunkColors[index % chunkColors.length]
            const isHovered = hoveredChunk?.id === chunk.id
            const isSelected = selectedChunk?.id === chunk.id

            // Gather all boxes to draw for this chunk on this page
            const boxes = []
            if (chunk.bboxes && chunk.bboxes.length > 0) {
                boxes.push(...chunk.bboxes.filter(b => b.page === currentPage))
            } else if (chunk.bbox && chunk.bbox.page === currentPage) {
                boxes.push(chunk.bbox)
            }

            boxes.forEach(box => {
                const x = box.x * scale
                const y = box.y * scale
                const w = box.width * scale
                const h = box.height * scale

                // Fill Phase
                // Use lower opacity for base, higher for hover
                ctx.fillStyle = isHovered ? color.replace(')', ', 0.4)') : color.replace(')', ', 0.15)')
                ctx.fillRect(x, y, w, h)

                // Stroke Phase
                // Thicker stroke for selected
                ctx.lineWidth = isSelected ? 3 : 1
                ctx.strokeStyle = isSelected ? '#ffffff' : color
                ctx.strokeRect(x, y, w, h)

                if (isSelected) {
                    // Double border for visibility
                    ctx.strokeStyle = color
                    ctx.lineWidth = 1
                    ctx.strokeRect(x - 2, y - 2, w + 4, h + 4)
                }
            })
        })

    }, [chunks, currentPage, pdfDimensions, scale, hoveredChunk, selectedChunk, chunkColors])

    // --- Reactive Drawing ---
    // Redraw whenever relevant state changes
    useEffect(() => {
        // Debounce resize or heavy updates if needed, but for <500 chunks direct draw is fine
        drawOverlay()
    }, [drawOverlay])

    // --- Interactions ---

    const handleMouseMove = useCallback((e: React.MouseEvent<HTMLCanvasElement>) => {
        if (!pdfDimensions) return

        const rect = canvasRef.current?.getBoundingClientRect()
        if (!rect) return

        // Mouse Pos in CSS Pixels relative to Canvas
        const mouseX = e.clientX - rect.left
        const mouseY = e.clientY - rect.top

        // Convert to PDF Coordinate Space for Hit Test
        // PDF Point = Screen Pixel / Scale
        const pdfX = mouseX / scale
        const pdfY = mouseY / scale

        // Reverse iterate to find top-most chunk
        const pageChunks = chunks.filter(c =>
            (c.bbox?.page === currentPage) ||
            (c.bboxes?.some(b => b.page === currentPage))
        )
        let found: Chunk | null = null

        for (let i = pageChunks.length - 1; i >= 0; i--) {
            const c = pageChunks[i]
            let isHit = false

            if (c.bboxes && c.bboxes.length > 0) {
                isHit = c.bboxes.some(b =>
                    b.page === currentPage &&
                    pdfX >= b.x && pdfX <= b.x + b.width &&
                    pdfY >= b.y && pdfY <= b.y + b.height
                )
            } else if (c.bbox && c.bbox.page === currentPage) {
                isHit = (
                    pdfX >= c.bbox.x &&
                    pdfX <= c.bbox.x + c.bbox.width &&
                    pdfY >= c.bbox.y &&
                    pdfY <= c.bbox.y + c.bbox.height
                )
            }

            if (isHit) {
                found = c
                break
            }
        }

        if (found?.id !== hoveredChunk?.id) {
            setHoveredChunk(found)
        }
    }, [chunks, currentPage, scale, hoveredChunk, pdfDimensions, setHoveredChunk])

    const handleClick = useCallback(() => {
        if (hoveredChunk) {
            setSelectedChunk(hoveredChunk)
        } else {
            setSelectedChunk(null)
        }
    }, [hoveredChunk, setSelectedChunk])

    const [error, setError] = useState<string | null>(null)

    // --- PDF Event Handlers ---
    function onDocumentLoadSuccess({ numPages }: { numPages: number }) {
        console.log('PDF Load Success. Pages:', numPages)
        setNumPages(numPages)
        setIsPdfLoaded(true)
        setError(null)
    }

    function onDocumentLoadError(err: Error) {
        console.error('PDF Load Error:', err)
        setError(err.message)
        setIsPdfLoaded(true)
    }

    function onPageLoadSuccess(page: any) {
        // Store rendered dimensions to sync canvas
        // page.view is [0, 0, originalWidth, originalHeight]
        setPdfDimensions({
            width: page.view[2] * scale,
            height: page.view[3] * scale
        })
    }

    return (
        <div
            ref={containerRef}
            className="flex-1 w-full bg-neutral-900 border border-neutral-800 rounded-xl overflow-auto shadow-2xl custom-scrollbar relative"
            style={{ minHeight: '100%' }}
        >
            {!isPdfLoaded && (
                <div className="absolute inset-0 flex items-center justify-center text-neutral-500 gap-2">
                    <Loader2 className="animate-spin h-5 w-5" />
                    <span>Loading PDF Pipeline...</span>
                </div>
            )}

            {error && (
                <div className="absolute inset-0 flex items-center justify-center text-red-500 bg-neutral-950/80 z-50 p-12 flex-col gap-6 backdrop-blur-md">
                    <div className="w-16 h-16 rounded-full bg-red-500/10 flex items-center justify-center border border-red-500/20">
                        <AlertCircle className="h-8 w-8 text-red-500" />
                    </div>
                    <div className="text-center max-w-md">
                        <h3 className="text-2xl font-bold text-white mb-2">Failed to Load Document</h3>
                        <p className="text-neutral-400 text-sm mb-6">
                            We couldn't retrieve the document content. This could be due to an expired session or a server-side error.
                        </p>
                        <div className="font-mono text-xs bg-black/50 p-4 rounded-lg border border-red-900/30 text-red-400 break-all mb-8">
                            Error: {error}
                        </div>
                        <button
                            onClick={() => window.location.reload()}
                            className="px-6 py-2 bg-white text-black rounded-full font-semibold hover:bg-neutral-200 transition-colors"
                        >
                            Retry Loading
                        </button>
                    </div>
                </div>
            )}

            <div className="flex justify-center p-8 bg-neutral-900/50 min-h-full">
                <div
                    className="relative shadow-lg bg-white"
                    style={{
                        width: pdfDimensions?.width ? `${pdfDimensions.width}px` : 'auto',
                        height: pdfDimensions?.height ? `${pdfDimensions.height}px` : 'auto'
                    }}
                >
                    <Document
                        file={fileProp}
                        onLoadSuccess={onDocumentLoadSuccess}
                        onLoadError={onDocumentLoadError}
                        className="flex flex-col gap-4 shadow-2xl"
                        loading={
                            <div className="flex items-center justify-center p-24">
                                <Loader2 className="animate-spin h-8 w-8 text-amber-500" />
                            </div>
                        }
                        error={
                            <div className="text-red-500 p-4 text-center">
                                Failed to render PDF.
                            </div>
                        }
                    >
                        <Page
                            pageNumber={currentPage}
                            scale={scale}
                            onLoadSuccess={onPageLoadSuccess}
                            className="bg-white"
                            renderTextLayer={false}
                            renderAnnotationLayer={false}
                            devicePixelRatio={Math.min(2, typeof window !== 'undefined' ? window.devicePixelRatio : 1)}
                        />
                    </Document>

                    {/* Canvas Overlay Layer */}
                    {/* Matches size of PDF Page exactly via absolute positioning */}
                    <canvas
                        ref={canvasRef}
                        data-testid="visualizer-canvas"
                        className="absolute top-0 left-0 w-full h-full cursor-crosshair touch-none"
                        onMouseMove={handleMouseMove}
                        onMouseLeave={() => setHoveredChunk(null)}
                        onClick={handleClick}
                    />
                </div>
            </div>

            {/* Simple Page Controls for Validation Phase */}
            {numPages > 0 && (
                <div className="absolute bottom-4 left-1/2 -translate-x-1/2 flex gap-4 items-center bg-black/80 px-4 py-2 rounded-full border border-white/10 backdrop-blur-md z-20">
                    <button
                        disabled={currentPage <= 1}
                        onClick={() => setCurrentPage(prev => prev - 1)}
                        className="text-white disabled:opacity-30 hover:text-amber-400"
                    >
                        Prev
                    </button>
                    <span className="text-sm font-mono text-neutral-300">
                        Page {currentPage} / {numPages}
                    </span>
                    <button
                        disabled={currentPage >= numPages}
                        onClick={() => setCurrentPage(prev => prev + 1)}
                        className="text-white disabled:opacity-30 hover:text-amber-400"
                    >
                        Next
                    </button>
                </div>
            )}
        </div>
    )
}
