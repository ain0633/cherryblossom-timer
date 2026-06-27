// Lightweight Web Audio: a soft chime for phase transitions (PRD alarm).
let ctx: AudioContext | null = null
function ac(): AudioContext {
  if (!ctx) ctx = new (window.AudioContext || (window as any).webkitAudioContext)()
  if (ctx.state === 'suspended') ctx.resume()
  return ctx
}

// gentle two-note bell
export function playChime() {
  const a = ac()
  const now = a.currentTime
  const notes = [880, 1174.7] // A5, D6
  notes.forEach((f, i) => {
    const o = a.createOscillator()
    const g = a.createGain()
    o.type = 'sine'
    o.frequency.value = f
    const t0 = now + i * 0.18
    g.gain.setValueAtTime(0, t0)
    g.gain.linearRampToValueAtTime(0.22, t0 + 0.03)
    g.gain.exponentialRampToValueAtTime(0.0001, t0 + 1.6)
    o.connect(g); g.connect(a.destination)
    o.start(t0); o.stop(t0 + 1.7)
  })
}
