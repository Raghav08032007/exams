/**
 * HeroAmbientParticles.jsx
 * Sparse floating "paper fleck" particle canvas layer.
 * Low GPU footprint (12 particles max).
 * Lerps particle tints to match the active exam's accent color.
 */
import { useRef, useMemo } from 'react'
import { Canvas, useFrame } from '@react-three/fiber'
import { useReducedMotion } from '../../hooks/useReducedMotion'
import * as THREE from 'three'

function ParticleFlecks({ activeAccent }) {
  const meshRef = useRef()
  const count = 14

  const targetColor = useMemo(() => new THREE.Color(activeAccent), [activeAccent])
  const currentColor = useRef(new THREE.Color(activeAccent)).current

  // Generate random initial positions & speeds for paper flecks
  const particles = useMemo(() => {
    return Array.from({ length: count }, () => ({
      position: [
        (Math.random() - 0.5) * 8,
        (Math.random() - 0.5) * 6,
        (Math.random() - 0.5) * 4,
      ],
      rotation: [Math.random() * Math.PI, Math.random() * Math.PI, 0],
      speed: 0.2 + Math.random() * 0.3,
      scale: 0.08 + Math.random() * 0.12,
    }))
  }, [count])

  useFrame((state) => {
    if (!meshRef.current) return
    const t = state.clock.elapsedTime
    currentColor.lerp(targetColor, 0.08)

    // Gentle sine wave floating motion
    meshRef.current.children.forEach((child, i) => {
      const p = particles[i]
      child.position.y = p.position[1] + Math.sin(t * p.speed + i) * 0.25
      child.position.x = p.position[0] + Math.cos(t * p.speed * 0.8 + i) * 0.15
      child.rotation.z += 0.005
    })
  })

  return (
    <group ref={meshRef}>
      {particles.map((p, i) => (
        <mesh key={i} position={p.position} rotation={p.rotation} scale={p.scale}>
          <planeGeometry args={[0.5, 0.7]} />
          <meshBasicMaterial
            color={currentColor}
            transparent
            opacity={0.28}
            side={THREE.DoubleSide}
          />
        </mesh>
      ))}
    </group>
  )
}

export default function HeroAmbientParticles({ activeAccent = '#8FB9A8' }) {
  const reduced = useReducedMotion()

  if (reduced) return null

  return (
    <div
      style={{
        position: 'absolute',
        inset: 0,
        pointerEvents: 'none',
        zIndex: 0,
      }}
      aria-hidden="true"
    >
      <Canvas
        camera={{ position: [0, 0, 5], fov: 50 }}
        gl={{ antialias: true, alpha: true, powerPreference: 'low-power' }}
        dpr={[1, 1.5]}
        style={{ background: 'transparent' }}
        onCreated={({ gl }) => gl.setClearColor(0x000000, 0)}
      >
        <ParticleFlecks activeAccent={activeAccent} />
      </Canvas>
    </div>
  )
}
