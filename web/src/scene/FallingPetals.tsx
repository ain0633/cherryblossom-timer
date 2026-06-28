import * as THREE from 'three'
import { useEffect, useMemo, useRef, useState } from 'react'
import { useFrame } from '@react-three/fiber'
import { asset } from '../assetUrl'

// Petals fall FROM the tree: each one spawns at a real blossom position (from blossoms.json)
// and descends to the ground, then recycles to another blossom. Pool / object reuse -> seamless.
const MAX = 2200
const GROUND = 0.12
const clamp = (x: number) => Math.max(0, Math.min(1, x))

type P = {
  bx: number; bz: number; y: number          // bx/bz = the column it falls in (a blossom's x,z); y descends
  vy: number; sway: number; freq: number; phase: number
  rx: number; ry: number; rz: number         // rotation
  wx: number; wy: number; wz: number         // tumble
  s: number
}

export function FallingPetals({ amount }: { amount: number }) {
  const ref = useRef<THREE.InstancedMesh>(null)
  const dummy = useMemo(() => new THREE.Object3D(), [])
  const posRef = useRef<number[][] | null>(null)
  const psRef = useRef<P[]>([])
  const [ready, setReady] = useState(false)

  // the real cherry petal sprite rendered in Blender (shape + soft shading + tip notch)
  const tex = useMemo(() => {
    const t = new THREE.TextureLoader().load(asset('petals/petal.png'))
    t.colorSpace = THREE.SRGBColorSpace
    return t
  }, [])

  // spawn a petal at a random blossom location. prewarm: scatter down the fall path (full on frame 1)
  const spawn = (prewarm: boolean): P => {
    const pos = posRef.current!
    const b = pos[(Math.random() * pos.length) | 0]
    return {
      bx: b[0], bz: b[2],
      y: prewarm ? GROUND + Math.random() * (b[1] - GROUND) : b[1],
      vy: 0.5 + Math.random() * 0.5,
      sway: 0.12 + Math.random() * 0.28, freq: 0.4 + Math.random() * 0.7, phase: Math.random() * 6.28,
      rx: Math.random() * 6.28, ry: Math.random() * 6.28, rz: Math.random() * 6.28,
      wx: (Math.random() * 2 - 1) * 1.2, wy: (Math.random() * 2 - 1) * 1.2, wz: (Math.random() * 2 - 1) * 1.2,
      s: 0.11 + Math.random() * 0.06,
    }
  }

  useEffect(() => {
    fetch(asset('assets/blossoms.json')).then((r) => r.json()).then((d) => {
      posRef.current = d.positions
      psRef.current = Array.from({ length: MAX }, () => spawn(true))
      setReady(true)
    })
  }, [])

  useFrame((st, dt) => {
    const inst = ref.current
    if (!inst || !ready) return
    const d = Math.min(0.05, dt)
    const t = st.clock.elapsedTime
    const ps = psRef.current
    const active = Math.floor(clamp(amount) * MAX)
    for (let i = 0; i < MAX; i++) {
      const p = ps[i]
      if (i >= active) {                       // hide inactive (fewer petals as the tree empties)
        dummy.position.set(0, -1000, 0); dummy.scale.setScalar(0)
        dummy.updateMatrix(); inst.setMatrixAt(i, dummy.matrix); continue
      }
      p.y -= p.vy * d
      if (p.y < GROUND) { Object.assign(p, spawn(false)); }   // landed -> detach from another blossom
      p.rx += p.wx * d; p.ry += p.wy * d; p.rz += p.wz * d     // tumble
      const sx = Math.sin(t * p.freq + p.phase) * p.sway       // gentle sway around its column
      const sz = Math.cos(t * p.freq + p.phase) * p.sway * 0.7
      dummy.position.set(p.bx + sx, p.y, p.bz + sz)
      dummy.rotation.set(p.rx, p.ry, p.rz)
      dummy.scale.setScalar(p.s)
      dummy.updateMatrix(); inst.setMatrixAt(i, dummy.matrix)
    }
    inst.instanceMatrix.needsUpdate = true
  })

  if (!ready) return null
  return (
    <instancedMesh ref={ref} args={[undefined, undefined, MAX]}>
      <planeGeometry args={[1, 1]} />
      <meshStandardMaterial map={tex} side={THREE.DoubleSide}
        transparent depthWrite={false} alphaTest={0.04} roughness={0.85} />
    </instancedMesh>
  )
}
