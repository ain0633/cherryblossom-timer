import { useGLTF } from '@react-three/drei'
import { asset } from '../assetUrl'

export function Tree() {
  // draco decoder served from /public/draco. trunk.glb = v2 red bark baked from BarkMat.
  const { scene } = useGLTF(asset('assets/trunk.glb'), asset('draco/'))
  return <primitive object={scene} />
}

useGLTF.preload(asset('assets/trunk.glb'), asset('draco/'))
