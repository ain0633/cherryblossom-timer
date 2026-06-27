import * as THREE from 'three'

const TREES = Array.from({ length: 16 }, (_, i) => {
  const a = (i / 16) * Math.PI * 2 + (Math.random() * 0.3 - 0.15)
  const r = 45 + Math.random() * 30
  const s = 3 + Math.random() * 2.5
  return { x: Math.cos(a) * r, z: Math.sin(a) * r, s }
})

export function DistantTrees() {
  return (
    <group>
      {TREES.map((t, i) => (
        <group key={i} position={[t.x, 0, t.z]}>
          <mesh position-y={t.s * 0.35}>
            <cylinderGeometry args={[t.s * 0.06, t.s * 0.1, t.s * 0.7, 6]} />
            <meshStandardMaterial color="#3a2a22" roughness={1} />
          </mesh>
          <mesh position-y={t.s * 0.85} scale={[t.s * 0.7, t.s * 0.55, t.s * 0.7]}>
            <icosahedronGeometry args={[1, 2]} />
            <meshStandardMaterial color="#c489a0" roughness={1} flatShading={false} side={THREE.FrontSide} />
          </mesh>
        </group>
      ))}
    </group>
  )
}
