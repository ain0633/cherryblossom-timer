import * as THREE from 'three'
import { useMemo, useRef } from 'react'
import { useFrame } from '@react-three/fiber'

type P = {
  x: number; z: number; y: number; speed: number
  swayAmp: number; swayFreq: number; phase: number
  rot: number; rotSpeed: number; scale: number
}

export function Petals({ count = 450, intensity = 1 }: { count?: number; intensity?: number }) {
  const ref = useRef<THREE.InstancedMesh>(null)
  const dummy = useMemo(() => new THREE.Object3D(), [])
  const data = useMemo<P[]>(
    () =>
      Array.from({ length: count }, () => ({
        x: (Math.random() * 2 - 1) * 7,
        z: (Math.random() * 2 - 1) * 7,
        y: Math.random() * 9,
        speed: 0.45 + Math.random() * 0.5,
        swayAmp: 0.25 + Math.random() * 0.55,
        swayFreq: 0.4 + Math.random() * 0.8,
        phase: Math.random() * 6.28,
        rot: Math.random() * 6.28,
        rotSpeed: (Math.random() * 2 - 1) * 1.8,
        scale: 0.09 + Math.random() * 0.05,
      })),
    [count]
  )

  useFrame((state, dt) => {
    const inst = ref.current
    if (!inst) return
    const t = state.clock.elapsedTime
    const visible = Math.floor(THREE.MathUtils.clamp(intensity, 0, 1) * count)
    for (let i = 0; i < count; i++) {
      const p = data[i]
      p.y -= p.speed * dt
      if (p.y < 0.06) {
        p.y = 8 + Math.random() * 2
        p.x = (Math.random() * 2 - 1) * 7
        p.z = (Math.random() * 2 - 1) * 7
      }
      p.rot += p.rotSpeed * dt
      const sx = Math.sin(t * p.swayFreq + p.phase) * p.swayAmp
      const sz = Math.cos(t * p.swayFreq + p.phase) * p.swayAmp * 0.6
      dummy.position.set(p.x + sx, p.y, p.z + sz)
      dummy.rotation.set(p.rot, p.rot * 0.7, p.rot * 0.4)
      const s = i < visible ? p.scale : 0
      dummy.scale.set(s, s, s)
      dummy.updateMatrix()
      inst.setMatrixAt(i, dummy.matrix)
    }
    inst.instanceMatrix.needsUpdate = true
  })

  return (
    <instancedMesh ref={ref} args={[undefined, undefined, count]}>
      <planeGeometry args={[1, 1.4]} />
      <meshStandardMaterial color="#f2a6bd" roughness={0.8} side={THREE.DoubleSide} />
    </instancedMesh>
  )
}
