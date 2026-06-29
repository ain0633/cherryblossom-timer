import { useEffect, useRef, useState } from 'react'
import { Scene } from './scene/Scene'
import { usePomodoro, DURATIONS } from './usePomodoro'
import { playChime, notify, requestNotifyPermission } from './sound'

function fmt(s: number) {
  const m = Math.floor(s / 60)
  const ss = Math.floor(s % 60)
  return `${String(m).padStart(2, '0')}:${String(ss).padStart(2, '0')}`
}

export default function App() {
  const t = usePomodoro()
  // petals fall in proportion to the blossoms still on the tree; none during break
  const petalAmount = t.mode === 'focus' ? t.bloom : 0
  // when a phase just finished, show the NEXT phase ready (paused) so 「시작」 starts it
  const dispMode = t.phaseDone ? t.nextMode : t.mode
  const dispSeconds = t.phaseDone ? DURATIONS[t.nextMode] : t.secondsLeft

  const [toast, setToast] = useState<string | null>(null)
  const toastTimer = useRef<number>(0)

  // dev-only scrub bar: hidden normally, shown when the URL hash is #dev
  const showDev = typeof window !== 'undefined' && window.location.hash === '#dev'

  // first-visit intro (re-openable via the ? button). gated by localStorage.
  const [showIntro, setShowIntro] = useState(() => {
    try { return !localStorage.getItem('cbt-intro-v1') } catch { return true }
  })
  const closeIntro = () => {
    setShowIntro(false)
    try { localStorage.setItem('cbt-intro-v1', '1') } catch { /* ignore */ }
  }

  // phase-transition alarm: chime + system notification + on-screen message (PRD 3.1)
  useEffect(() => {
    if (!t.completed) return
    playChime()
    const focus = t.completed.ended === 'focus'
    const msg = focus
      ? '집중 완료! 낙화가 끝났어요. 「휴식 시작」을 눌러 쉬어가세요.'
      : '휴식 완료! 다시 꽃이 만개했어요. 「집중 시작」을 눌러보세요.'
    // system notification reaches the user even on another tab/app
    notify(focus ? '🌸 집중 완료 — 휴식 시간이에요' : '🌸 휴식 완료 — 집중할 시간이에요', msg)
    setToast(msg)
    window.clearTimeout(toastTimer.current)
    toastTimer.current = window.setTimeout(() => setToast(null), 6000)
  }, [t.completed?.n])

  // request notification permission on the first explicit start (user gesture)
  const handleStart = () => { requestNotifyPermission(); t.start() }

  return (
    <>
      <Scene bloom={t.bloom} petalAmount={petalAmount} carpetAmount={t.carpet} />

      {toast && <div className="toast">{toast}</div>}

      <button className="help-btn" onClick={() => setShowIntro(true)} aria-label="도움말">?</button>

      {showIntro && (
        <div className="intro-backdrop" onClick={closeIntro}>
          <div className="intro-card" onClick={(e) => e.stopPropagation()}>
            <div className="intro-emoji">🌸</div>
            <h1 className="intro-title">벚꽃이 지면</h1>
            <p className="intro-sub">꽃이 다 질 때까지 집중하는 뽀모도로 타이머</p>
            <div className="intro-lines">
              <p><b>집중 45분</b> · 꽃잎이 하나둘 흩날려요 <span>낙화</span></p>
              <p><b>휴식 15분</b> · 다시 벚꽃이 피어나요 <span>개화</span></p>
            </div>
            <p className="intro-foot">
              「시작」을 누르면 시간이 흐르기 시작하고,<br />
              한 단계가 끝나면 가만히 알려드릴게요.
            </p>
            <button className="intro-btn" onClick={closeIntro}>시작하기</button>
          </div>
        </div>
      )}

      {/* dev-only preview bar (scrub bloom + switch phase): visible only at #dev */}
      {showDev && (
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
      )}

      <div className="hud">
        <div className="mode" data-mode={dispMode}>{dispMode === 'focus' ? '집중' : '휴식'}</div>
        <div className="time">{fmt(dispSeconds)}</div>
        <div className="buttons">
          {t.running ? (
            <button onClick={t.pause}>일시정지</button>
          ) : (
            <button className="primary" onClick={handleStart}>시작</button>
          )}
          <button onClick={t.reset}>리셋</button>
        </div>
      </div>
    </>
  )
}
