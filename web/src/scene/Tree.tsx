import { useGLTF } from '@react-three/drei'

export function Tree() {
  // draco decoder served from /public/draco
  const { scene } = useGLTF('/assets/trunk.glb', '/draco/')
  return <primitive object={scene} />
}

useGLTF.preload('/assets/trunk.glb', '/draco/')
