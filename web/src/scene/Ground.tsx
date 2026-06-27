export function Ground() {
  return (
    <mesh rotation-x={-Math.PI / 2} position-y={0} receiveShadow>
      <circleGeometry args={[120, 64]} />
      <meshStandardMaterial color="#7a8a3c" roughness={1} />
    </mesh>
  )
}
