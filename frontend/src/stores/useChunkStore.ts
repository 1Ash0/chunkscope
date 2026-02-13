import { create } from 'zustand';

export interface Chunk {
    id: string;
    text: string;
    bbox?: {
        page: number;
        x: number;
        y: number;
        width: number;
        height: number;
    } | null;
    bboxes?: {
        page: number;
        x: number;
        y: number;
        width: number;
        height: number;
    }[];
    metadata: {
        char_count: number;
        token_count: number;
        [key: string]: any;
    };
}

interface ChunkStore {
    chunks: Chunk[];
    selectedChunk: Chunk | null;
    hoveredChunk: Chunk | null;

    // Actions
    setChunks: (chunks: Chunk[]) => void;
    setSelectedChunk: (chunk: Chunk | null) => void;
    setHoveredChunk: (chunk: Chunk | null) => void;
    clearChunks: () => void;

    // Computed helpers (could be selectors)
    getChunksByPage: (page: number) => Chunk[];
}

export const useChunkStore = create<ChunkStore>((set, get) => ({
    chunks: [],
    selectedChunk: null,
    hoveredChunk: null,

    setChunks: (chunks) => set({ chunks }),
    setSelectedChunk: (chunk) => set({ selectedChunk: chunk }),
    setHoveredChunk: (chunk) => set({ hoveredChunk: chunk }),
    clearChunks: () => set({ chunks: [], selectedChunk: null, hoveredChunk: null }),

    getChunksByPage: (page: number) => {
        return get().chunks.filter((c) => c.bbox && c.bbox.page === page);
    },
}));
