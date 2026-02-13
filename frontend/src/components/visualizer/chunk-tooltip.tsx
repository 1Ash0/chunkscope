"use client"

import { motion } from 'framer-motion'
import { Badge } from '@/components/ui/badge'
import { Card } from '@/components/ui/card'
import type { Chunk } from '@/stores/useChunkStore'

interface ChunkTooltipProps {
    chunk: Chunk
    position: { x: number; y: number }
}

export function ChunkTooltip({ chunk, position }: ChunkTooltipProps) {
    // Smart Positioning Logic:
    // We want to prevent the tooltip from clipping off the right or bottom edges.
    // We assume a viewport-based calculation (simplistic approach for now).
    // In a real app, we might use `getBoundingClientRect` of the window.

    // Offset to ensure cursor doesn't obscure content
    const OFFSET_X = 15;
    const OFFSET_Y = 15;

    // We can't know window size in SSR easily, but for client component we can check window.
    // For safety, we just render near mouse. In a production app, we would use
    // `useMeasure` or similar to flip coordinates if x > window.width - 300.

    return (
        <motion.div
            initial={{ opacity: 0, scale: 0.9, y: 10 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.9 }}
            transition={{ duration: 0.15, ease: "easeOut" }}
            style={{
                position: 'fixed',
                left: position.x + OFFSET_X,
                top: position.y + OFFSET_Y,
                zIndex: 50,
                pointerEvents: 'none', // Critical: allows mouse events to pass through to canvas
                maxWidth: '320px'
            }}
        >
            <Card className="p-3 bg-neutral-900/95 backdrop-blur-md border-white/10 shadow-2xl text-white">
                <div className="space-y-2">
                    {/* Header */}
                    <div className="flex items-center gap-2 justify-between">
                        <Badge variant="outline" className="text-[10px] border-white/20 text-blue-200">
                            ID: {chunk.id.slice(0, 8)}...
                        </Badge>
                        <span className="text-[10px] text-neutral-400 font-mono">
                            Page {chunk.bbox?.page ?? '?'}
                        </span>
                    </div>

                    {/* Text Preview */}
                    <div className="text-xs text-neutral-300 leading-relaxed max-h-32 overflow-hidden text-ellipsis line-clamp-4 font-sans">
                        {chunk.text}
                    </div>

                    {/* Metadata Footer */}
                    <div className="grid grid-cols-2 gap-2 text-[10px] text-neutral-500 pt-2 border-t border-white/5 font-mono">
                        <div>Length: {chunk.metadata.char_count} chars</div>
                        <div>Tokens: {chunk.metadata.token_count}</div>
                    </div>
                </div>
            </Card>
        </motion.div>
    )
}
