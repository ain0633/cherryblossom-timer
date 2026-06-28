import * as THREE from 'three'
import { useEffect, useMemo, useRef } from 'react'
import { useFrame } from '@react-three/fiber'

// An even, snow-like carpet of fallen petals, growing with accumulation (amount = 1 - bloom).
// The ground undulates +-0.15 near the tree, so the carpet sits at Y_CARPET (above the hills) as a
// flat layer -> no grass pokes through, even coverage. Blanket decal + flat petal sprites on top.
const MAX = 7000
const R = 12.0
const Y_CARPET = 0.18 // above the ground hills (Z range -0.15..0.14 near the trunk)
const clamp = (x: number) => Math.max(0, Math.min(1, x))
const PINKS = ['#edaac6', '#e892b8', '#f4c6da', '#f6dceb', '#e585aa']

// even pink carpet: solid core -> soft feathered rim, with uniform light petal speckle
function makeBlanket() {
  const c = document.createElement('canvas')
  c.width = c.height = 512
  const g = c.getContext('2d')!
  const grd = g.createRadialGradient(256, 256, 20, 256, 256, 256)
  grd.addColorStop(0.0, 'rgba(233,168,196,1)')
  grd.addColorStop(0.72, 'rgba(234,166,194,0.97)')
  grd.addColorStop(0.9, 'rgba(238,176,202,0.6)')
  grd.addColorStop(1.0, 'rgba(240,180,205,0)')
  g.fillStyle = grd
  g.fillRect(0, 0, 512, 512)
  for (let i = 0; i < 12000; i++) {
    const x = Math.random() * 512, y = Math.random() * 512
    if (Math.hypot(x - 256, y - 256) > 250) continue
    const r = Math.random()
    g.fillStyle = r > 0.6 ? 'rgba(247,208,224,0.45)' : r > 0.3 ? 'rgba(216,128,170,0.4)' : 'rgba(250,230,240,0.4)'
    g.fillRect(x, y, 3, 3)
  }
  const t = new THREE.CanvasTexture(c)
  t.colorSpace = THREE.SRGBColorSpace
  return t
}

export function GroundCarpet({ amount }: { amount: number }) {
  const baseRef = useRef<THREE.Mesh>(null)
  const instRef = useRef<THREE.InstancedMesh>(null)
  const amt = useRef(amount)
  amt.current = amount
  const cur = useRef(0)   // eased display amount -> carpet fades in/out instead of popping

  const petalTex = useMemo(() => {
    const t = new THREE.TextureLoader().load('/petals/petal.png')
    t.colorSpace = THREE.SRGBColorSpace
    return t
  }, [])
  const blanketTex = useMemo(makeBlanket, [])

  // fixed scatter, laid FLAT (yaw on Z so petals never stand up), within the blanket, above the hills
  useEffect(() => {
    const inst = instRef.current
    if (!inst) return
    const d = new THREE.Object3D()
    const col = new THREE.Color()
    for (let i = 0; i < MAX; i++) {
      const a = Math.random() * Math.PI * 2
      const r = Math.pow(Math.random(), 0.6) * R
      d.position.set(Math.cos(a) * r, Y_CARPET + 0.01 + Math.random() * 0.05, Math.sin(a) * r - 1.0)
      d.rotation.set(-Math.PI / 2 + (Math.random() * 0.14 - 0.07), 0, Math.random() * Math.PI * 2)
      d.scale.setScalar(0.12 + Math.random() * 0.07)
      d.updateMatrix()
      inst.setMatrixAt(i, d.matrix)
      col.set(PINKS[(Math.random() * PINKS.length) | 0])
      inst.setColorAt(i, col)
    }
    inst.instanceMatrix.needsUpdate = true
    if (inst.instanceColor) inst.instanceColor.needsUpdate = true
  }, [])

  useFrame((_, dt) => {
    const target = clamp(amt.current)
    cur.current += (target - cur.current) * Math.min(1, dt * 6) // ~0.3s ease
    const a = cur.current
    if (instRef.current) instRef.current.count = Math.floor(a * MAX)
    if (baseRef.current) (baseRef.current.material as THREE.MeshStandardMaterial).opacity = a * 0.96
  })

  return (
    <group>
      {/* even pink blanket, floating just above the ground hills so nothing pokes through */}
      <mesh ref={baseRef} rotation-x={-Math.PI / 2} position={[0, Y_CARPET, -1.0]}>
        <circleGeometry args={[13, 64]} />
        <meshStandardMaterial map={blanketTex} transparent opacity={0} depthWrite={false} roughness={1} />
      </mesh>
      {/* flat petal sprites on top for subtle texture */}
      <instancedMesh ref={instRef} args={[undefined, undefined, MAX]}>
        <planeGeometry args={[1, 1]} />
        <meshStandardMaterial map={petalTex} side={THREE.DoubleSide}
          transparent depthWrite={false} alphaTest={0.35} roughness={0.9} />
      </instancedMesh>
    </group>
  )
}
