"use client"

import { BaseNode } from './base-node'
import { Search } from 'lucide-react'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Label } from '@/components/ui/label'
import { Slider } from '@/components/ui/slider'

export function RetrievalNode({ data, selected }: any) {
    return (
        <BaseNode
            label={data.label || 'Retrieval'}
            icon={<Search className="w-4 h-4" />}
            selected={selected}
            inputs={1}
            outputs={1}
            className="border-cyan-900/50"
        >
            <div className="flex flex-col gap-3 min-w-[180px]">
                <div className="flex flex-col gap-1.5">
                    <Label className="text-[10px] uppercase text-neutral-500 font-bold">Search Type</Label>
                    <Select defaultValue="semantic">
                        <SelectTrigger className="h-8 bg-black/40 border-white/5 text-xs">
                            <SelectValue placeholder="Type" />
                        </SelectTrigger>
                        <SelectContent className="bg-neutral-900 border-white/10 text-white text-xs">
                            <SelectItem value="semantic">Semantic (Vector)</SelectItem>
                            <SelectItem value="keyword">Keyword (BM25)</SelectItem>
                            <SelectItem value="hybrid">Hybrid</SelectItem>
                        </SelectContent>
                    </Select>
                </div>

                <div className="flex flex-col gap-1.5">
                    <div className="flex justify-between items-center">
                        <Label className="text-[10px] uppercase text-neutral-500 font-bold">Top K</Label>
                        <span className="text-[10px] text-cyan-400 font-mono">5</span>
                    </div>
                    <Slider defaultValue={[5]} max={20} step={1} className="py-2" />
                </div>
            </div>
        </BaseNode>
    )
}
