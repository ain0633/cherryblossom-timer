import { useGLTF } from '@react-three/drei'
import { useFrame } from '@react-three/fiber'
import { useMemo, useRef } from 'react'
import * as THREE from 'three'

// Distant cherry trees, straight from Blender (fartrees.glb): a branch skeleton (FarTrunkMat) +
// fluffy 9-lump canopy (FarPink1/2/3). The canopy fades with `bloom` -> on 낙화 the branches show.
const FAR: Record<string, string> = {
  FarTrunkMat: '#5b4636',
  FarPink1: '#eda8c7',
  FarPink2: '#db80ab',
  FarPink3: '#f5ccde',
}
const clamp = (x: number) => Math.max(0, Math.min(1, x))

export function FarTrees({ bloom }: { bloom: number }) {
  const { scene } = useGLTF('/assets/fartrees.glb', '/draco/')
  const canopyMats = useRef<THREE.MeshStandardMaterial[]>([])
  const bloomRef = useRef(bloom)
  bloomRef.current = bloom

  useMemo(() => {
    const seen = new Set<THREE.Material>()
    scene.traverse((o) => {
      const m = o as THREE.Mesh
      const mat = m.material as THREE.MeshStandardMaterial
      if (!(m as any).isMesh || !mat) return
      const isTrunk = mat.name.includes('Trunk') || m.name.toLowerCase().includes('branch')
      const hex = FAR[mat.name] ?? (isTrunk ? '#5b4636' : '#f0bcd4')
      mat.color.set(hex)
      mat.roughness = 0.9
      if (isTrunk) {
        mat.emissive.set('#000000')
        mat.emissiveIntensity = 0
      } else {
        mat.emissive.set(hex)
        mat.emissiveIntensity = 0.12
        mat.transparent = true // fade with bloom (낙화/개화)
        if (!seen.has(mat)) { seen.add(mat); canopyMats.current.push(mat) }
      }
    })
  }, [scene])

  useFrame(() => {
    const b = clamp(bloomRef.current)
    for (const mat of canopyMats.current) {
      mat.opacity = b
      mat.emissiveIntensity = 0.12 * b
      mat.depthWrite = b > 0.5 // solid crown when bloomed; reveals branches as it sheds
    }
  })

  return <primitive object={scene} />
}

useGLTF.preload('/assets/fartrees.glb', '/draco/')
