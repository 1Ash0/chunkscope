# ChunkScope Frontend Development Guide
## Building an Interactive, Non-Generic Visual RAG Interface

---

## 🎨 Design Philosophy

**Goal**: Create a stunning, interactive visualization tool that stands out from generic CRUD apps.

**Inspiration Sources**:
- **21st.dev** - Premium shader components and interactive backgrounds
- **Aceternity UI** - Modern, animated React components
- **Magic UI** - Beautiful, performant UI components
- **Framer Motion** - Smooth animations and transitions

**Core Principles**:
1. **Visual Impact First** - Grab attention with shaders and animations
2. **Performance Second** - Maintain 60fps even with complex visualizations
3. **Functionality Third** - Features work smoothly within beautiful UI
4. **Accessibility Always** - Beautiful AND usable by everyone

---

## 📐 Component Architecture

### **Three-Layer Structure**

```
┌─────────────────────────────────────────────┐
│  BACKGROUND LAYER (Shader Components)      │
│  - Animated backgrounds                     │
│  - Particle effects                         │
│  - Gradient animations                      │
└─────────────────────────────────────────────┘
          ↓
┌─────────────────────────────────────────────┐
│  CONTENT LAYER (Interactive UI)             │
│  - PDF Visualizer                           │
│  - Pipeline Builder                         │
│  - Control Panels                           │
└─────────────────────────────────────────────┘
          ↓
┌─────────────────────────────────────────────┐
│  OVERLAY LAYER (Feedback & Effects)         │
│  - Tooltips                                 │
│  - Notifications                            │
│  - Loading states                           │
└─────────────────────────────────────────────┘
```

---

## 🎭 Component Library Setup

### **1. Initialize Project with shadcn/ui**

```bash
# Create Next.js project with TypeScript
npx create-next-app@latest chunkscope-frontend --typescript --tailwind --app

cd chunkscope-frontend

# Initialize shadcn/ui
npx shadcn-ui@latest init

# Configuration prompts:
# - Style: Default
# - Base color: Slate
# - CSS variables: Yes
# - React Server Components: Yes
# - Directory structure:
#   - components: src/components
#   - utils: src/lib
#   - CSS: src/app/globals.css
#   - Tailwind config: tailwind.config.ts
```

### **2. Install Core Dependencies**

```bash
# shadcn/ui components (install as needed)
npx shadcn-ui@latest add button
npx shadcn-ui@latest add card
npx shadcn-ui@latest add dialog
npx shadcn-ui@latest add slider
npx shadcn-ui@latest add tooltip
npx shadcn-ui@latest add tabs
npx shadcn-ui@latest add select
npx shadcn-ui@latest add badge
npx shadcn-ui@latest add separator

# Animation and interaction
npm install framer-motion
npm install @react-spring/web

# PDF handling
npm install react-pdf pdfjs-dist

# 3D rendering (for shaders)
npm install three @types/three

# State management
npm install zustand

# API client
npm install @tanstack/react-query axios

# Icons
npm install lucide-react

# Utilities
npm install clsx tailwind-merge
npm install class-variance-authority
```

### **3. Project Structure**

```
src/
├── app/
│   ├── layout.tsx           # Root layout with providers
│   ├── page.tsx             # Home/landing page
│   ├── visualizer/
│   │   └── page.tsx         # Chunking visualizer page
│   ├── pipeline/
│   │   └── page.tsx         # Pipeline builder page
│   └── globals.css
│
├── components/
│   ├── ui/                  # shadcn/ui components
│   │   ├── button.tsx
│   │   ├── card.tsx
│   │   └── ...
│   │
│   ├── shaders/             # ⭐ Shader background components
│   │   ├── neon-crystal-city.tsx
│   │   ├── shader-animation.tsx
│   │   ├── shader-lines.tsx
│   │   └── atc-shader.tsx
│   │
│   ├── visualizer/          # ⭐ PDF chunk visualization
│   │   ├── chunk-visualizer.tsx
│   │   ├── chunk-overlay.tsx
│   │   ├── chunk-tooltip.tsx
│   │   ├── chunk-detail-panel.tsx
│   │   └── pdf-renderer.tsx
│   │
│   ├── pipeline/            # Pipeline builder components
│   │   ├── pipeline-canvas.tsx
│   │   ├── node-library.tsx
│   │   ├── node-component.tsx
│   │   └── edge-connector.tsx
│   │
│   ├── layout/              # Layout components
│   │   ├── navbar.tsx
│   │   ├── sidebar.tsx
│   │   └── footer.tsx
│   │
│   └── feedback/            # User feedback
│       ├── loading-spinner.tsx
│       ├── error-boundary.tsx
│       └── toast.tsx
│
├── lib/
│   ├── api.ts               # API client
│   ├── utils.ts             # Utility functions
│   └── constants.ts         # App constants
│
├── hooks/
│   ├── useDocuments.ts      # React Query hooks
│   ├── useChunks.ts
│   └── usePipeline.ts
│
├── stores/
│   ├── useChunkStore.ts     # Zustand stores
│   ├── usePipelineStore.ts
│   └── useUIStore.ts
│
└── types/
    ├── chunk.ts
    ├── document.ts
    └── pipeline.ts
```

---

## 🌟 Shader Background Components

### **Component Integration Strategy**

