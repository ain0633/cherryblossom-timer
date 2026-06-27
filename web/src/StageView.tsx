import { useEffect } from 'react'

const N = 20
const urls = Array.from({ length: N }, (_, i) => `/stages/stage_${String(i).padStart(2, '0')}.jpg`)

const clamp = (x: number) => Math.max(0, Math.min(1, x))

// Pre-rendered Blender stages, cross-faded by bloom (1 = full blossom, 0 = bare)
export function StageView({ bloom }: { bloom: number }) {
  useEffect(() => {
    urls.forEach((u) => {
      const im = new Image()
      im.src = u
    })
  }, [])

  const pos = (1 - clamp(bloom)) * (N - 1)
  const i0 = Math.floor(pos)
  const i1 = Math.min(N - 1, i0 + 1)
  const blend = pos - i0

  return (
    <div className="stage">
      <img src={urls[i0]} className="stage-img" alt="" />
      <img src={urls[i1]} className="stage-img" style={{ opacity: blend }} alt="" />
    </div>
  )
}
