import { Chunk } from '@/stores/useChunkStore';

// Using a reliable, CORS-friendly sample PDF (Mozilla's Tracemonkey or a simple sample)
// Local demo PDF served by backend to avoid CORS issues
export const DEMO_PDF_URL = "http://localhost:8000/static/demo.pdf";

export const MOCK_CHUNKS: Chunk[] = [
    {
        id: "chunk_1",
        text: "Hello, world!",
        bbox: {
            page: 1,
            x: 50,
            y: 50,
            width: 500, // Large box to cover the text area
            height: 500
        },
        metadata: {
            char_count: 13,
            token_count: 3,
            section: "Greeting"
        }
    }
];
