import { useEffect, useRef } from 'react'

const clamp = (x: number) => Math.max(0, Math.min(1, x))

// Lightweight 2D falling-petal overlay (smooth motion on top of the pre-rendered stage)
export function PetalOverlay({ intensity }: { intensity: number }) {
  const ref = useRef<HTMLCanvasElement>(null)
  const inten = useRef(intensity)
  inten.current = intensity

  useEffect(() => {
    const cv = ref.current!
    const ctx = cv.getContext('2d')!
    let W = (cv.width = window.innerWidth)
    let H = (cv.height = window.innerHeight)
    const onResize = () => {
      W = cv.width = window.innerWidth
      H = cv.height = window.innerHeight
    }
    window.addEventListener('resize', onResize)

    const MAX = 280
    const mk = () => ({
      x: Math.random() * W,
      y: Math.random() * H,
      vy: 22 + Math.random() * 34,
      amp: 12 + Math.random() * 34,
      fr: 0.4 + Math.random() * 0.9,
      ph: Math.random() * 6.28,
      rot: Math.random() * 6.28,
      vr: (Math.random() * 2 - 1) * 2,
      s: 4 + Math.random() * 5,
      hue: 335 + Math.random() * 20,
    })
    const ps = Array.from({ length: MAX }, mk)

    let last = performance.now()
    let raf = 0
    const draw = (t: number) => {
      const dt = Math.min(0.05, (t - last) / 1000)
      last = t
      ctx.clearRect(0, 0, W, H)
      const vis = Math.floor(clamp(inten.current) * MAX)
      for (let i = 0; i < vis; i++) {
        const p = ps[i]
        p.y += p.vy * dt
        p.rot += p.vr * dt
        if (p.y > H + 12) {
          p.y = -12
          p.x = Math.random() * W
        }
        const x = p.x + Math.sin((t / 1000) * p.fr + p.ph) * p.amp
        ctx.save()
        ctx.translate(x, p.y)
        ctx.rotate(p.rot)
        ctx.fillStyle = `hsla(${p.hue}, 65%, 80%, 0.92)`
        ctx.beginPath()
        ctx.ellipse(0, 0, p.s * 0.62, p.s, 0, 0, 6.283)
        ctx.fill()
        ctx.restore()
      }
      raf = requestAnimationFrame(draw)
    }
    raf = requestAnimationFrame(draw)
    return () => {
      cancelAnimationFrame(raf)
      window.removeEventListener('resize', onResize)
    }
  }, [])

  return <canvas ref={ref} className="petal-canvas" />
}