Based on the provided shader components, here's how to integrate them:

#### **1. Neon Crystal City (Landing Page Background)**

**Purpose**: Stunning animated background for home/landing page

**Integration**:
```tsx
// src/app/page.tsx
import NeonCrystalCity from "@/components/shaders/neon-crystal-city"

export default function Home() {
  return (
    <div className="relative min-h-screen">
      {/* Background shader */}
      <div className="fixed inset-0 z-0">
        <NeonCrystalCity 
          cameraSpeed={5}
          tileSize={2}
          className="opacity-80"
        />
      </div>

      {/* Content overlay */}
      <div className="relative z-10 flex flex-col items-center justify-center min-h-screen">
        <h1 className="text-7xl font-bold text-white mb-4">
          ChunkScope
        </h1>
        <p className="text-xl text-white/80 mb-8">
          Visual Debugging for RAG Pipelines
        </p>
        <Button size="lg" asChild>
          <Link href="/visualizer">
            Get Started
          </Link>
        </Button>
      </div>
    </div>
  )
}
```

**Performance Optimization**:
```tsx
// Lazy load shader for better initial load
import dynamic from 'next/dynamic'

const NeonCrystalCity = dynamic(
  () => import('@/components/shaders/neon-crystal-city'),
  { 
    ssr: false,
    loading: () => <div className="w-full h-full bg-black" />
  }
)
```

#### **2. Shader Lines (Visualizer Background)**

**Purpose**: Dynamic animated background for chunking visualizer

**Integration**:
```tsx
// src/app/visualizer/page.tsx
import { ShaderAnimation } from "@/components/shaders/shader-lines"

export default function VisualizerPage() {
  return (
    <div className="relative h-screen">
      {/* Shader background */}
      <div className="absolute inset-0 z-0">
        <ShaderAnimation />
      </div>

      {/* Visualizer content */}
      <div className="relative z-10 h-full">
        <ChunkVisualizer />
      </div>
    </div>
  )
}
```

#### **3. ATC Shader (Pipeline Builder Background)**

**Purpose**: Abstract animated background for pipeline builder

**When to Use**: Pipeline builder page, settings page

---

## 🎨 PDF Chunk Visualization Component

### **Architecture Overview**

```
ChunkVisualizer (Main Component)
├── PDFRenderer (Displays PDF)
│   └── react-pdf integration
├── ChunkOverlay (Renders colored rectangles)
│   ├── Canvas rendering (chosen approach)
│   └── Color generation algorithm
├── ChunkTooltip (Hover information)
│   └── Framer Motion animation
└── ChunkDetailPanel (Selected chunk details)
    └── Slide-in panel with chunk data
```

### **Technical Implementation**

#### **Rendering Strategy Decision**

**Evaluated Options**:
1. **CSS Overlays** - Simple but doesn't scale to 100+ chunks
2. **SVG Overlays** - Good for interaction, slower at scale
3. **Canvas Overlays** ⭐ **CHOSEN** - Best performance for 100+ chunks

**Why Canvas?**
- Direct pixel manipulation (fast)
- Hardware acceleration
- Supports 1000+ chunks without lag
- Can implement custom hit detection
- Offscreen canvas for background processing

#### **Implementation: ChunkVisualizer.tsx**

```tsx
// src/components/visualizer/chunk-visualizer.tsx
"use client"

import { useRef, useEffect, useState, useCallback } from 'react'
import { Document, Page, pdfjs } from 'react-pdf'
import { motion, AnimatePresence } from 'framer-motion'
import { useChunkStore } from '@/stores/useChunkStore'
import { ChunkTooltip } from './chunk-tooltip'
import { ChunkDetailPanel } from './chunk-detail-panel'
import type { Chunk, ChunkVisualizerProps } from '@/types/chunk'

// Configure PDF.js worker
pdfjs.GlobalWorkerOptions.workerSrc = `//cdnjs.cloudflare.com/ajax/libs/pdf.js/${pdfjs.version}/pdf.worker.min.js`

