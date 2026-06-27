import { useEffect, useRef } from 'react'

const FRAMES = 150
const TIERS = 3 // 0 = sparse (near-empty tree), 2 = heavy (full tree)
const FPS = 24
const V = 3 // bump to bust the browser cache when petal frames are re-rendered
const clamp = (x: number) => Math.max(0, Math.min(1, x))
const urls = Array.from({ length: TIERS }, (_, ti) =>
  Array.from({ length: FRAMES }, (_, fi) => `/petals_seq/t${ti}/petal_${String(fi + 1).padStart(4, '0')}.png?v=${V}`)
)

// Blender-rendered falling petals, density crossfaded by `amount` (= remaining blossoms).
// Two playheads offset by half the loop, each with a triangular alpha (0 at its loop
// boundary, 1 at mid-loop) whose sum is ~1 everywhere -> the loop seam is never visible,
// so petals fall continuously with no stutter/restart.
export function PetalSequence({ amount }: { amount: number }) {
  const ref = useRef<HTMLCanvasElement>(null)
  const amt = useRef(amount)
  amt.current = amount

  useEffect(() => {
    const imgs = urls.map((tier) => tier.map((u) => { const im = new Image(); im.src = u; return im }))
    const cv = ref.current!
    const ctx = cv.getContext('2d')!
    let W = (cv.width = window.innerWidth)
    let H = (cv.height = window.innerHeight)
    const onResize = () => { W = cv.width = window.innerWidth; H = cv.height = window.innerHeight }
    window.addEventListener('resize', onResize)

    const drawFrame = (ti: number, frame: number, alpha: number) => {
      if (alpha <= 0.01) return
      const im = imgs[ti][frame]
      if (!im.complete || !im.naturalWidth) return
      const s = Math.max(W / im.naturalWidth, H / im.naturalHeight) // cover (matches stages)
      const dw = im.naturalWidth * s, dh = im.naturalHeight * s
      ctx.globalAlpha = alpha
      ctx.drawImage(im, (W - dw) / 2, (H - dh) / 2, dw, dh)
      ctx.globalAlpha = 1
    }

    const start = performance.now()
    let raf = 0
    const draw = (now: number) => {
      ctx.clearRect(0, 0, W, H)
      const a = clamp(amt.current)
      if (a > 0.02) {
        const pos = a * (TIERS - 1)
        const t0 = Math.floor(pos)
        const t1 = Math.min(TIERS - 1, t0 + 1)
        const b = pos - t0

        const phase = (((now - start) / 1000) * FPS) % FRAMES   // float playhead A
        const phaseB = (phase + FRAMES / 2) % FRAMES             // playhead B (half-loop offset)
        const wA = 1 - Math.abs((2 * phase) / FRAMES - 1)        // triangular: 0 at seam, 1 mid
        const wB = 1 - Math.abs((2 * phaseB) / FRAMES - 1)
        const fA = Math.floor(phase) % FRAMES
        const fB = Math.floor(phaseB) % FRAMES

        drawFrame(t0, fA, (1 - b) * wA); drawFrame(t1, fA, b * wA)
        drawFrame(t0, fB, (1 - b) * wB); drawFrame(t1, fB, b * wB)
      }
      raf = requestAnimationFrame(draw)
    }
    raf = requestAnimationFrame(draw)
    return () => { cancelAnimationFrame(raf); window.removeEventListener('resize', onResize) }
  }, [])

  return <canvas ref={ref} className="petal-canvas" />
}
