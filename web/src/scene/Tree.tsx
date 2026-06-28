import { useGLTF } from '@react-three/drei'

export function Tree() {
  // draco decoder served from /public/draco. trunk.glb = v2 red bark baked from BarkMat.
  const { scene } = useGLTF('/assets/trunk.glb', '/draco/')
  return <primitive object={scene} />
}

useGLTF.preload('/assets/trunk.glb', '/draco/')
