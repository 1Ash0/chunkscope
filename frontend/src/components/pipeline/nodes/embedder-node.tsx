import { BrainCircuit } from 'lucide-react'
import { BaseNode } from './base-node'
import { NodeProps } from 'reactflow'

export function EmbedderNode({ data, selected }: NodeProps) {
    return (
        <BaseNode
            label="Embedding Model"
            icon={<BrainCircuit className="w-4 h-4" />}
            selected={selected}
            inputs={1}
            outputs={1}
            className="border-purple-500/50"
        >
            <div className="text-xs text-neutral-400">
                <p>Model: <span className="text-purple-400">{data.model || 'OpenAI Ada-002'}</span></p>
                <p>Dim: 1536</p>
            </div>
        </BaseNode>
    )
}
