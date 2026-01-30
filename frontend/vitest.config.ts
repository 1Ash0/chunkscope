import { defineConfig } from 'vitest/config'
import react from '@vitejs/plugin-react'
import path from 'path'
import { fileURLToPath } from 'url'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)

export default defineConfig({
    plugins: [react()],
    test: {
        environment: 'jsdom',
        globals: true,
        setupFiles: ['./vitest.setup.ts'],
        alias: {
            '@': path.resolve(__dirname, './src'),
        },
        // Fix for ERR_REQUIRE_ESM with jsdom/html-encoding-sniffer
        deps: {
            optimizer: {
                web: {
                    include: ['html-encoding-sniffer', '@exodus/bytes'],
                },
            },
        },
        server: {
            deps: {
                inline: ['html-encoding-sniffer', '@exodus/bytes'],
            },
        },
    },
})
