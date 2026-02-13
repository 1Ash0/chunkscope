"use client"

import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Button } from "@/components/ui/button"
import { Scissors, Eye } from 'lucide-react'
import { Handle, Position } from 'reactflow'
import {
    Dialog,
    DialogContent,
    DialogHeader,
    DialogTitle,
    DialogTrigger
} from "@/components/ui/dialog"
import { ChunkingPreview } from "@/components/preview/chunking-preview"
import { usePipelineStore } from '@/stores/usePipelineStore'

export function SplitterNode({ id, data }: { id: string, data: any }) {
    const updateNodeData = usePipelineStore((state) => state.updateNodeData)

    const handleConfigChange = (newConfig: any) => {
        updateNodeData(id, {
            ...data,
            ...newConfig
        })
    }

    return (
        <div className="bg-neutral-900 border-2 border-emerald-500 rounded-lg shadow-xl w-64 overflow-hidden relative group">
            <div className="bg-emerald-500 p-2 flex items-center justify-between text-white">
                <div className="flex items-center gap-2">
                    <Scissors size={14} />
                    <span className="text-xs font-bold uppercase tracking-wider">Splitter Node</span>
                </div>
                <Dialog>
                    <DialogTrigger asChild>
                        <Button variant="ghost" size="icon" className="h-6 w-6 text-white hover:bg-emerald-600 rounded-full">
                            <Eye size={12} />
                        </Button>
                    </DialogTrigger>
                    <DialogContent className="max-w-4xl bg-neutral-950 border-white/10 shadow-2xl">
                        <DialogHeader>
                            <DialogTitle className="flex items-center gap-2 text-emerald-400">
                                <Scissors className="w-5 h-5" />
                                Real-Time Chunking Preview
                            </DialogTitle>
                        </DialogHeader>
                        <ChunkingPreview
                            config={{
                                method: data.method || 'recursive',
                                chunkSize: data.chunkSize || 512,
                                overlap: data.overlap || 50,
                                threshold: data.threshold || 0.5,
                                windowSize: data.windowSize || 1
                            }}
                            onConfigChange={handleConfigChange}
                        />
                    </DialogContent>
                </Dialog>
            </div>

            <div className="p-4 space-y-4">
                <Handle type="target" position={Position.Top} className="w-3 h-3 bg-emerald-500 border-2 border-neutral-900" />

                <div className="space-y-1.5">
                    <Label className="text-[10px] uppercase font-bold text-neutral-500">Method</Label>
                    <Select
                        value={data.method || 'recursive'}
                        onValueChange={(value) => updateNodeData(id, { method: value })}
                    >
                        <SelectTrigger className="h-8 text-xs bg-black/40 border-white/10 text-neutral-300 focus:ring-emerald-500/20">
                            <SelectValue placeholder="Select method" />
                        </SelectTrigger>
                        <SelectContent className="bg-neutral-900 border-white/10 text-neutral-300">
                            <SelectItem value="fixed">Fixed Size</SelectItem>
                            <SelectItem value="recursive">Recursive</SelectItem>
                            <SelectItem value="sentence">Sentence</SelectItem>
                            <SelectItem value="paragraph">Paragraph</SelectItem>
                            <SelectItem value="semantic">Semantic (Pro)</SelectItem>
                        </SelectContent>
                    </Select>
                </div>

                <div className="grid grid-cols-2 gap-3">
                    <div className="space-y-1.5">
                        <Label className="text-[10px] uppercase font-bold text-neutral-500">
                            {data.method === 'sentence_window' ? 'Window' : 'Size'}
                        </Label>
                        <Input
                            type="number"
                            className="h-8 text-xs bg-black/40 border-white/10 text-neutral-300 focus:ring-emerald-500/20"
                            value={data.windowSize || data.chunkSize || 512}
                            onChange={(e) => {
                                const val = parseInt(e.target.value) || 0
                                updateNodeData(id, {
                                    windowSize: val,
                                    chunkSize: val
                                })
                            }}
                        />
                    </div>
                    <div className="space-y-1.5">
                        <Label className="text-[10px] uppercase font-bold text-neutral-500">Overlap</Label>
                        <Input
                            type="number"
                            className="h-8 text-xs bg-black/40 border-white/10 text-neutral-300 focus:ring-emerald-500/20"
                            value={data.overlap || 0}
                            onChange={(e) => updateNodeData(id, { overlap: parseInt(e.target.value) || 0 })}
                        />
                    </div>
                </div>

                <Handle type="source" position={Position.Bottom} className="w-3 h-3 bg-emerald-500 border-2 border-neutral-900" />
            </div>
        </div>
    )
}
