"use client"

import { useState, useEffect, useMemo } from 'react'
import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Badge } from '@/components/ui/badge'
import {
    Scissors,
    Text as TextIcon,
    BarChart3,
    Layers,
    RefreshCcw,
    ChevronRight,
    Search
} from 'lucide-react'
import { cn } from '@/lib/utils'
import { useDebounce } from 'use-debounce'

interface Chunk {
    id: string
    text: string
    start: number
    end: number
    metadata: any
}

interface ChunkingPreviewProps {
    initialText?: string
    config: {
        method: string
        chunkSize: number
        overlap: number
        threshold?: number
        windowSize?: number
    }
    onConfigChange?: (config: any) => void
}

const SAMPLE_TEXT = `Artificial intelligence (AI) is intelligence demonstrated by machines, as opposed to natural intelligence displayed by animals including humans. AI research has been defined as the field of study of intelligent agents, which refers to any system that perceives its environment and takes actions that maximize its chance of achieving its goals.

The term "artificial intelligence" had previously been used to describe machines that mimic and display "human" cognitive skills that are associated with the human mind, such as "learning" and "problem-solving". This definition has since been rejected by major AI researchers who now describe AI in terms of rationality and acting rationally, which does not limit how intelligence can be articulated.

AI applications include advanced web search engines (e.g., Google Search), recommendation systems (used by YouTube, Amazon, and Netflix), understanding human speech (such as Siri and Alexa), self-driving cars (e.g., Waymo), generative or creative tools (ChatGPT and AI art), and competing at the highest level in strategic games (such as chess and Go).`

