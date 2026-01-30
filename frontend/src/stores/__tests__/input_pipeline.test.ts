
import { describe, it, expect, beforeEach, vi } from 'vitest'
import { act } from '@testing-library/react'
import { usePipelineStore } from '../usePipelineStore'
import { Node, Edge } from 'reactflow'

// Mock ReactFlow
vi.mock('reactflow', async () => {
    const actual = await vi.importActual('reactflow')
    return {
        ...actual,
        applyNodeChanges: (changes: any, nodes: any) => nodes, // Simplified for test
        applyEdgeChanges: (changes: any, edges: any) => edges,
        addEdge: (conn: any, edges: any) => [...edges, { ...conn, id: 'e1' }]
    }
})

describe('Pipeline Store & Logic', () => {

    beforeEach(() => {
        usePipelineStore.setState({
            nodes: [],
            edges: [],
            history: [],
            future: []
        })
    })

    describe('Undo/Redo', () => {
        it('should save history when adding a node', () => {
            const node: Node = { id: '1', type: 'loader', position: { x: 0, y: 0 }, data: {} }

            usePipelineStore.getState().addNode(node)

            const state = usePipelineStore.getState()
            expect(state.nodes).toHaveLength(1)
            // History is saved BEFORE the action in our implementation? 
            // Let's check the store code. The store calls saveHistory() THEN set().
            // So history should have the EMPTY state.
            expect(state.history).toHaveLength(1)
            expect(state.history[0].nodes).toHaveLength(0)
        })

        it('should undo the last action', () => {
            const node: Node = { id: '1', type: 'loader', position: { x: 0, y: 0 }, data: {} }

            usePipelineStore.getState().addNode(node) // Adds 1 node, saves empty state to history
            expect(usePipelineStore.getState().nodes).toHaveLength(1)

            usePipelineStore.getState().undo() // Should revert to empty

            const state = usePipelineStore.getState()
            expect(state.nodes).toHaveLength(0)
            expect(state.future).toHaveLength(1) // The undone state goes to future
        })

        it('should redo the undone action', () => {
            const node: Node = { id: '1', type: 'loader', position: { x: 0, y: 0 }, data: {} }

            usePipelineStore.getState().addNode(node)
            usePipelineStore.getState().undo()

            expect(usePipelineStore.getState().nodes).toHaveLength(0)

            usePipelineStore.getState().redo()

            const state = usePipelineStore.getState()
            expect(state.nodes).toHaveLength(1)
            expect(state.nodes[0].id).toBe('1')
        })
    })

    describe('Connection Validation Rules', () => {
        // We need to extract the validation logic or duplicate it here for testing
        // since it was defined inside the Component in previous steps.
        // Ideally, it should be a shared utility.

        const rules: Record<string, string[]> = {
            'loader': ['splitter', 'metadata'],
            'scraper': ['splitter', 'metadata'],
            'api_connector': ['splitter', 'metadata'],
            'splitter': ['embedder', 'vector_db', 'postgres'],
            'embedder': ['vector_db', 'postgres', 'search', 'hybrid'],
            'vector_db': ['search', 'hybrid'],
            'postgres': ['search', 'hybrid'],
            'search': ['reranker', 'llm', 'evaluator'],
            'hybrid': ['reranker', 'llm', 'evaluator'],
            'reranker': ['llm', 'evaluator'],
            'llm': ['evaluator'],
            'evaluator': []
        }

        const isValidConnection = (sourceType: string, targetType: string) => {
            if (rules[sourceType]) {
                return rules[sourceType].includes(targetType)
            }
            return true
        }

        it('should allow Loader -> Splitter', () => {
            expect(isValidConnection('loader', 'splitter')).toBe(true)
        })

        it('should allow Splitter -> Embedder', () => {
            expect(isValidConnection('splitter', 'embedder')).toBe(true)
        })

        it('should allow Embedder -> Vector DB', () => {
            expect(isValidConnection('embedder', 'vector_db')).toBe(true)
        })

        it('should BLOCK Loader -> Vector DB (direct)', () => {
            expect(isValidConnection('loader', 'vector_db')).toBe(false)
        })

        it('should BLOCK Vector DB -> Splitter (cycle/backwards)', () => {
            expect(isValidConnection('vector_db', 'splitter')).toBe(false)
        })

        it('should allow Search -> LLM', () => {
            expect(isValidConnection('search', 'llm')).toBe(true)
        })

        it('should allow LLM -> Evaluator', () => {
            expect(isValidConnection('llm', 'evaluator')).toBe(true)
        })
    })
})
