import { create } from 'zustand';

export type ChunkingMethod = 'fixed' | 'semantic' | 'recursive' | 'sentence_window' | 'paragraph' | 'code_aware' | 'heading_based';

interface ConfigStore {
    // Parameters
    method: ChunkingMethod;
    chunkSize: number;
    overlap: number;
    threshold: number; // For semantic chunking

    // Actions
    setMethod: (method: ChunkingMethod) => void;
    setChunkSize: (size: number) => void;
    setOverlap: (overlap: number) => void;
    setThreshold: (threshold: number) => void;
    resetDefaults: () => void;
}

export const useConfigStore = create<ConfigStore>((set) => ({
    method: 'semantic',
    chunkSize: 512,
    overlap: 50,
    threshold: 0.5,

    setMethod: (method) => set({ method }),
    setChunkSize: (chunkSize) => set({ chunkSize }),
    setOverlap: (overlap) => set({ overlap }),
    setThreshold: (threshold) => set({ threshold }),
    resetDefaults: () => set({
        method: 'semantic',
        chunkSize: 512,
        overlap: 50,
        threshold: 0.5
    })
}));
