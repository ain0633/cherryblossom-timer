import { useEffect } from 'react'
import { useThree, useLoader } from '@react-three/fiber'
import * as THREE from 'three'

// Blender SkyDome baked to an equirectangular image -> the web sky is 100% identical to the .blend.
export function SkyDome() {
  const { scene } = useThree()
  const tex = useLoader(THREE.TextureLoader, '/assets/sky.jpg')
  useEffect(() => {
    tex.mapping = THREE.EquirectangularReflectionMapping
    tex.colorSpace = THREE.SRGBColorSpace
    scene.background = tex
    return () => { scene.background = null }
  }, [tex, scene])
  return null
}