export function ChunkingPreview({ initialText = SAMPLE_TEXT, config, onConfigChange }: ChunkingPreviewProps) {
    const [text, setText] = useState(initialText)
    const [localConfig, setLocalConfig] = useState(config)
    const [chunks, setChunks] = useState<Chunk[]>([])
    const [metrics, setMetrics] = useState<any>(null)
    const [isLoading, setIsLoading] = useState(false)
    const [debouncedText] = useDebounce(text, 500)
    const [debouncedConfig] = useDebounce(localConfig, 300)

    useEffect(() => {
        const fetchPreview = async () => {
            setIsLoading(true)
            try {
                const baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
                const response = await fetch(`${baseUrl}/api/v1/preview/chunking`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        text: debouncedText,
                        config: {
                            method: debouncedConfig.method,
                            chunk_size: debouncedConfig.windowSize || debouncedConfig.chunkSize || 512,
                            overlap: debouncedConfig.overlap || 0,
                            threshold: debouncedConfig.threshold || 0.5,
                            window_size: debouncedConfig.windowSize || 1
                        }
                    })
                })
                const data = await response.json()
                if (response.ok) {
                    setChunks(data.chunks)
                    setMetrics(data.metrics)
                }
            } catch (error) {
                console.error('Failed to fetch preview:', error)
            } finally {
                setIsLoading(false)
            }
        }

        fetchPreview()
    }, [debouncedText, debouncedConfig])

    // Generate highlighted view
    const highlightedContent = useMemo(() => {
        if (!chunks.length) return text

        const elements = []
        let lastIndex = 0

        // In a real highlight view, we need to handle overlaps.
        // For simplicity, we'll assume non-overlapping or just show boundaries.
        // To handle overlaps well, we actually need to stack layers.

        // Simple non-overlapping highlight logic for now
        const sortedChunks = [...chunks].sort((a, b) => a.start - b.start)

        sortedChunks.forEach((chunk, i) => {
            // Text before chunk
            if (chunk.start > lastIndex) {
                elements.push(text.slice(lastIndex, chunk.start))
            }

            // The chunk itself
            const colors = [
                'bg-blue-500/20 border-blue-500/30',
                'bg-emerald-500/20 border-emerald-500/30',
                'bg-amber-500/20 border-amber-500/30',
                'bg-purple-500/20 border-purple-500/30',
                'bg-pink-500/20 border-pink-500/30',
                'bg-cyan-500/20 border-cyan-500/30',
            ]

            elements.push(
                <span
                    key={chunk.id}
                    className={cn(
                        "px-0.5 rounded-sm border transition-all cursor-pointer hover:brightness-125",
                        colors[i % colors.length]
                    )}
                    title={`Chunk ${i + 1}: ${chunk.end - chunk.start} chars`}
                >
                    {text.slice(chunk.start, chunk.end)}
                </span>
            )
            lastIndex = chunk.end
        })

        if (lastIndex < text.length) {
            elements.push(text.slice(lastIndex))
        }

        return elements
    }, [chunks, text])

    return (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 h-[70vh] min-h-0">
            {/* Left: Input & Controls */}
            <div className="flex flex-col gap-4 min-h-0 overflow-hidden">
                <div className="flex flex-col gap-2 flex-1 min-h-0">
                    <div className="flex justify-between items-center">
                        <Label className="text-xs font-bold text-neutral-500 uppercase">Input Text</Label>
                        <Button
                            variant="ghost"
                            size="sm"
                            className="h-6 text-[10px]"
                            onClick={() => setText(SAMPLE_TEXT)}
                        >
                            <RefreshCcw className="w-3 h-3 mr-1" /> Reset
                        </Button>
                    </div>
                    <textarea
                        className="flex-1 w-full p-3 bg-black/40 border border-white/10 rounded-md text-sm font-sans focus:outline-none focus:ring-1 focus:ring-blue-500 resize-none text-neutral-300 overflow-y-auto"
                        value={text}
                        onChange={(e) => setText(e.target.value)}
                        placeholder="Paste text here to test chunking..."
                    />
                </div>

                <div className="flex flex-col gap-4 p-4 bg-white/5 border border-white/10 rounded-lg shrink-0">
                    <Label className="text-xs font-bold text-neutral-500 uppercase">Parameters</Label>

                    <div className="grid grid-cols-2 gap-4">
                        <div className="flex flex-col gap-2">
                            <Label className="text-[10px] text-neutral-400">Method</Label>
                            <Badge variant="outline" className="justify-center border-blue-500/30 text-blue-400">
                                {localConfig.method.toUpperCase()}
                            </Badge>
                        </div>
                        <div className="flex flex-col gap-2">
                            <Label className="text-[10px] text-neutral-400">
                                {localConfig.method === 'sentence_window' ? 'Window Size' : 'Chunk Size'}
                            </Label>
                            <Input
                                type="number"
                                className="h-7 text-xs bg-black/40 border-white/10"
                                value={localConfig.windowSize || localConfig.chunkSize || 512}
                                onChange={(e) => {
                                    const val = parseInt(e.target.value) || 0
                                    setLocalConfig(prev => ({ ...prev, chunkSize: val, windowSize: val }))
                                }}
                            />
                        </div>
                    </div>

                    {localConfig.method !== 'paragraph' && (
                        <div className="flex flex-col gap-2">
                            <div className="flex justify-between">
                                <Label className="text-[10px] text-neutral-400">Overlap</Label>
                                <span className="text-[10px] text-neutral-500">{localConfig.overlap} chars</span>
                            </div>
                            <input
                                type="range"
                                min="0"
                                max="200"
                                step="10"
                                className="w-full h-1 bg-white/10 rounded-lg appearance-none cursor-pointer accent-blue-500"
                                value={localConfig.overlap}
                                onChange={(e) => setLocalConfig(prev => ({ ...prev, overlap: parseInt(e.target.value) }))}
                            />
                        </div>
                    )}
                </div>
            </div>

            {/* Right: Preview & Stats */}
            <div className="flex flex-col gap-4 min-h-0 overflow-hidden">
                <div className="grid grid-cols-3 gap-3 shrink-0">
                    <Card className="p-3 bg-black/40 border-white/10 flex flex-col items-center">
                        <span className="text-[10px] uppercase text-neutral-500 font-bold mb-1">Chunks</span>
                        <span className="text-xl font-mono text-blue-400">
                            {isLoading ? "..." : chunks.length}
                        </span>
                    </Card>
                    <Card className="p-3 bg-black/40 border-white/10 flex flex-col items-center">
                        <span className="text-[10px] uppercase text-neutral-500 font-bold mb-1">Avg Size</span>
                        <span className="text-xl font-mono text-emerald-400">
                            {metrics ? Math.round(metrics.avg_chunk_size) : 0}
                        </span>
                    </Card>
                    <Card className="p-3 bg-black/40 border-white/10 flex flex-col items-center">
                        <span className="text-[10px] uppercase text-neutral-500 font-bold mb-1">Time</span>
                        <span className="text-xl font-mono text-amber-400">
                            {metrics ? metrics.processing_time_ms : 0}ms
                        </span>
                    </Card>
                </div>

                <div className="flex-1 flex flex-col bg-black border border-white/10 rounded-md overflow-hidden min-h-0">
                    <div className="px-3 py-2 border-b border-white/10 bg-white/5 flex items-center justify-between shrink-0">
                        <div className="flex items-center gap-2">
                            <Layers className="w-3 h-3 text-neutral-400" />
                            <span className="text-[10px] font-bold text-neutral-400 uppercase tracking-tight">Visual Preview</span>
                        </div>
                        {isLoading && <div className="text-[10px] text-blue-400 animate-pulse">Calculating...</div>}
                    </div>
                    <ScrollArea className="flex-1 p-4 h-full">
                        <div className="whitespace-pre-wrap text-sm font-sans leading-relaxed text-neutral-400">
                            {highlightedContent}
                        </div>
                    </ScrollArea>
                </div>

                <Button
                    variant="secondary"
                    className="w-full bg-blue-600 hover:bg-blue-700 text-white gap-2 h-9 text-xs shrink-0"
                    onClick={() => onConfigChange?.(localConfig)}
                >
                    Apply Configurations
                </Button>
            </div>
        </div>
    )
}
