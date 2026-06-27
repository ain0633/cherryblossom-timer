import { useEffect, useRef, useState } from 'react'
import { StageView } from './StageView'
import { PetalsLive } from './PetalsLive'
import { usePomodoro } from './usePomodoro'
import { playChime } from './sound'

function fmt(s: number) {
  const m = Math.floor(s / 60)
  const ss = Math.floor(s % 60)
  return `${String(m).padStart(2, '0')}:${String(ss).padStart(2, '0')}`
}

export default function App() {
  const t = usePomodoro()
  // petals fall in proportion to the blossoms still on the tree; none during break
  const petalAmount = t.mode === 'focus' ? t.bloom : 0

  const [toast, setToast] = useState<string | null>(null)
  const toastTimer = useRef<number>(0)

  // phase-transition alarm: chime + message (PRD 3.1)
  useEffect(() => {
    if (!t.completed) return
    playChime()
    const msg = t.completed.ended === 'focus'
      ? '낙화가 완료되었습니다. 잠시 쉬어가세요.'
      : '다시 꽃이 만개했습니다. 집중할 시간입니다.'
    setToast(msg)
    window.clearTimeout(toastTimer.current)
    toastTimer.current = window.setTimeout(() => setToast(null), 6000)
  }, [t.completed?.n])

  return (
    <>
      <StageView bloom={t.bloom} />
      <PetalsLive amount={petalAmount} />

      {toast && <div className="toast">{toast}</div>}

      {/* local preview bar: scrub the bloom and switch phase to verify the animation */}
      <div className="preview">
        <div className="preview-modes">
          <button className={t.mode === 'focus' ? 'on' : ''}
            onClick={() => t.preview('focus', t.scrub ?? 0)}>집중(낙화)</button>
          <button className={t.mode === 'break' ? 'on' : ''}
            onClick={() => t.preview('break', t.scrub ?? 0)}>휴식(개화)</button>
        </div>
        <input type="range" min={0} max={1} step={0.005}
          value={t.progress}
          onChange={(e) => t.preview(t.mode, parseFloat(e.target.value))} />
        <span className="preview-val">개화 {Math.round(t.bloom * 100)}%</span>
      </div>

      <div className="hud">
        <div className="mode" data-mode={t.mode}>{t.mode === 'focus' ? '집중' : '휴식'}</div>
        <div className="time">{fmt(t.secondsLeft)}</div>
        <div className="buttons">
          {t.running ? (
            <button onClick={t.pause}>일시정지</button>
          ) : (
            <button className="primary" onClick={t.start}>시작</button>
          )}
          <button onClick={t.reset}>리셋</button>
        </div>
      </div>
    </>
  )
}
