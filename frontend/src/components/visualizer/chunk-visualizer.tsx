"use client"

import { useRef, useEffect, useState, useCallback, useMemo } from 'react'
import { Document, Page, pdfjs } from 'react-pdf'
import { useDebouncedCallback } from 'use-debounce'
import { useChunkStore, Chunk } from '@/stores/useChunkStore'
import { generateDistinctColors, isPointInRect } from '@/lib/chunk-utils'
import { Loader2 } from 'lucide-react'

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
        const pageChunks = chunks.filter(c => c.bbox.page === currentPage)

        // 3. Draw Chunks
        pageChunks.forEach((chunk, index) => {
            // Coordinate Mapping:
            // chunk.bbox.x/y are in PDF Points (72 DPI)
            // canvas is scaled by `scale` prop

            const x = chunk.bbox.x * scale
            const y = chunk.bbox.y * scale
            const w = chunk.bbox.width * scale
            const h = chunk.bbox.height * scale

            const color = chunkColors[index % chunkColors.length]
            const isHovered = hoveredChunk?.id === chunk.id
            const isSelected = selectedChunk?.id === chunk.id

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
        const pageChunks = chunks.filter(c => c.bbox.page === currentPage)
        let found: Chunk | null = null

        for (let i = pageChunks.length - 1; i >= 0; i--) {
            const c = pageChunks[i]
            if (
                pdfX >= c.bbox.x &&
                pdfX <= c.bbox.x + c.bbox.width &&
                pdfY >= c.bbox.y &&
                pdfY <= c.bbox.y + c.bbox.height
            ) {
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

    // --- PDF Loading Handlers ---

    function onDocumentLoadSuccess({ numPages }: { numPages: number }) {
        console.log('PDF Load Success. Pages:', numPages)
        setNumPages(numPages)
        setIsPdfLoaded(true)
    }

    function onDocumentLoadError(error: Error) {
        console.error('PDF Load Error:', error)
        setIsPdfLoaded(true) // Stop loading spinner so we can see the error message
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
            className="relative bg-neutral-900 border border-neutral-800 rounded-xl overflow-hidden shadow-2xl"
            style={{ minHeight: '600px' }}
        >
            {!isPdfLoaded && (
                <div className="absolute inset-0 flex items-center justify-center text-neutral-500 gap-2">
                    <Loader2 className="animate-spin h-5 w-5" />
                    <span>Loading PDF Pipeline...</span>
                </div>
            )}

            <div className="flex justify-center p-8 bg-neutral-900/50 backdrop-blur-3xl">
                <div className="relative shadow-lg">
                    <Document
                        file={pdfUrl}
                        onLoadSuccess={onDocumentLoadSuccess}
                        onLoadError={onDocumentLoadError}
                        className="flex flex-col gap-4"
                    >
                        <Page
                            pageNumber={currentPage}
                            scale={scale}
                            onLoadSuccess={onPageLoadSuccess}
                            className="bg-white"
                            renderTextLayer={false}
                            renderAnnotationLayer={false}
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
