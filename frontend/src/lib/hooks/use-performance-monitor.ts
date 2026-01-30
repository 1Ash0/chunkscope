"use client"

import { useEffect, useState } from 'react'
import { addEffect, addAfterEffect } from '@react-three/fiber'
import * as THREE from 'three'

export function usePerformanceMonitor() {
    const [fps, setFps] = useState(60)
    const [memory, setMemory] = useState({ geometries: 0, textures: 0 })

    useEffect(() => {
        let lastTime = performance.now()
        let frames = 0

        // R3F effect loop for accurate FPS relative to render loop
        const unsubscribe = addAfterEffect(() => {
            const time = performance.now()
            frames++
            if (time >= lastTime + 1000) {
                setFps(Math.round((frames * 1000) / (time - lastTime)))
                frames = 0
                lastTime = time
            }
        })

        return unsubscribe
    }, [])

    return { fps, memory }
}
