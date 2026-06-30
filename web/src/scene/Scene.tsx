import { Canvas } from '@react-three/fiber'
import { OrbitControls } from '@react-three/drei'
import { Suspense } from 'react'
import { Tree } from './Tree'
import { Canopy } from './Canopy'
import { FallingPetals } from './FallingPetals'
import { GroundCarpet } from './GroundCarpet'
import { SkyDome } from './SkyDome'
import { Ground } from './Ground'
import { FarTrees } from './FarTrees'

// Real-time 3D scene: petals truly detach from the tree (spawn at blossom positions).
// bloom -> how many blossoms remain on the tree; petalAmount -> how many are falling.
export function Scene({ bloom, petalAmount, carpetAmount }:
  { bloom: number; petalAmount: number; carpetAmount: number }) {
  return (
    <Canvas
      className="scene-canvas"
      camera={{ position: [0.5, 7.5, 27], fov: 42, near: 0.1, far: 800 }}
      gl={{ antialias: true }}
    >
      <hemisphereLight args={['#dcefff', '#7cae58', 1.05]} />
      <directionalLight position={[14, 26, 12]} intensity={1.5} color="#fff4e6" />
      {/* soft fill from the camera side so the bark isn't dark/contrasty */}
      <directionalLight position={[-6, 10, 24]} intensity={0.6} color="#eaf2ff" />
      <ambientLight intensity={0.4} />
      <Suspense fallback={null}>
        <SkyDome />
        <Ground />
        <FarTrees bloom={bloom} />
        <Tree />
        <Canopy bloom={bloom} />
        <FallingPetals amount={petalAmount} />
        <GroundCarpet amount={carpetAmount} />
      </Suspense>
      <OrbitControls
        target={[0, 6, 0]}
        enablePan={false}
        enableDamping
        minDistance={12}
        maxDistance={70}
        minPolarAngle={0.25}
        maxPolarAngle={Math.PI / 2 - 0.04}
      />
    </Canvas>
  )
}
