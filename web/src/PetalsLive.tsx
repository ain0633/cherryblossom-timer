import { Canvas, useFrame, useThree } from '@react-three/fiber'
import * as THREE from 'three'
import { useEffect, useMemo, useRef } from 'react'

const MAX = 5500
const clamp = (x: number) => Math.max(0, Math.min(1, x))

// Petals detach from the CANOPY and fall to the ground. The canopy is modeled as an
// ELLIPSOID (umbrella) so petals only ever appear over the pink foliage -- never in the blue
// sky beside/above it. The radius tapers to ~0 at the top & bottom, like the real crown.
const Y_BOT = 4.0                      // canopy bottom (three y)
const Y_TOP = 12.5                     // canopy top
const Y_CEN = (Y_BOT + Y_TOP) / 2      // 8.25 -> widest height
const Y_HALF = (Y_TOP - Y_BOT) / 2     // 4.25
const R_CEN = 6.0                      // horizontal radius at the canopy's widest (mid height)
const Z_OFF = -1.0                     // nudge toward the camera-front half (off the trunk)

// max horizontal radius at height y: 0 at top/bottom, R_CEN at the middle (ellipsoid profile)
function rmaxAt(y: number) {
  const t = (y - Y_CEN) / Y_HALF
  return R_CEN * Math.sqrt(Math.max(0, 1 - t * t))
}

// tints multiply the pale Blender-rendered petal sprite -> varied sakura pinks
const PINKS = ['#f3a4c4', '#ec8cb6', '#f8c8dc', '#ffdbe8']

type P = {
  x: number; z: number; y: number
  vy: number                     // terminal fall speed (units/s)
  dx: number; dz: number         // net sideways drift -> petals fan out as they fall (wind)
  ax: number; az: number; fx: number; fz: number; px: number; pz: number  // flutter
  rx: number; ry: number; rz: number      // current rotation
  wx: number; wy: number; wz: number      // angular velocity (tumble)
  s: number
}

function makePetal(full: boolean): P {
  // 1. pick a detach point INSIDE the canopy ellipsoid (always over the pink foliage, never sky)
  const sy = Y_CEN + (Math.random() * 2 - 1) * Y_HALF * 0.96   // height within the crown
  const a = Math.random() * Math.PI * 2
  // mild center bias only -> petals shed from the WHOLE canopy width, not just a central column
  const r = Math.pow(Math.random(), 0.85) * rmaxAt(sy)
  return {
    x: Math.cos(a) * r,
    z: Math.sin(a) * r + Z_OFF,
    // recycle: start AT the detach point (drifts out of the foliage).
    // pre-warm (full): scatter down the fall path so the whole column is full on frame 1.
    y: full ? sy - Math.random() * (sy + 0.5) : sy,
    vy: 0.55 + Math.random() * 0.45,                  // gentle float-down (varied -> no streaks)
    // very light sway only -> petals stay UNDER the tree (don't blow out across the field)
    dx: (Math.random() * 2 - 1) * 0.12, dz: (Math.random() * 2 - 1) * 0.08,
    ax: 0.1 + Math.random() * 0.22, az: 0.1 + Math.random() * 0.22,  // local flutter
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
      p.y -= p.vy * d                           // fall
      p.x += p.dx * d; p.z += p.dz * d          // wind drift -> fans out from the canopy as it descends
      if (p.y < -0.3) Object.assign(p, makePetal(false))  // recycle back up into the foliage
      p.rx += p.wx * d; p.ry += p.wy * d; p.rz += p.wz * d  // tumble (so it never looks like a flat card)
      const sx = Math.sin(t * p.fx + p.px) * p.ax        // local flutter
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
