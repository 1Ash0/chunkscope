import { defineConfig, configDefaults } from 'vitest/config'
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
        exclude: [
            ...configDefaults.exclude,
            'src/tests/e2e/**',
        ],
        alias: {
            '@': path.resolve(__dirname, './src'),
        },
        deps: {
            optimizer: {
                web: {
                    include: ['html-encoding-sniffer', '@exodus/bytes', '@testing-library/dom'],
                },
            },
        },
        server: {
            deps: {
                inline: ['html-encoding-sniffer', '@exodus/bytes', '@testing-library/dom'],
            },
        },
    },
})
