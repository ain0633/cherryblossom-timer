import { useGLTF } from '@react-three/drei'

// v2 ground (rolling hills) with the GroundMat grass baked to a texture in Blender -> authentic color
export function Ground() {
  const { scene } = useGLTF('/assets/ground.glb', '/draco/')
  return <primitive object={scene} />
}

useGLTF.preload('/assets/ground.glb', '/draco/')