export function ChunkVisualizer({ 
  documentId,
  pdfUrl,
  initialChunks = []
}: ChunkVisualizerProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const containerRef = useRef<HTMLDivElement>(null)
  const pdfContainerRef = useRef<HTMLDivElement>(null)
  
  const [numPages, setNumPages] = useState<number>(0)
  const [currentPage, setCurrentPage] = useState<number>(1)
  const [scale, setScale] = useState<number>(1.5)
  const [hoveredChunk, setHoveredChunk] = useState<Chunk | null>(null)
  const [mousePos, setMousePos] = useState({ x: 0, y: 0 })
  
  const { 
    chunks, 
    selectedChunk, 
    setSelectedChunk,
    setChunks 
  } = useChunkStore()

  // Initialize chunks
  useEffect(() => {
    if (initialChunks.length > 0) {
      setChunks(initialChunks)
    }
  }, [initialChunks, setChunks])

  // Generate distinct colors for chunks
  const generateChunkColors = useCallback((count: number): string[] => {
    const colors: string[] = []
    const goldenRatio = 0.618033988749895
    let hue = Math.random() // Start with random hue
    
    for (let i = 0; i < count; i++) {
      hue += goldenRatio
      hue %= 1
      
      // HSL to ensure perceptually distinct colors
      const saturation = 70 + (i % 3) * 10 // 70-90%
      const lightness = 50 + (i % 2) * 10  // 50-60%
      
      colors.push(`hsl(${hue * 360}, ${saturation}%, ${lightness}%)`)
    }
    
    return colors
  }, [])

  // Draw chunk overlays on canvas
  const drawChunkOverlays = useCallback(() => {
    const canvas = canvasRef.current
    const pdfContainer = pdfContainerRef.current
    
    if (!canvas || !pdfContainer || chunks.length === 0) return

    const ctx = canvas.getContext('2d', { 
      alpha: true,
      desynchronized: true // Performance hint
    })
    if (!ctx) return

    // Match canvas size to PDF container
    const rect = pdfContainer.getBoundingClientRect()
    const dpr = window.devicePixelRatio || 1
    
    canvas.width = rect.width * dpr
    canvas.height = rect.height * dpr
    canvas.style.width = `${rect.width}px`
    canvas.style.height = `${rect.height}px`
    
    ctx.scale(dpr, dpr)
    ctx.clearRect(0, 0, rect.width, rect.height)

    // Generate colors once
    const colors = generateChunkColors(chunks.length)

    // Filter chunks for current page
    const pageChunks = chunks.filter(chunk => 
      chunk.bbox.page === currentPage
    )

    // Draw each chunk
    pageChunks.forEach((chunk, index) => {
      const { x, y, width, height } = chunk.bbox
      
      // Scale coordinates to match PDF rendering scale
      const scaledX = x * scale
      const scaledY = y * scale
      const scaledWidth = width * scale
      const scaledHeight = height * scale

      // Fill with semi-transparent color
      ctx.fillStyle = colors[index % colors.length] + '40' // 25% opacity
      ctx.fillRect(scaledX, scaledY, scaledWidth, scaledHeight)

      // Border
      ctx.strokeStyle = colors[index % colors.length]
      ctx.lineWidth = 2
      ctx.strokeRect(scaledX, scaledY, scaledWidth, scaledHeight)

      // Highlight selected chunk
      if (selectedChunk?.id === chunk.id) {
        ctx.strokeStyle = '#fff'
        ctx.lineWidth = 4
        ctx.strokeRect(
          scaledX - 2, 
          scaledY - 2, 
          scaledWidth + 4, 
          scaledHeight + 4
        )
      }

      // Highlight hovered chunk
      if (hoveredChunk?.id === chunk.id) {
        ctx.fillStyle = colors[index % colors.length] + 'A0' // 63% opacity
        ctx.fillRect(scaledX, scaledY, scaledWidth, scaledHeight)
      }
    })
  }, [chunks, currentPage, scale, selectedChunk, hoveredChunk, generateChunkColors])

  // Redraw on changes
  useEffect(() => {
    drawChunkOverlays()
  }, [drawChunkOverlays])

  // Handle mouse move for hover detection
  const handleMouseMove = useCallback((e: React.MouseEvent<HTMLCanvasElement>) => {
    const canvas = canvasRef.current
    if (!canvas) return

    const rect = canvas.getBoundingClientRect()
    const x = (e.clientX - rect.left) / scale
    const y = (e.clientY - rect.top) / scale

    setMousePos({ x: e.clientX, y: e.clientY })

    // Find hovered chunk
    const pageChunks = chunks.filter(chunk => chunk.bbox.page === currentPage)
    const hovered = pageChunks.find(chunk => {
      const { x: cx, y: cy, width, height } = chunk.bbox
      return x >= cx && x <= cx + width && y >= cy && y <= cy + height
    })

    setHoveredChunk(hovered || null)
  }, [chunks, currentPage, scale])

  // Handle click to select chunk
  const handleClick = useCallback(() => {
    if (hoveredChunk) {
      setSelectedChunk(hoveredChunk)
    }
  }, [hoveredChunk, setSelectedChunk])

  // Handle zoom
  const handleZoom = useCallback((delta: number) => {
    setScale(prev => Math.max(0.5, Math.min(3, prev + delta)))
  }, [])

  return (
    <div ref={containerRef} className="relative w-full h-full bg-gray-900">
      {/* PDF Document */}
      <div ref={pdfContainerRef} className="relative">
        <Document
          file={pdfUrl}
          onLoadSuccess={({ numPages }) => setNumPages(numPages)}
          className="flex justify-center"
        >
          <Page
            pageNumber={currentPage}
            scale={scale}
            renderTextLayer={false}
            renderAnnotationLayer={false}
          />
        </Document>

        {/* Canvas Overlay */}
        <canvas
          ref={canvasRef}
          className="absolute top-0 left-0 pointer-events-auto cursor-pointer"
          onMouseMove={handleMouseMove}
          onClick={handleClick}
          onMouseLeave={() => setHoveredChunk(null)}
        />
      </div>

      {/* Hover Tooltip */}
      <AnimatePresence>
        {hoveredChunk && (
          <ChunkTooltip 
            chunk={hoveredChunk} 
            position={mousePos}
          />
        )}
      </AnimatePresence>

      {/* Detail Panel */}
      <AnimatePresence>
        {selectedChunk && (
          <ChunkDetailPanel 
            chunk={selectedChunk}
            onClose={() => setSelectedChunk(null)}
          />
        )}
      </AnimatePresence>

      {/* Controls */}
      <div className="absolute bottom-4 right-4 flex gap-2 bg-black/50 backdrop-blur-sm rounded-lg p-2">
        <Button
          size="sm"
          variant="ghost"
          onClick={() => handleZoom(-0.2)}
          disabled={scale <= 0.5}
        >
          <ZoomOut className="w-4 h-4" />
        </Button>
        <Button
          size="sm"
          variant="ghost"
          onClick={() => handleZoom(0.2)}
          disabled={scale >= 3}
        >
          <ZoomIn className="w-4 h-4" />
        </Button>
        <Separator orientation="vertical" />
        <Button
          size="sm"
          variant="ghost"
          onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
          disabled={currentPage <= 1}
        >
          <ChevronLeft className="w-4 h-4" />
        </Button>
        <span className="text-white text-sm px-2 flex items-center">
          {currentPage} / {numPages}
        </span>
        <Button
          size="sm"
          variant="ghost"
          onClick={() => setCurrentPage(p => Math.min(numPages, p + 1))}
          disabled={currentPage >= numPages}
        >
          <ChevronRight className="w-4 h-4" />
        </Button>
      </div>
    </div>
  )
}
```

#### **Performance Optimizations**

```tsx
// 1. Use offscreen canvas for heavy operations
const offscreenCanvas = document.createElement('canvas')
const offscreenCtx = offscreenCanvas.getContext('2d')

