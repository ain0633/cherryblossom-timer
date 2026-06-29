import { useEffect, useRef, useState, useCallback } from 'react'

export type Mode = 'focus' | 'break'
export type Durations = Record<Mode, number> // seconds
export const DEFAULT_DURATIONS: Durations = { focus: 45 * 60, break: 15 * 60 }
// user-settable bounds (seconds): 1 min .. 180 min
export const DURATION_BOUNDS = { min: 60, max: 180 * 60 }
const STORAGE_KEY = 'cbt-durations-v1'
const other = (m: Mode): Mode => (m === 'focus' ? 'break' : 'focus')
const clampDur = (s: number) =>
  Math.min(DURATION_BOUNDS.max, Math.max(DURATION_BOUNDS.min, Math.round(s)))

function loadDurations(): Durations {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    if (raw) {
      const d = JSON.parse(raw)
      if (typeof d?.focus === 'number' && typeof d?.break === 'number')
        return { focus: clampDur(d.focus), break: clampDur(d.break) }
    }
  } catch { /* ignore */ }
  return DEFAULT_DURATIONS
}

export type Completed = { ended: Mode; next: Mode; n: number }

export function usePomodoro() {
  // user-customizable phase lengths, persisted across visits
  const [durations, setDur] = useState<Durations>(loadDurations)
  const durationsRef = useRef(durations); durationsRef.current = durations
  const [mode, setMode] = useState<Mode>('focus')
  const [secondsLeft, setSecondsLeft] = useState(durations.focus)
  const [running, setRunning] = useState(false)
  const runningRef = useRef(running); runningRef.current = running
  // fires once each time a phase naturally completes (for chime + message)
  const [completed, setCompleted] = useState<Completed | null>(null)
  // manual scrub (0..1) for dev preview (hidden in the normal UI)
  const [scrub, setScrub] = useState<number | null>(null)
  const nCompleted = useRef<number>(0)
  // wall-clock endpoint: the phase ends at an absolute timestamp, so the timer
  // stays accurate while the tab is backgrounded (RAF stops, and throttled
  // timers can drift, but Date.now() never lies).
  const endAt = useRef<number>(0)
  // refs so start() reads live values without re-subscribing
  const modeRef = useRef(mode); modeRef.current = mode
  const secondsRef = useRef(secondsLeft); secondsRef.current = secondsLeft

  useEffect(() => {
    if (!running) return
    let done = false
    const finish = () => {
      if (done) return
      done = true
      // phase finished: STOP and wait for the user to start the next phase
      setRunning(false)
      setSecondsLeft(0)
      nCompleted.current += 1
      const ended = modeRef.current
      setCompleted({ ended, next: other(ended), n: nCompleted.current })
    }
    const check = () => {
      const remaining = (endAt.current - Date.now()) / 1000
      if (remaining <= 0) { finish(); return }
      setSecondsLeft(remaining)
    }
    check()
    // interval keeps the display fresh and detects completion even in a hidden
    // tab (browsers throttle these but never stop them the way they stop RAF).
    const interval = window.setInterval(check, 250)
    // a single long timeout fires the chime close to on-time even when the tab
    // is deeply throttled (the interval may be clamped to ~1/min in background).
    const timeout = window.setTimeout(finish, Math.max(0, endAt.current - Date.now()))
    // instant catch-up the moment the user returns to the tab.
    const onVis = () => { if (document.visibilityState === 'visible') check() }
    document.addEventListener('visibilitychange', onVis)
    return () => {
      window.clearInterval(interval)
      window.clearTimeout(timeout)
      document.removeEventListener('visibilitychange', onVis)
    }
  }, [running])

  // start: if the current phase is finished (00:00), advance to the next phase first; else resume.
  const start = useCallback(() => {
    let secs = secondsRef.current
    if (secs <= 0) {
      const nm = other(modeRef.current)
      setMode(nm); secs = durationsRef.current[nm]; setSecondsLeft(secs); setScrub(null)
    }
    endAt.current = Date.now() + secs * 1000
    setRunning(true)
  }, [])
  const pause = useCallback(() => setRunning(false), [])
  const reset = useCallback(() => {
    setRunning(false); setMode('focus'); setSecondsLeft(durationsRef.current.focus); setScrub(null)
  }, [])

  // update phase lengths (seconds); persists and, while idle, updates the clock now.
  const setDurations = useCallback((next: Durations) => {
    const clamped: Durations = { focus: clampDur(next.focus), break: clampDur(next.break) }
    setDur(clamped)
    try { localStorage.setItem(STORAGE_KEY, JSON.stringify(clamped)) } catch { /* ignore */ }
    if (!runningRef.current) { setSecondsLeft(clamped[modeRef.current]); setScrub(null) }
  }, [])

  const liveProgress = 1 - secondsLeft / durations[mode] // 0..1 within current mode
  const progress = scrub != null ? scrub : liveProgress

  // bloom: 1 = full canopy, 0 = bare. LINEAR so half the time -> half the blossoms.
  // focus: blossoms fall (1 -> 0). break: blossoms return (0 -> 1).
  const bloom = mode === 'focus' ? 1 - progress : progress

  // ground carpet: accumulates ONLY during focus; cleared the moment a break begins.
  const carpet = mode === 'focus' ? 1 - bloom : 0

  // phase finished and waiting for the user to start the next one (shows the next phase, paused)
  const phaseDone = !running && secondsLeft <= 0
  const nextMode = other(mode)

  // preview: jump to a phase without running the clock (local verification bar)
  const preview = useCallback((m: Mode, value: number) => {
    setRunning(false); setMode(m); setSecondsLeft(durationsRef.current[m] * (1 - value)); setScrub(value)
  }, [])

  return { mode, secondsLeft, running, progress, bloom, carpet, completed, phaseDone, nextMode,
           durations, setDurations, start, pause, reset, scrub, setScrub, preview }
}
