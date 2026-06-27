import { useEffect, useRef, useState, useCallback } from 'react'

export type Mode = 'focus' | 'break'
export const DURATIONS: Record<Mode, number> = { focus: 45 * 60, break: 15 * 60 }

export type Completed = { ended: Mode; next: Mode; n: number }

export function usePomodoro() {
  const [mode, setMode] = useState<Mode>('focus')
  const [secondsLeft, setSecondsLeft] = useState(DURATIONS.focus)
  const [running, setRunning] = useState(false)
  // fires once each time a phase naturally completes (for chime + message)
  const [completed, setCompleted] = useState<Completed | null>(null)
  // manual scrub (0..1) for dev preview (hidden in the normal UI)
  const [scrub, setScrub] = useState<number | null>(null)
  const raf = useRef<number>(0)
  const last = useRef<number>(0)
  const nCompleted = useRef<number>(0)

  useEffect(() => {
    if (!running) return
    last.current = performance.now()
    const tick = (now: number) => {
      const dt = (now - last.current) / 1000
      last.current = now
      setSecondsLeft((s) => {
        const next = s - dt
        if (next <= 0) {
          setMode((m) => {
            const nm: Mode = m === 'focus' ? 'break' : 'focus'
            setSecondsLeft(DURATIONS[nm])
            nCompleted.current += 1
            setCompleted({ ended: m, next: nm, n: nCompleted.current })
            return nm
          })
          return 0
        }
        return next
      })
      raf.current = requestAnimationFrame(tick)
    }
    raf.current = requestAnimationFrame(tick)
    return () => cancelAnimationFrame(raf.current)
  }, [running])

  const start = useCallback(() => setRunning(true), [])
  const pause = useCallback(() => setRunning(false), [])
  const reset = useCallback(() => {
    setRunning(false); setMode('focus'); setSecondsLeft(DURATIONS.focus); setScrub(null)
  }, [])

  const liveProgress = 1 - secondsLeft / DURATIONS[mode] // 0..1 within current mode
  const progress = scrub != null ? scrub : liveProgress

  // bloom: 1 = full canopy, 0 = bare. LINEAR so half the time -> half the blossoms.
  // focus: blossoms fall (1 -> 0). break: blossoms return (0 -> 1).
  const bloom = mode === 'focus' ? 1 - progress : progress

  // preview: jump to a phase without running the clock (local verification bar)
  const preview = useCallback((m: Mode, value: number) => {
    setRunning(false); setMode(m); setSecondsLeft(DURATIONS[m] * (1 - value)); setScrub(value)
  }, [])

  return { mode, secondsLeft, running, progress, bloom, completed,
           start, pause, reset, scrub, setScrub, preview }
}