// 2. Debounce expensive operations
import { useDebouncedCallback } from 'use-debounce'

const debouncedRedraw = useDebouncedCallback(
  () => drawChunkOverlays(),
  100
)

// 3. Virtualization for long documents
const [visiblePages, setVisiblePages] = useState([currentPage])

useEffect(() => {
  // Only render current page ± 1
  setVisiblePages([
    Math.max(1, currentPage - 1),
    currentPage,
    Math.min(numPages, currentPage + 1)
  ])
}, [currentPage, numPages])

// 4. Web Workers for color generation
// src/workers/color-generator.worker.ts
self.onmessage = (e: MessageEvent<number>) => {
  const count = e.data
  const colors = generateColors(count) // Move logic to worker
  self.postMessage(colors)
}

// 5. RequestAnimationFrame for smooth updates
const frameId = useRef<number>()

const smoothUpdate = () => {
  drawChunkOverlays()
  frameId.current = requestAnimationFrame(smoothUpdate)
}

useEffect(() => {
  frameId.current = requestAnimationFrame(smoothUpdate)
  return () => cancelAnimationFrame(frameId.current!)
}, [])
```

#### **Accessibility Features**

```tsx
// src/components/visualizer/chunk-visualizer.tsx

// Add keyboard navigation
useEffect(() => {
  const handleKeyPress = (e: KeyboardEvent) => {
    switch(e.key) {
      case 'ArrowLeft':
        setCurrentPage(p => Math.max(1, p - 1))
        break
      case 'ArrowRight':
        setCurrentPage(p => Math.min(numPages, p + 1))
        break
      case 'Escape':
        setSelectedChunk(null)
        break
      case '+':
      case '=':
        handleZoom(0.2)
        break
      case '-':
        handleZoom(-0.2)
        break
    }
  }

  window.addEventListener('keydown', handleKeyPress)
  return () => window.removeEventListener('keydown', handleKeyPress)
}, [numPages, handleZoom, setSelectedChunk])

// Add ARIA labels
return (
  <div 
    ref={containerRef} 
    className="relative w-full h-full bg-gray-900"
    role="application"
    aria-label="PDF Chunk Visualizer"
    tabIndex={0}
  >
    {/* Screen reader announcements */}
    <div className="sr-only" aria-live="polite">
      {selectedChunk && `Selected chunk ${selectedChunk.id}`}
      {currentPage && `Page ${currentPage} of ${numPages}`}
    </div>
    
    {/* ... rest of component */}
  </div>
)
```

#### **Mobile Responsiveness**

```tsx
// Touch event handling
const handleTouchMove = useCallback((e: React.TouchEvent) => {
  if (e.touches.length === 1) {
    // Single touch - hover simulation
    const touch = e.touches[0]
    const rect = canvasRef.current?.getBoundingClientRect()
    if (!rect) return

    const x = (touch.clientX - rect.left) / scale
    const y = (touch.clientY - rect.top) / scale

    const hovered = chunks.find(chunk => {
      const { x: cx, y: cy, width, height } = chunk.bbox
      return x >= cx && x <= cx + width && y >= cy && y <= cy + height
    })

    setHoveredChunk(hovered || null)
  }
}, [chunks, scale])

const handlePinchZoom = useCallback((e: React.TouchEvent) => {
  if (e.touches.length === 2) {
    // Pinch zoom logic
    const touch1 = e.touches[0]
    const touch2 = e.touches[1]
    
    const distance = Math.hypot(
      touch2.clientX - touch1.clientX,
      touch2.clientY - touch1.clientY
    )

    // Compare with previous distance to determine zoom direction
    // Implementation details...
  }
}, [])

// Responsive canvas sizing
useEffect(() => {
  const handleResize = () => {
    if (window.innerWidth < 768) {
      setScale(1.0) // Smaller scale for mobile
    } else {
      setScale(1.5) // Default for desktop
    }
  }

  window.addEventListener('resize', handleResize)
  handleResize()

  return () => window.removeEventListener('resize', handleResize)
}, [])
```

---

## 🎭 Interactive UI Components

### **ChunkTooltip.tsx**

```tsx
// src/components/visualizer/chunk-tooltip.tsx
"use client"

