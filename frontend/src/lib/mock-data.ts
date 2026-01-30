import { Chunk } from '@/stores/useChunkStore';

// Using a reliable, CORS-friendly sample PDF (Mozilla's Tracemonkey or a simple sample)
export const DEMO_PDF_URL = "https://raw.githubusercontent.com/mozilla/pdf.js/ba2edeae/examples/learning/helloworld.pdf";

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
