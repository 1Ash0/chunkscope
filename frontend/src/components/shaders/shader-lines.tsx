"use client"

import { useRef, useMemo } from 'react'
import { useFrame } from '@react-three/fiber'
import * as THREE from 'three'
import { Line } from '@react-three/drei'

export function ShaderAnimation() {
    // Create flowing lines
    const lines = useMemo(() => {
        return new Array(20).fill(0).map((_, i) => {
            const points = []
            // Create a nice curve
            for (let j = 0; j < 50; j++) {
                const x = (j - 25) * 2
                const y = Math.sin(j * 0.2 + i) * 5 + (i - 10) * 2
                const z = 0
                points.push(new THREE.Vector3(x, y, z))
            }
            return points
        })
    }, [])

    return (
        <>
            <color attach="background" args={['#020408']} />

            {lines.map((points, i) => (
                <Line
                    key={i}
                    points={points}
                    color={i % 2 === 0 ? "#4facfe" : "#00f2fe"}
                    lineWidth={1}
                    opacity={0.3}
                    transparent
                    position={[0, 0, -20]}
                />
            ))}

            <MovingParticles />
        </>
    )
}

function MovingParticles() {
    const count = 100
    const mesh = useRef<THREE.InstancedMesh>(null)

    const particles = useMemo(() => {
        const temp = []
        for (let i = 0; i < count; i++) {
            const t = Math.random() * 100
            const factor = 20 + Math.random() * 100
            const speed = 0.01 + Math.random() / 200
            const xFactor = -50 + Math.random() * 100
            const yFactor = -50 + Math.random() * 100
            const zFactor = -50 + Math.random() * 100
            temp.push({ t, factor, speed, xFactor, yFactor, zFactor, mx: 0, my: 0 })
        }
        return temp
    }, [])

    const dummy = useMemo(() => new THREE.Object3D(), [])

    useFrame((state) => {
        if (!mesh.current) return

        particles.forEach((particle, i) => {
            let { t, factor, speed, xFactor, yFactor, zFactor } = particle
            t = particle.t += speed / 2
            const a = Math.cos(t) + Math.sin(t * 1) / 10
            const b = Math.sin(t) + Math.cos(t * 2) / 10
            const s = Math.cos(t)

            particle.mx += (state.pointer.x * 1000 - particle.mx) * 0.01
            particle.my += (state.pointer.y * 1000 - 1 - particle.my) * 0.01

            dummy.position.set(
                (particle.mx / 10) * a + xFactor + Math.cos((t / 10) * factor) + (Math.sin(t * 1) * factor) / 10,
                (particle.my / 10) * b + yFactor + Math.sin((t / 10) * factor) + (Math.cos(t * 2) * factor) / 10,
                (particle.my / 10) * b + zFactor + Math.cos((t / 10) * factor) + (Math.sin(t * 3) * factor) / 10
            )
            dummy.scale.set(s, s, s)
            dummy.rotation.set(s * 5, s * 5, s * 5)
            dummy.updateMatrix()
            mesh.current!.setMatrixAt(i, dummy.matrix)
        })
        mesh.current.instanceMatrix.needsUpdate = true
    })

    return (
        <instancedMesh ref={mesh} args={[undefined, undefined, count]}>
            <dodecahedronGeometry args={[0.2, 0]} />
            <meshPhongMaterial color="#05f" />
        </instancedMesh>
    )
}
