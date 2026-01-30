import { Scissors } from 'lucide-react'
import { BaseNode } from './base-node'
import { NodeProps } from 'reactflow'
import { Badge } from '@/components/ui/badge'

export function SplitterNode({ data, selected }: NodeProps) {
    return (
        <BaseNode
            label="Text Splitter"
            icon={<Scissors className="w-4 h-4" />}
            selected={selected}
            inputs={1}
            outputs={1}
            className="border-amber-500/50"
        >
            <div className="flex flex-col gap-2">
                <div className="flex justify-between text-xs text-neutral-400">
                    <span>Size:</span>
                    <Badge variant="outline" className="text-[10px] h-5 border-amber-500/30 text-amber-500">
                        {data.chunkSize || 512}
                    </Badge>
                </div>
                <div className="flex justify-between text-xs text-neutral-400">
                    <span>Overlap:</span>
                    <Badge variant="outline" className="text-[10px] h-5 border-amber-500/30 text-amber-500">
                        {data.overlap || 50}
                    </Badge>
                </div>
            </div>
        </BaseNode>
    )
}