import { motion } from 'framer-motion'
import { Badge } from '@/components/ui/badge'
import { Card } from '@/components/ui/card'
import type { Chunk } from '@/types/chunk'

interface ChunkTooltipProps {
  chunk: Chunk
  position: { x: number; y: number }
}

export function ChunkTooltip({ chunk, position }: ChunkTooltipProps) {
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      exit={{ opacity: 0, scale: 0.9 }}
      transition={{ duration: 0.15 }}
      style={{
        position: 'fixed',
        left: position.x + 10,
        top: position.y + 10,
        zIndex: 50,
        pointerEvents: 'none'
      }}
    >
      <Card className="p-3 bg-black/90 backdrop-blur-sm border-white/20 max-w-xs">
        <div className="space-y-2">
          <div className="flex items-center gap-2">
            <Badge variant="outline" className="text-xs">
              {chunk.id}
            </Badge>
            <span className="text-xs text-muted-foreground">
              Page {chunk.bbox.page}
            </span>
          </div>
          
          <div className="text-sm text-white/90">
            <p className="line-clamp-2">{chunk.text}</p>
          </div>

          <div className="flex gap-4 text-xs text-muted-foreground">
            <span>{chunk.metadata.char_count} chars</span>
            <span>{chunk.metadata.token_count} tokens</span>
          </div>
        </div>
      </Card>
    </motion.div>
  )
}
```

### **ChunkDetailPanel.tsx**

```tsx
// src/components/visualizer/chunk-detail-panel.tsx
"use client"

import { motion } from 'framer-motion'
import { X, Copy, Check } from 'lucide-react'
import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Separator } from '@/components/ui/separator'
import type { Chunk } from '@/types/chunk'

interface ChunkDetailPanelProps {
  chunk: Chunk
  onClose: () => void
}

