"use client"

import { useCallback, useState, useEffect } from 'react'
import ReactFlow, {
    Background,
    Controls,
    MiniMap,
    NodeTypes,
    Node,
} from 'reactflow'
import 'reactflow/dist/style.css'
import { PipelineToolbar } from './pipeline-toolbar'
import { LoaderNode } from './nodes/loader-node'
import { SplitterNode } from './nodes/splitter-node'
import { EmbedderNode } from './nodes/embedder-node'
import { StorageNode } from './nodes/storage-node'
import { RetrievalNode } from './nodes/retrieval-node'
import { GenerationNode } from './nodes/generation-node'
import { usePipelineStore } from '@/stores/usePipelineStore'

// Define Custom Node Types
const nodeTypes: NodeTypes = {
    // Data Sources
    loader: LoaderNode,
    scraper: LoaderNode,
    api_connector: LoaderNode,

    // Processing
    splitter: SplitterNode,
    embedder: EmbedderNode,
    metadata: SplitterNode,

    // Storage
    vector_db: StorageNode,
    postgres: StorageNode,

    // Retrieval
    search: RetrievalNode,
    hybrid: RetrievalNode,

    // Augmentation
    reranker: RetrievalNode,
    hyde: RetrievalNode,

    // Generation
    llm: GenerationNode,

    // Evaluation
    evaluator: GenerationNode
}

export function PipelineBuilder() {
    const {
        nodes,
        edges,
        onNodesChange,
        onEdgesChange,
        onConnect,
        addNode,
        saveHistory
    } = usePipelineStore()

    const [reactFlowInstance, setReactFlowInstance] = useState<any>(null)

    const onDragOver = useCallback((event: React.DragEvent) => {
        event.preventDefault()
        event.dataTransfer.dropEffect = 'move'
    }, [])

    const onDrop = useCallback(
        (event: React.DragEvent) => {
            event.preventDefault()

            if (!reactFlowInstance) return

            const type = event.dataTransfer.getData('application/reactflow')

            if (typeof type === 'undefined' || !type) {
                return
            }

            const position = reactFlowInstance.screenToFlowPosition({
                x: event.clientX,
                y: event.clientY,
            })

            const newNode: Node = {
                id: `${type}-${Date.now()}`,
                type,
                position,
                data: { label: `${type.charAt(0).toUpperCase() + type.slice(1)}` },
            }

            addNode(newNode)
        },
        [reactFlowInstance, addNode]
    )

    // Save history when a node interaction finishes
    const onNodeDragStop = useCallback(() => {
        saveHistory()
    }, [saveHistory])

    const isValidConnection = useCallback((connection: any) => {
        const sourceNode = nodes.find(n => n.id === connection.source)
        const targetNode = nodes.find(n => n.id === connection.target)

        if (!sourceNode || !targetNode) return false

        const sourceType = sourceNode.type
        const targetType = targetNode.type

        // Rule definitions
        const rules: Record<string, string[]> = {
            'loader': ['splitter', 'metadata', 'llm'],
            'scraper': ['splitter', 'metadata', 'llm'],
            'api_connector': ['splitter', 'metadata', 'llm'],
            'splitter': ['embedder', 'vector_db', 'postgres', 'llm'],
            'embedder': ['vector_db', 'postgres', 'search', 'hybrid', 'llm'],
            'vector_db': ['search', 'hybrid'],
            'postgres': ['search', 'hybrid'],
            'search': ['reranker', 'llm', 'evaluator'],
            'hybrid': ['reranker', 'llm', 'evaluator'],
            'reranker': ['llm', 'evaluator'],
            'llm': ['evaluator'],
            'evaluator': []
        }

        if (sourceType && rules[sourceType]) {
            return rules[sourceType].includes(targetType as string)
        }

        return true // Default for unknown types
    }, [nodes])

    return (
        <div className="w-full h-full flex flex-col">
            <div className="flex-1 w-full h-full relative">
                <ReactFlow
                    nodes={nodes}
                    edges={edges}
                    onNodesChange={onNodesChange}
                    onEdgesChange={onEdgesChange}
                    onConnect={onConnect}
                    onInit={setReactFlowInstance}
                    onDrop={onDrop}
                    onDragOver={onDragOver}
                    onNodeDragStop={onNodeDragStop}
                    isValidConnection={isValidConnection}
                    nodeTypes={nodeTypes}
                    fitView
                    className="bg-neutral-950"
                >
                    <Background color="#222" gap={16} />
                    <Controls className="bg-white/5 border-white/10 text-white" />
                    <MiniMap className="bg-neutral-900 border-white/10" />
                </ReactFlow>

                {/* Overlay Toolbar */}
                <div className="absolute top-4 left-4 z-10 bottom-4">
                    <PipelineToolbar />
                </div>
            </div>
        </div>
    )
}
