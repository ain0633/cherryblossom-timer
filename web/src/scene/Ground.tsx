import { useGLTF } from '@react-three/drei'
import { asset } from '../assetUrl'

// v2 ground (rolling hills) with the GroundMat grass baked to a texture in Blender -> authentic color
export function Ground() {
  const { scene } = useGLTF(asset('assets/ground.glb'), asset('draco/'))
  return <primitive object={scene} />
}

useGLTF.preload(asset('assets/ground.glb'), asset('draco/'))
