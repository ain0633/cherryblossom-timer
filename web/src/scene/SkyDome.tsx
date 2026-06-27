import * as THREE from 'three'
import { useMemo } from 'react'

// teal -> pale gradient sky on the inside of a big sphere
export function SkyDome() {
  const mat = useMemo(() => {
    return new THREE.ShaderMaterial({
      side: THREE.BackSide,
      depthWrite: false,
      uniforms: {
        top: { value: new THREE.Color('#0a5466') },
        mid: { value: new THREE.Color('#2f9fb0') },
        bottom: { value: new THREE.Color('#bfe6e6') },
      },
      vertexShader: `
        varying vec3 vPos;
        void main() {
          vPos = position;
          gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
        }`,
      fragmentShader: `
        varying vec3 vPos;
        uniform vec3 top; uniform vec3 mid; uniform vec3 bottom;
        void main() {
          float h = clamp((normalize(vPos).y * 0.5 + 0.5), 0.0, 1.0);
          vec3 c = h < 0.5
            ? mix(bottom, mid, h * 2.0)
            : mix(mid, top, (h - 0.5) * 2.0);
          gl_FragColor = vec4(c, 1.0);
        }`,
    })
  }, [])
  return (
    <mesh material={mat} scale={300}>
      <sphereGeometry args={[1, 32, 16]} />
    </mesh>
  )
}
