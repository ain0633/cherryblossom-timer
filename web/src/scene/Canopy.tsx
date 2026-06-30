import * as THREE from 'three'
import { useMemo, useRef } from 'react'
import { useGLTF } from '@react-three/drei'
import { useFrame } from '@react-three/fiber'
import { asset } from '../assetUrl'

// The cherry canopy brought straight from Blender: the FlowerCard sprite mesh
// (flower_card.png + a per-card HSV tint). This is exactly the lush Blender tree.
// bloom (1..0) hides a random fraction of cards so the canopy thins out as focus
// time passes (each card carries a random threshold in the blue vertex channel).
export function Canopy({ bloom }: { bloom: number }) {
  const { scene } = useGLTF(asset('assets/canopy.glb'))
  const bloomU = useRef({ value: 1 })

  const tex = useMemo(() => {
    const t = new THREE.TextureLoader().load(asset('assets/flower_card.png'))
    t.colorSpace = THREE.SRGBColorSpace
    return t
  }, [])

  // FlowerCard reproduction: sample the card texture, then apply the per-card
  // HSV tint (vCard.r -> value, vCard.g -> saturation; both /2 at export, *2 here)
  // and drop cards whose random key (vCard.b) exceeds the current bloom.
  const mat = useMemo(() => {
    const m = new THREE.MeshBasicMaterial({ map: tex, side: THREE.DoubleSide })
    m.onBeforeCompile = (sh) => {
      sh.uniforms.uBloom = bloomU.current
      sh.vertexShader = sh.vertexShader
        .replace('#include <common>',
          '#include <common>\nattribute vec3 acard;\nvarying vec3 vCard;')
        .replace('#include <begin_vertex>',
          '#include <begin_vertex>\n  vCard = acard;')
      sh.fragmentShader = sh.fragmentShader
        .replace('#include <common>', `#include <common>
        uniform float uBloom; varying vec3 vCard;
        vec3 rgb2hsv(vec3 c){vec4 K=vec4(0.,-1./3.,2./3.,-1.);vec4 p=mix(vec4(c.bg,K.wz),vec4(c.gb,K.xy),step(c.b,c.g));vec4 q=mix(vec4(p.xyw,c.r),vec4(c.r,p.yzx),step(p.x,c.r));float d=q.x-min(q.w,q.y);float e=1.0e-10;return vec3(abs(q.z+(q.w-q.y)/(6.*d+e)),d/(q.x+e),q.x);}
        vec3 hsv2rgb(vec3 c){vec4 K=vec4(1.,2./3.,1./3.,3.);vec3 p=abs(fract(c.xxx+K.xyz)*6.-K.www);return c.z*mix(K.xxx,clamp(p-K.xxx,0.,1.),c.y);}`)
        .replace('#include <map_fragment>', `#include <map_fragment>
        if (vCard.b > uBloom) discard;
        if (diffuseColor.a < 0.45) discard;
        vec3 hsv = rgb2hsv(diffuseColor.rgb);
        hsv.y = clamp(hsv.y * vCard.g * 1.64, 0.0, 1.0);
        hsv.z = clamp(hsv.z * vCard.r * 2.0, 0.0, 1.6);
        diffuseColor.rgb = hsv2rgb(hsv);`)
    }
    return m
  }, [tex])

  // attach our material + move COLOR_0 into a custom 'acard' attribute; keep the
  // glb node transforms (so it lines up with trunk.glb exactly like the trunk does).
  const prepared = useMemo(() => {
    scene.traverse((o) => {
      const mesh = o as THREE.Mesh
      if (!(mesh as any).isMesh) return
      const g = mesh.geometry
      const c = g.getAttribute('color') as THREE.BufferAttribute | undefined
      if (c && !g.getAttribute('acard')) {
        const n = c.count
        const arr = new Float32Array(n * 3)
        for (let i = 0; i < n; i++) { arr[i*3] = c.getX(i); arr[i*3+1] = c.getY(i); arr[i*3+2] = c.getZ(i) }
        g.setAttribute('acard', new THREE.BufferAttribute(arr, 3))
        g.deleteAttribute('color')
      }
      mesh.material = mat
      mesh.frustumCulled = false
    })
    return scene
  }, [scene, mat])

  useFrame(() => { bloomU.current.value = THREE.MathUtils.clamp(bloom, 0, 1) })

  return <primitive object={prepared} />
}

useGLTF.preload(asset('assets/canopy.glb'))
