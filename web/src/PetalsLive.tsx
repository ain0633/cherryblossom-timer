import { Canvas, useFrame, useThree } from '@react-three/fiber'
import * as THREE from 'three'
import { useEffect, useMemo, useRef } from 'react'

const MAX = 2800
const clamp = (x: number) => Math.max(0, Math.min(1, x))

// canopy region (three coords): disc radius R in x/z, petals fall from canopy down to ground.
// TOP = canopy top: petals are never spawned ABOVE this (no petals in the sky over the tree).
const R = 6.0
const TOP = 11.0
// tints multiply the pale Blender-rendered petal sprite -> varied sakura pinks
const PINKS = ['#f3a4c4', '#ec8cb6', '#f8c8dc', '#ffdbe8']

type P = {
  x: number; z: number; y: number
  vy: number                     // terminal fall speed (units/s) -> uniform column
  ax: number; az: number; fx: number; fz: number; px: number; pz: number  // flutter
  rx: number; ry: number; rz: number      // current rotation
  wx: number; wy: number; wz: number      // angular velocity (tumble)
  s: number
}

function makePetal(full: boolean): P {
  const a = Math.random() * Math.PI * 2
  const r = Math.pow(Math.random(), 0.5) * R        // strong center bias: dense under the canopy
  return {
    x: Math.cos(a) * r,
    // bias toward the camera-facing front half so petals don't float "in front of" the trunk
    z: Math.sin(a) * r - 1.5,
    // full=true: spread through the column (0..TOP) so it's full from the first frame.
    // recycle: re-emerge WITHIN the upper canopy (never above it -> no petals in the sky)
    y: full ? Math.random() * TOP : TOP - Math.random() * 2.0,
    vy: 0.6 + Math.random() * 0.5,                    // gentle float-down
    ax: 0.1 + Math.random() * 0.22, az: 0.1 + Math.random() * 0.22,  // small drift -> mostly vertical
    fx: 0.3 + Math.random() * 0.5, fz: 0.3 + Math.random() * 0.5,
    px: Math.random() * 6.28, pz: Math.random() * 6.28,
    rx: Math.random() * 6.28, ry: Math.random() * 6.28, rz: Math.random() * 6.28,
    wx: (Math.random() * 2 - 1) * 0.9, wy: (Math.random() * 2 - 1) * 0.9, wz: (Math.random() * 2 - 1) * 0.9,
    s: 0.085 + Math.random() * 0.055,                // small, dense petals (like Blender)
  }
}

function Petals({ amount }: { amount: number }) {
  const ref = useRef<THREE.InstancedMesh>(null)
  const dummy = useMemo(() => new THREE.Object3D(), [])
  // real cherry petal rendered in Blender (shape + soft shading + tip notch)
  const tex = useMemo(() => {
    const t = new THREE.TextureLoader().load('/petals/petal.png')
    t.colorSpace = THREE.SRGBColorSpace
    return t
  }, [])
  const ps = useMemo(() => Array.from({ length: MAX }, () => makePetal(true)), [])

  useEffect(() => {
    const inst = ref.current; if (!inst) return
    for (let i = 0; i < MAX; i++) inst.setColorAt(i, new THREE.Color(PINKS[(Math.random() * PINKS.length) | 0]))
    if (inst.instanceColor) inst.instanceColor.needsUpdate = true
  }, [ps])

  useFrame((st, dt) => {
    const inst = ref.current; if (!inst) return
    const d = Math.min(0.05, dt)
    const t = st.clock.elapsedTime
    const active = Math.floor(clamp(amount) * MAX)
    for (let i = 0; i < MAX; i++) {
      const p = ps[i]
      if (i >= active) {                        // hide inactive (fewer petals as tree empties)
        dummy.position.set(0, -1000, 0); dummy.scale.setScalar(0)
        dummy.updateMatrix(); inst.setMatrixAt(i, dummy.matrix); continue
      }
      p.y -= p.vy * d                           // constant terminal-velocity fall (uniform column)
      if (p.y < -0.3) Object.assign(p, makePetal(false))  // recycle to the top
      p.rx += p.wx * d; p.ry += p.wy * d; p.rz += p.wz * d  // tumble (so it never looks like a flat card)
      const sx = Math.sin(t * p.fx + p.px) * p.ax        // flutter / drift
      const sz = Math.cos(t * p.fz + p.pz) * p.az
      dummy.position.set(p.x + sx, p.y, p.z + sz)
      dummy.rotation.set(p.rx, p.ry, p.rz)
      dummy.scale.setScalar(p.s)
      dummy.updateMatrix(); inst.setMatrixAt(i, dummy.matrix)
    }
    inst.instanceMatrix.needsUpdate = true
  })

  return (
    <instancedMesh ref={ref} args={[undefined, undefined, MAX]}>
      <planeGeometry args={[1, 1]} />
      <meshBasicMaterial map={tex} toneMapped={false} side={THREE.DoubleSide}
        transparent depthWrite={false} alphaTest={0.04} />
    </instancedMesh>
  )
}

// match the baked Blender stage camera (loc (0.4,44,3.0), lookAt (0,0,5.5), lens 46, 16:9)
const CAM_POS: [number, number, number] = [0.4, 3.0, -44.0]
const CAM_LOOK: [number, number, number] = [0, 5.5, 0]
function CamRig() {
  const { camera, size } = useThree()
  useEffect(() => {
    const cam = camera as THREE.PerspectiveCamera
    const hfov = (42.74 * Math.PI) / 180
    const vfov16 = 2 * Math.atan(Math.tan(hfov / 2) * (9 / 16))
    const aspect = size.width / size.height
    const fov = aspect >= 16 / 9 ? 2 * Math.atan(Math.tan(hfov / 2) / aspect) : vfov16
    cam.fov = (fov * 180) / Math.PI
    cam.position.set(...CAM_POS); cam.lookAt(...CAM_LOOK); cam.updateProjectionMatrix()
  }, [camera, size])
  return null
}

export function PetalsLive({ amount }: { amount: number }) {
  return (
    <Canvas className="petal-canvas" gl={{ alpha: true, antialias: true }} camera={{ position: CAM_POS, fov: 28 }}>
      <CamRig />
      <Petals amount={amount} />
    </Canvas>
  )
}
