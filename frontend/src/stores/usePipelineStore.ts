import { create } from 'zustand';
import {
    Node,
    Edge,
    applyNodeChanges,
    applyEdgeChanges,
    NodeChange,
    EdgeChange,
    Connection,
    addEdge
} from 'reactflow';

interface PipelineState {
    nodes: Node[];
    edges: Edge[];
    history: { nodes: Node[]; edges: Edge[] }[];
    future: { nodes: Node[]; edges: Edge[] }[];

    // Actions
    setNodes: (nodes: Node[]) => void;
    setEdges: (edges: Edge[]) => void;
    onNodesChange: (changes: NodeChange[]) => void;
    onEdgesChange: (changes: EdgeChange[]) => void;
    onConnect: (connection: Connection) => void;
    addNode: (node: Node) => void;

    // History Actions
    undo: () => void;
    redo: () => void;
    saveHistory: () => void;
}

export const usePipelineStore = create<PipelineState>((set, get) => ({
    nodes: [],
    edges: [],
    history: [],
    future: [],

    saveHistory: () => {
        const { nodes, edges, history } = get();
        // Limit history to 20 steps
        const newHistory = [...history, { nodes, edges }].slice(-20);
        set({ history: newHistory, future: [] });
    },

    setNodes: (nodes) => set({ nodes }),

    setEdges: (edges) => set({ edges }),

    onNodesChange: (changes) => {
        // We only save history for "important" changes? 
        // For simplicity, we save before applying if history is requested,
        // but ReactFlow triggers changes continuously during drag.
        // Usually, we save onDragStop.
        set({
            nodes: applyNodeChanges(changes, get().nodes),
        });
    },

    onEdgesChange: (changes) => {
        set({
            edges: applyEdgeChanges(changes, get().edges),
        });
    },

    onConnect: (connection) => {
        get().saveHistory();
        set({
            edges: addEdge(connection, get().edges),
        });
    },

    addNode: (node) => {
        get().saveHistory();
        set({
            nodes: [...get().nodes, node],
        });
    },

    undo: () => {
        const { history, future, nodes, edges } = get();
        if (history.length === 0) return;

        const previous = history[history.length - 1];
        const newHistory = history.slice(0, history.length - 1);

        set({
            nodes: previous.nodes,
            edges: previous.edges,
            history: newHistory,
            future: [{ nodes, edges }, ...future],
        });
    },

    redo: () => {
        const { history, future, nodes, edges } = get();
        if (future.length === 0) return;

        const next = future[0];
        const newFuture = future.slice(1);

        set({
            nodes: next.nodes,
            edges: next.edges,
            history: [...history, { nodes, edges }],
            future: newFuture,
        });
    },
}));
