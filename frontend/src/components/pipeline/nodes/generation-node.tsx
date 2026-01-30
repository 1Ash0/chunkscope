"use client"

import { BaseNode } from './base-node'
import { MessageSquare } from 'lucide-react'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Label } from '@/components/ui/label'
import { Input } from '@/components/ui/input'

export function GenerationNode({ data, selected }: any) {
    return (
        <BaseNode
            label={data.label || 'Generator'}
            icon={<MessageSquare className="w-4 h-4" />}
            selected={selected}
            inputs={1}
            outputs={1}
            className="border-red-900/50"
        >
            <div className="flex flex-col gap-3 min-w-[200px]">
                <div className="flex flex-col gap-1">
                    <Label className="text-[10px] uppercase text-neutral-500 font-bold">API Key (OpenAI)</Label>
                    <Input
                        type="password"
                        className="h-6 text-[10px] bg-black/40 border-white/10"
                        placeholder="sk-..."
                        defaultValue={data.apiKey || ""}
                        onChange={(e) => data.apiKey = e.target.value}
                    />
                </div>
                <div className="flex flex-col gap-1.5">
                    <Label className="text-[10px] uppercase text-neutral-500 font-bold">Model</Label>
                    <Select defaultValue="gpt-4o">
                        <SelectTrigger className="h-8 bg-black/40 border-white/5 text-xs">
                            <SelectValue placeholder="Model" />
                        </SelectTrigger>
                        <SelectContent className="bg-neutral-900 border-white/10 text-white text-xs">
                            <SelectItem value="gpt-4o">GPT-4o</SelectItem>
                            <SelectItem value="claude-3-5">Claude 3.5 Sonnet</SelectItem>
                            <SelectItem value="llama-3">Llama 3 (Groq)</SelectItem>
                        </SelectContent>
                    </Select>
                </div>

                <div className="flex flex-col gap-1.5">
                    <Label className="text-[10px] uppercase text-neutral-500 font-bold">System Prompt</Label>
                    <textarea
                        className="text-[11px] px-2 py-1.5 rounded bg-black/40 border border-white/5 text-neutral-300 min-h-[60px] resize-none focus:outline-none focus:border-white/20"
                        placeholder="You are a helpful assistant..."
                        defaultValue={data.systemPrompt || "You are a helpful assistant. Use the context provided to answer the user's question."}
                        onChange={(e) => data.systemPrompt = e.target.value}
                    />
                </div>
            </div>
        </BaseNode>
    )
}