export function ChunkDetailPanel({ chunk, onClose }: ChunkDetailPanelProps) {
  const [copied, setCopied] = useState(false)

  const handleCopy = async () => {
    await navigator.clipboard.writeText(chunk.text)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  return (
    <motion.div
      initial={{ x: '100%' }}
      animate={{ x: 0 }}
      exit={{ x: '100%' }}
      transition={{ type: 'spring', damping: 25, stiffness: 200 }}
      className="fixed right-0 top-0 h-full w-96 bg-gray-900 border-l border-white/10 shadow-2xl z-40"
    >
      <div className="flex flex-col h-full">
        {/* Header */}
        <div className="p-4 border-b border-white/10 flex items-center justify-between">
          <h3 className="text-lg font-semibold text-white">Chunk Details</h3>
          <Button
            size="sm"
            variant="ghost"
            onClick={onClose}
            className="text-white/60 hover:text-white"
          >
            <X className="w-4 h-4" />
          </Button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {/* Metadata */}
          <div className="space-y-2">
            <div className="flex items-center gap-2">
              <Badge variant="outline">{chunk.id}</Badge>
              <span className="text-sm text-muted-foreground">
                Page {chunk.bbox.page}
              </span>
            </div>

            <div className="grid grid-cols-2 gap-2 text-sm">
              <div>
                <span className="text-muted-foreground">Characters:</span>
                <span className="ml-2 text-white">
                  {chunk.metadata.char_count}
                </span>
              </div>
              <div>
                <span className="text-muted-foreground">Tokens:</span>
                <span className="ml-2 text-white">
                  {chunk.metadata.token_count}
                </span>
              </div>
              <div>
                <span className="text-muted-foreground">Position:</span>
                <span className="ml-2 text-white">
                  {chunk.start_pos} - {chunk.end_pos}
                </span>
              </div>
            </div>
          </div>

          <Separator />

          {/* Text Content */}
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium text-white">Text</span>
              <Button
                size="sm"
                variant="ghost"
                onClick={handleCopy}
                className="text-xs"
              >
                {copied ? (
                  <>
                    <Check className="w-3 h-3 mr-1" />
                    Copied
                  </>
                ) : (
                  <>
                    <Copy className="w-3 h-3 mr-1" />
                    Copy
                  </>
                )}
              </Button>
            </div>

            <div className="p-3 bg-black/40 rounded-lg text-sm text-white/90 whitespace-pre-wrap font-mono">
              {chunk.text}
            </div>
          </div>

          {/* Bounding Box Info */}
          <div className="space-y-2">
            <span className="text-sm font-medium text-white">Bounding Box</span>
            <div className="p-3 bg-black/40 rounded-lg text-xs font-mono">
              <div>x: {chunk.bbox.x.toFixed(2)}</div>
              <div>y: {chunk.bbox.y.toFixed(2)}</div>
              <div>width: {chunk.bbox.width.toFixed(2)}</div>
              <div>height: {chunk.bbox.height.toFixed(2)}</div>
            </div>
          </div>
        </div>
      </div>
    </motion.div>
  )
}
```

---

## 🎮 Interactive Control Panel

### **ChunkConfigPanel.tsx**

```tsx
// src/components/visualizer/chunk-config-panel.tsx
"use client"

import { useState } from 'react'
import { motion } from 'framer-motion'
import { Settings, Play, Download } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/card'
import { Slider } from '@/components/ui/slider'
import { Select } from '@/components/ui/select'
import { Label } from '@/components/ui/label'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'

export function ChunkConfigPanel() {
  const [chunkSize, setChunkSize] = useState(512)
  const [overlap, setOverlap] = useState(50)
  const [method, setMethod] = useState('semantic')
  const [threshold, setThreshold] = useState(0.5)

  return (
    <motion.div
      initial={{ y: -20, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      className="w-full max-w-md"
    >
      <Card className="p-6 bg-black/40 backdrop-blur-xl border-white/10">
        <div className="flex items-center gap-2 mb-4">
          <Settings className="w-5 h-5 text-white" />
          <h3 className="text-lg font-semibold text-white">
            Chunking Configuration
          </h3>
        </div>

        <Tabs defaultValue="basic" className="w-full">
          <TabsList className="grid w-full grid-cols-2">
            <TabsTrigger value="basic">Basic</TabsTrigger>
            <TabsTrigger value="advanced">Advanced</TabsTrigger>
          </TabsList>

          <TabsContent value="basic" className="space-y-4 mt-4">
            {/* Chunking Method */}
            <div className="space-y-2">
              <Label htmlFor="method" className="text-white">
                Chunking Method
              </Label>
              <Select
                value={method}
                onValueChange={setMethod}
              >
                <option value="fixed">Fixed Size</option>
                <option value="semantic">Semantic</option>
                <option value="recursive">Recursive</option>
                <option value="sentence">Sentence-based</option>
              </Select>
            </div>

            {/* Chunk Size */}
            <div className="space-y-2">
              <Label htmlFor="chunk-size" className="text-white">
                Chunk Size: {chunkSize}
              </Label>
              <Slider
                id="chunk-size"
                min={100}
                max={2000}
                step={50}
                value={[chunkSize]}
                onValueChange={([value]) => setChunkSize(value)}
                className="w-full"
              />
              <div className="flex justify-between text-xs text-muted-foreground">
                <span>100</span>
                <span>2000</span>
              </div>
            </div>

            {/* Overlap */}
            <div className="space-y-2">
              <Label htmlFor="overlap" className="text-white">
                Overlap: {overlap}
              </Label>
              <Slider
                id="overlap"
                min={0}
                max={500}
                step={10}
                value={[overlap]}
                onValueChange={([value]) => setOverlap(value)}
                className="w-full"
              />
            </div>
          </TabsContent>

          <TabsContent value="advanced" className="space-y-4 mt-4">
            {/* Semantic Threshold (only for semantic method) */}
            {method === 'semantic' && (
              <div className="space-y-2">
                <Label htmlFor="threshold" className="text-white">
                  Similarity Threshold: {threshold.toFixed(2)}
                </Label>
                <Slider
                  id="threshold"
                  min={0.1}
                  max={0.9}
                  step={0.05}
                  value={[threshold]}
                  onValueChange={([value]) => setThreshold(value)}
                  className="w-full"
                />
              </div>
            )}

            {/* More advanced options */}
          </TabsContent>
        </Tabs>

        {/* Actions */}
        <div className="flex gap-2 mt-6">
          <Button className="flex-1" size="sm">
            <Play className="w-4 h-4 mr-2" />
            Apply
          </Button>
          <Button variant="outline" size="sm">
            <Download className="w-4 h-4 mr-2" />
            Export
          </Button>
        </div>
      </Card>
    </motion.div>
  )
}
```

---

## 🎬 Animation Patterns

### **Page Transitions**

```tsx
// src/app/layout.tsx
import { AnimatePresence, motion } from 'framer-motion'

const pageVariants = {
  initial: { opacity: 0, y: 20 },
  animate: { opacity: 1, y: 0 },
  exit: { opacity: 0, y: -20 }
}

export default function Template({ children }: { children: React.ReactNode }) {
  return (
    <AnimatePresence mode="wait">
      <motion.div
        variants={pageVariants}
        initial="initial"
        animate="animate"
        exit="exit"
        transition={{ duration: 0.3 }}
      >
        {children}
      </motion.div>
    </AnimatePresence>
  )
}
```

### **Loading States**

```tsx
// src/components/feedback/loading-spinner.tsx
"use client"

import { motion } from 'framer-motion'

export function LoadingSpinner() {
  return (
    <div className="flex items-center justify-center">
      <motion.div
        className="w-12 h-12 border-4 border-white/20 border-t-white rounded-full"
        animate={{ rotate: 360 }}
        transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
      />
    </div>
  )
}

// Skeleton loader for chunks
export function ChunkSkeleton() {
  return (
    <motion.div
      className="space-y-2"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
    >
      {[1, 2, 3, 4, 5].map((i) => (
        <motion.div
          key={i}
          className="h-20 bg-white/5 rounded-lg"
          animate={{
            opacity: [0.5, 1, 0.5]
          }}
          transition={{
            duration: 1.5,
            repeat: Infinity,
            delay: i * 0.1
          }}
        />
      ))}
    </motion.div>
  )
}
```

---

## 🌐 State Management

### **Zustand Store for Chunks**

```tsx
// src/stores/useChunkStore.ts
import { create } from 'zustand'
import type { Chunk } from '@/types/chunk'

interface ChunkStore {
  chunks: Chunk[]
  selectedChunk: Chunk | null
  hoveredChunk: Chunk | null
  
  setChunks: (chunks: Chunk[]) => void
  setSelectedChunk: (chunk: Chunk | null) => void
  setHoveredChunk: (chunk: Chunk | null) => void
  
  clearChunks: () => void
}

export const useChunkStore = create<ChunkStore>((set) => ({
  chunks: [],
  selectedChunk: null,
  hoveredChunk: null,
  
  setChunks: (chunks) => set({ chunks }),
  setSelectedChunk: (chunk) => set({ selectedChunk: chunk }),
  setHoveredChunk: (chunk) => set({ hoveredChunk: chunk }),
  
  clearChunks: () => set({ 
    chunks: [], 
    selectedChunk: null, 
    hoveredChunk: null 
  })
}))
```

---

## 📱 Responsive Design Strategy

### **Breakpoints**

```tsx
// tailwind.config.ts
export default {
  theme: {
    screens: {
      'sm': '640px',
      'md': '768px',
      'lg': '1024px',
      'xl': '1280px',
      '2xl': '1536px',
    }
  }
}

// Usage in components
<div className="
  w-full h-screen          // Mobile: full screen
  md:w-3/4 md:h-auto       // Tablet: 75% width
  lg:w-2/3 lg:max-w-5xl    // Desktop: 66% width, max 5xl
">
```

### **Mobile-First Approach**

```tsx
// Hide complex features on mobile
<div className="hidden md:block">
  <ShaderAnimation /> {/* Too heavy for mobile */}
</div>

// Simplified mobile version
<div className="block md:hidden">
  <div className="bg-gradient-to-br from-blue-900 to-purple-900" />
</div>

// Touch-friendly controls
<Button 
  size="lg"              // Larger on all screens
  className="
    min-h-[48px]         // Touch target size (accessibility)
    md:min-h-[40px]      // Smaller on desktop
  "
>
  Apply
</Button>
```

---

## 🎯 Performance Budget

### **Target Metrics**

```
Metric                    Target       Measurement
─────────────────────────────────────────────────────
First Contentful Paint    < 1.5s       Lighthouse
Largest Contentful Paint  < 2.5s       Lighthouse
Time to Interactive       < 3.5s       Lighthouse
Cumulative Layout Shift   < 0.1        Lighthouse
First Input Delay         < 100ms      Lighthouse

Canvas Render Time        < 16ms       Custom (60fps)
Chunk Overlay Update      < 33ms       Custom (30fps acceptable)
PDF Page Load             < 1s         Custom
```

### **Monitoring**

```tsx
// src/lib/performance.ts
export function measurePerformance(name: string, fn: () => void) {
  const start = performance.now()
  fn()
  const end = performance.now()
  
  console.log(`[Perf] ${name}: ${(end - start).toFixed(2)}ms`)
  
  // Send to analytics in production
  if (process.env.NODE_ENV === 'production') {
    // analytics.track('performance', { name, duration: end - start })
  }
}

// Usage
measurePerformance('chunk-overlay-render', () => {
  drawChunkOverlays()
})
```

---

## 🎨 Color System

### **Design Tokens**

```css
/* src/app/globals.css */
@layer base {
  :root {
    /* Primary colors */
    --color-primary: 217 91% 60%;
    --color-primary-foreground: 0 0% 100%;
    
    /* Chunk visualization colors */
    --chunk-overlay-opacity: 0.25;
    --chunk-border-opacity: 1;
    --chunk-hover-opacity: 0.63;
    --chunk-selected-border: 0 0% 100%;
    
    /* Shader backgrounds */
    --shader-opacity: 0.8;
    --shader-blend-mode: screen;
  }

  .dark {
    --background: 224 71% 4%;
    --foreground: 213 31% 91%;
    /* ... */
  }
}
```

---

## 🚀 Deployment Configuration

### **Next.js Optimization**

```javascript
// next.config.js
/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  
  // Optimize images
  images: {
    domains: ['images.unsplash.com'],
    formats: ['image/avif', 'image/webp']
  },
  
  // Enable SWC minification
  swcMinify: true,
  
  // Compress responses
  compress: true,
  
  // Webpack optimizations
  webpack: (config, { isServer }) => {
    // Optimize shader components
    if (!isServer) {
      config.resolve.fallback = {
        ...config.resolve.fallback,
        fs: false,
      }
    }
    
    return config
  },
  
  // Experimental features
  experimental: {
    optimizeCss: true,
    scrollRestoration: true,
  }
}

module.exports = nextConfig
```

---

## ✅ Implementation Checklist

```markdown
## Setup Phase
- [ ] Initialize Next.js project with TypeScript
- [ ] Install shadcn/ui and configure
- [ ] Install all dependencies (three, react-pdf, framer-motion, etc.)
- [ ] Setup Tailwind CSS with custom configuration
- [ ] Create folder structure

## Shader Components
- [ ] Integrate Neon Crystal City (landing page)
- [ ] Integrate Shader Lines (visualizer background)
- [ ] Integrate ATC Shader (pipeline builder)
- [ ] Test performance on different devices
- [ ] Add fallback for devices without WebGL

## Chunk Visualizer
- [ ] Implement PDFRenderer component
- [ ] Implement Canvas-based ChunkOverlay
- [ ] Create color generation algorithm
- [ ] Add ChunkTooltip with animations
- [ ] Build ChunkDetailPanel with slide-in effect
- [ ] Implement hover detection
- [ ] Add click selection
- [ ] Test with 100+ chunks
- [ ] Optimize for 1000+ page documents
- [ ] Add keyboard navigation
- [ ] Ensure ARIA compliance

## Control Panels
- [ ] Build ChunkConfigPanel
- [ ] Add real-time preview
- [ ] Implement slider controls
- [ ] Add method selection dropdown
- [ ] Connect to backend API

## State Management
- [ ] Setup Zustand stores
- [ ] Implement chunk store
- [ ] Implement pipeline store
- [ ] Add UI store for modals/panels

## API Integration
- [ ] Setup TanStack Query
- [ ] Create API client
- [ ] Implement upload hooks
- [ ] Implement chunk visualization hooks
- [ ] Add error handling
- [ ] Add loading states

## Animations
- [ ] Add page transitions
- [ ] Implement loading skeletons
- [ ] Add micro-interactions
- [ ] Test animation performance

## Responsive Design
- [ ] Test on mobile (320px - 768px)
- [ ] Test on tablet (768px - 1024px)
- [ ] Test on desktop (1024px+)
- [ ] Add touch event handling
- [ ] Optimize for different screen sizes

## Performance
- [ ] Lighthouse audit (score > 90)
- [ ] Canvas rendering < 16ms
- [ ] PDF load time < 1s
- [ ] Implement code splitting
- [ ] Add lazy loading
- [ ] Optimize bundle size

## Accessibility
- [ ] Keyboard navigation works
- [ ] Screen reader compatible
- [ ] ARIA labels present
- [ ] Color contrast meets WCAG AA
- [ ] Focus indicators visible

## Testing
- [ ] Manual testing on all pages
- [ ] Cross-browser testing (Chrome, Firefox, Safari)
- [ ] Mobile device testing
- [ ] Performance testing
- [ ] Accessibility audit

## Documentation
- [ ] Component documentation
- [ ] API documentation
- [ ] Setup instructions
- [ ] Deployment guide
```

---

## 🎯 Quality Assurance

### **Testing Strategy**

```bash
# Visual regression testing
npm install -D @storybook/react
npm install -D chromatic

# Component testing
npm install -D @testing-library/react
npm install -D @testing-library/jest-dom

# E2E testing
npm install -D @playwright/test
```

### **Example Test**

```tsx
// src/components/visualizer/__tests__/chunk-visualizer.test.tsx
import { render, screen, fireEvent } from '@testing-library/react'
import { ChunkVisualizer } from '../chunk-visualizer'

describe('ChunkVisualizer', () => {
  const mockChunks = [
    {
      id: 'chunk_0',
      text: 'Sample chunk text',
      bbox: { page: 1, x: 100, y: 100, width: 200, height: 50 },
      metadata: { char_count: 17, token_count: 4 }
    }
  ]

  it('renders PDF with chunks', () => {
    render(
      <ChunkVisualizer 
        documentId="test-doc"
        pdfUrl="/test.pdf"
        initialChunks={mockChunks}
      />
    )
    
    expect(screen.getByRole('application')).toBeInTheDocument()
  })

  it('highlights chunk on hover', () => {
    const { container } = render(
      <ChunkVisualizer 
        documentId="test-doc"
        pdfUrl="/test.pdf"
        initialChunks={mockChunks}
      />
    )
    
    const canvas = container.querySelector('canvas')
    fireEvent.mouseMove(canvas!, { clientX: 150, clientY: 125 })
    
    // Tooltip should appear
    expect(screen.getByText('Sample chunk text')).toBeInTheDocument()
  })

  it('selects chunk on click', () => {
    const { container } = render(
      <ChunkVisualizer 
        documentId="test-doc"
        pdfUrl="/test.pdf"
        initialChunks={mockChunks}
      />
    )
    
    const canvas = container.querySelector('canvas')
    fireEvent.mouseMove(canvas!, { clientX: 150, clientY: 125 })
    fireEvent.click(canvas!)
    
    // Detail panel should open
    expect(screen.getByText('Chunk Details')).toBeInTheDocument()
  })
})
```

---

## 📚 Resources

### **Component Libraries**
- **shadcn/ui**: https://ui.shadcn.com
- **Magic UI**: https://magicui.design
- **Aceternity UI**: https://ui.aceternity.com
- **21st.dev**: https://21st.dev

### **Shader Resources**
- **Three.js Examples**: https://threejs.org/examples
- **Shadertoy**: https://www.shadertoy.com
- **The Book of Shaders**: https://thebookofshaders.com

### **Performance**
- **web.dev Performance**: https://web.dev/performance
- **Chrome DevTools**: Performance profiling
- **Lighthouse CI**: Automated audits

### **Accessibility**
- **WCAG Guidelines**: https://www.w3.org/WAI/WCAG21/quickref
- **ARIA Practices**: https://www.w3.org/WAI/ARIA/apg

---

This comprehensive guide provides everything needed to build a stunning, performant, and accessible frontend for ChunkScope using modern React practices and beautiful shader effects! 🚀
