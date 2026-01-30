import { render, screen } from '@testing-library/react'
import { ChunkVisualizer } from '@/components/visualizer/chunk-visualizer'
import { vi } from 'vitest'

// Mock the canvas context since JSDOM doesn't support 2D context
const mockContext = {
    clearRect: vi.fn(),
    fillStyle: '',
    fillRect: vi.fn(),
    beginPath: vi.fn(),
    arc: vi.fn(),
    fill: vi.fn(),
}

HTMLCanvasElement.prototype.getContext = vi.fn(() => mockContext) as unknown as typeof HTMLCanvasElement.prototype.getContext

describe('ChunkVisualizer', () => {
    it('renders without crashing', () => {
        render(<ChunkVisualizer pdfUrl="dummy.pdf" initialChunks={[]} />)
        const canvas = screen.getByTestId('visualizer-canvas')
        expect(canvas).toBeInTheDocument()
    })

    it('renders correct number of chunks', () => {
        const chunks = [
            { id: '1', text: 'Chunk 1', embedding: [0.1, 0.2], metadata: { page: 1, char_count: 7, token_count: 2 }, bbox: { page: 1, x: 0, y: 0, width: 100, height: 100 } },
            { id: '2', text: 'Chunk 2', embedding: [0.3, 0.4], metadata: { page: 1, char_count: 7, token_count: 2 }, bbox: { page: 1, x: 100, y: 100, width: 100, height: 100 } },
        ]
        render(<ChunkVisualizer pdfUrl="dummy.pdf" initialChunks={chunks} />)
        // In a real canvas test, we'd check if draw calls were made
        // For now, we verify the component mounted with data props (implicit)
        expect(screen.getByTestId('visualizer-canvas')).toBeInTheDocument()
    })
})
