import React from 'react'
import { render, screen } from '@testing-library/react'
import { vi, describe, it, expect } from 'vitest'
import { ReactFlowProvider } from 'reactflow'
import { LoaderNode } from '../components/pipeline/nodes/loader-node'
import { SplitterNode } from '../components/pipeline/nodes/splitter-node'
import { EmbedderNode } from '../components/pipeline/nodes/embedder-node'

// Mock reactflow components used in nodes
vi.mock('reactflow', async () => {
    const actual = await vi.importActual('reactflow')
    return {
        ...actual as any,
        Handle: () => <div data-testid="handle" />,
        Position: { Top: 'top', Bottom: 'bottom', Left: 'left', Right: 'right' }
    }
})

describe('Pipeline Builder Nodes', () => {
    const mockData = { label: 'Test Node' }

    it('renders LoaderNode', () => {
        render(
            <ReactFlowProvider>
                <LoaderNode data={mockData} isConnectable={true} />
            </ReactFlowProvider>
        )
        expect(screen.getByText(/Document Loader/i)).toBeInTheDocument()
        expect(screen.getAllByTestId('handle')).toHaveLength(1) // Output only
    })

    it('renders SplitterNode', () => {
        render(
            <ReactFlowProvider>
                <SplitterNode data={mockData} isConnectable={true} />
            </ReactFlowProvider>
        )
        expect(screen.getByText(/Text Splitter/i)).toBeInTheDocument()
        expect(screen.getAllByTestId('handle')).toHaveLength(2) // Input and Output
    })

    it('renders EmbedderNode', () => {
        render(
            <ReactFlowProvider>
                <EmbedderNode data={mockData} isConnectable={true} />
            </ReactFlowProvider>
        )
        expect(screen.getByText(/Embedding Model/i)).toBeInTheDocument()
        expect(screen.getAllByTestId('handle')).toHaveLength(2) // Input and Output (looking at code, it has both)
    })
})
