"use client"

import { useRef, useMemo } from 'react'
import { useFrame } from '@react-three/fiber'
import * as THREE from 'three'
import { Color } from 'three'

const BUILDING_COUNT = 400
const CITY_SIZE = 100

export default function NeonCrystalCity() {
    const meshRef = useRef<THREE.InstancedMesh>(null)
    const lightRef = useRef<THREE.PointLight>(null)

    // Generate city layout once
    const { positions, heights, colors } = useMemo(() => {
        const tempPositions = []
        const tempHeights = []
        const tempColors = []

        for (let i = 0; i < BUILDING_COUNT; i++) {
            // Grid-like layout with some randomness
            const x = (Math.random() - 0.5) * CITY_SIZE
            const z = (Math.random() - 0.5) * CITY_SIZE
            const y = 0

            const height = Math.random() * 5 + 1
            const color = new Color().setHSL(Math.random() * 0.1 + 0.6, 0.8, 0.5) // Blue-Purple range

            tempPositions.push(x, y, z)
            tempHeights.push(height)
            tempColors.push(color.r, color.g, color.b)
        }

        return {
            positions: new Float32Array(tempPositions),
            heights: new Float32Array(tempHeights),
            colors: new Float32Array(tempColors)
        }
    }, [])

    // Set instances
    useMemo(() => {
        if (!meshRef.current) return

        const tempObject = new THREE.Object3D()
        const tempColor = new THREE.Color()

        for (let i = 0; i < BUILDING_COUNT; i++) {
            tempObject.position.set(
                positions[i * 3],
                heights[i] / 2, // Center vertically
                positions[i * 3 + 2]
            )
            tempObject.scale.set(1, heights[i], 1)
            tempObject.updateMatrix()

            meshRef.current.setMatrixAt(i, tempObject.matrix)

            tempColor.setRGB(colors[i * 3], colors[i * 3 + 1], colors[i * 3 + 2])
            meshRef.current.setColorAt(i, tempColor)
        }
    }, [positions, heights, colors])

    useFrame((state) => {
        if (!meshRef.current) return

        // Subtle float animation for the whole city
        meshRef.current.rotation.y = Math.sin(state.clock.elapsedTime * 0.1) * 0.1

        // Move light
        if (lightRef.current) {
            lightRef.current.position.x = Math.sin(state.clock.elapsedTime * 0.5) * 20
            lightRef.current.position.z = Math.cos(state.clock.elapsedTime * 0.5) * 20
        }
    })

    return (
        <>
            <color attach="background" args={['#050510']} />
            <fog attach="fog" args={['#050510', 5, 40]} />

            <ambientLight intensity={0.2} />
            <pointLight ref={lightRef} position={[10, 10, 10]} intensity={1} color="#ff00ff" />

            <instancedMesh ref={meshRef} args={[undefined, undefined, BUILDING_COUNT]}>
                <boxGeometry args={[1, 1, 1]} />
                <meshStandardMaterial
                    color="#444"
                    emissive="#220033"
                    roughness={0.2}
                    metalness={0.8}
                />
            </instancedMesh>

            {/* Floor grid */}
            <gridHelper args={[100, 50, '#333', '#111']} position={[0, 0, 0]} />
        </>
    )
}
