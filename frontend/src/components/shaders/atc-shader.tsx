"use client"

import { useRef } from 'react'
import { useFrame } from '@react-three/fiber'
import * as THREE from 'three'

export default function ATCShader() {
    const groupRef = useRef<THREE.Group>(null)

    useFrame((state) => {
        if (groupRef.current) {
            groupRef.current.rotation.y += 0.002
            groupRef.current.rotation.z = Math.sin(state.clock.elapsedTime * 0.2) * 0.1
        }
    })

    return (
        <>
            <color attach="background" args={['#0a0a0a']} />
            <fog attach="fog" args={['#0a0a0a', 20, 90]} />

            <group ref={groupRef}>
                {/* Radar Rings */}
                {[10, 20, 30, 40].map((radius, i) => (
                    <mesh key={i} rotation={[-Math.PI / 2, 0, 0]}>
                        <ringGeometry args={[radius, radius + 0.1, 64]} />
                        <meshBasicMaterial color="#00ff44" transparent opacity={0.1} side={THREE.DoubleSide} />
                    </mesh>
                ))}

                {/* Connecting Lines (Nodes) */}
                <mesh>
                    <icosahedronGeometry args={[15, 1]} />
                    <meshBasicMaterial color="#00ff44" wireframe transparent opacity={0.05} />
                </mesh>

                {/* Floating Data Points */}
                <points>
                    <sphereGeometry args={[25, 64, 64]} />
                    <pointsMaterial color="#00ff44" size={0.1} transparent opacity={0.4} sizeAttenuation />
                </points>
            </group>
        </>
    )
}
