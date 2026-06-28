import * as THREE from 'three'
import { useEffect, useMemo, useRef, useState } from 'react'
import { useGLTF } from '@react-three/drei'
import { useFrame } from '@react-three/fiber'
import { asset } from '../assetUrl'

type Data = { positions: number[][]; colors: number[][] }

export function Blossoms({ bloom }: { bloom: number }) {
  const { nodes } = useGLTF(asset('assets/flower.glb'))
  const [data, setData] = useState<Data | null>(null)
  const ref = useRef<THREE.InstancedMesh>(null)

  useEffect(() => {
    fetch(asset('assets/blossoms.json')).then((r) => r.json()).then(setData)
  }, [])

  const geo = useMemo(() => {
    let g: THREE.BufferGeometry | null = null
    Object.values(nodes).forEach((n) => {
      const mesh = n as THREE.Mesh
      if ((mesh as any).isMesh && !g) g = mesh.geometry
    })
    return g
  }, [nodes])

  useEffect(() => {
    const inst = ref.current
    if (!inst || !data) return
    const m = new THREE.Matrix4()
    const q = new THREE.Quaternion()
    const e = new THREE.Euler()
    const pos = new THREE.Vector3()
    const scl = new THREE.Vector3()
    const col = new THREE.Color()
    for (let i = 0; i < data.positions.length; i++) {
      const p = data.positions[i]
      e.set(Math.random() * Math.PI, Math.random() * Math.PI * 2, Math.random() * Math.PI)
      q.setFromEuler(e)
      const s = 0.8 + Math.random() * 0.6
      pos.set(p[0], p[1], p[2])
      scl.set(s, s, s)
      m.compose(pos, q, scl)
      inst.setMatrixAt(i, m)
      const c = data.colors[i]
      // saturate toward pink (pull green/blue down) so the canopy reads pink, not whitish
      col.setRGB(c[0], c[1] * 0.82, c[2] * 0.9)
      inst.setColorAt(i, col)
    }
    inst.instanceMatrix.needsUpdate = true
    if (inst.instanceColor) inst.instanceColor.needsUpdate = true
  }, [data])

  useFrame(() => {
    if (!ref.current || !data) return
    ref.current.count = Math.floor(THREE.MathUtils.clamp(bloom, 0, 1) * data.positions.length)
  })

  if (!geo || !data) return null
  return (
    <instancedMesh ref={ref} args={[geo, undefined, data.positions.length]} castShadow>
      <meshStandardMaterial vertexColors roughness={0.7} side={THREE.DoubleSide} />
    </instancedMesh>
  )
}

useGLTF.preload(asset('assets/flower.glb'))
