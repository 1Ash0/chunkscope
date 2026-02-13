import { create } from 'zustand';
import { persist } from 'zustand/middleware';

export type ChunkingMethod = 'fixed' | 'semantic' | 'recursive' | 'sentence_window' | 'paragraph' | 'code_aware' | 'heading_based';

interface ConfigStore {
    // Parameters
    method: ChunkingMethod;
    chunkSize: number;
    overlap: number;
    threshold: number; // For semantic chunking

    // State
    selectedDocId: string | null;
    selectedPipelineId: string | null;

    // Actions
    setSelectedDocId: (id: string | null) => void;
    setSelectedPipelineId: (id: string | null) => void;
    setMethod: (method: ChunkingMethod) => void;
    setChunkSize: (size: number) => void;
    setOverlap: (overlap: number) => void;
    setThreshold: (threshold: number) => void;
    resetDefaults: () => void;
}

export const useConfigStore = create<ConfigStore>()(
    persist(
        (set) => ({
            method: 'semantic',
            chunkSize: 512,
            overlap: 50,
            threshold: 0.5,
            selectedDocId: null,
            selectedPipelineId: null,

            setMethod: (method) => set({ method }),
            setChunkSize: (chunkSize) => set({ chunkSize }),
            setOverlap: (overlap) => set({ overlap }),
            setThreshold: (threshold) => set({ threshold }),
            setSelectedDocId: (selectedDocId) => set({ selectedDocId }),
            setSelectedPipelineId: (selectedPipelineId) => set({ selectedPipelineId }),
            resetDefaults: () => set({
                method: 'semantic',
                chunkSize: 512,
                overlap: 50,
                threshold: 0.5,
                // We might want to keep selection on reset, but for now resetting everything is safer
                selectedDocId: null,
                selectedPipelineId: null
            })
        }),
        {
            name: 'chunkscope-config',
            // Optional: Filter what to persist if needed
            // partialize: (state) => ({ method: state.method, ... })
        }
    )
);
