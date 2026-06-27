# CLAUDE.md — 봄이 오는 시간 (Cherry Blossom Timer)

웹 3D 뽀모도로 타이머 프로젝트. 집중 45분 = 낙화(꽃잎 떨어짐), 휴식 15분 = 개화.
상세 기획은 [prd.md](prd.md). 최종 목표는 **웹(Three.js + React Three Fiber)** 실행이며,
현재는 **Blender로 벚꽃나무 3D 에셋을 제작하는 단계**다 (웹 코드는 아직 없음).

---

## Blender 연결 방법 (중요 — 먼저 읽기)

`mcp__blender__*` MCP 브리지는 이 PC에서 **깨져 있다** (`Not connected`).
원인: `localhost`가 IPv6(`::1`)로 먼저 풀리는데 Blender 애드온은 `127.0.0.1`(IPv4)만 리스닝.
애드온 자체는 정상 (포트 9876).

**우회 = raw IPv4 소켓으로 직접 구동:**
- 헬퍼: `_tools/blender_send.ps1` — .py 파일을 읽어 `{"type":"execute_code",...}`를 `127.0.0.1:9876`로 전송.
  - 호출: `& "_tools/blender_send.ps1" -CodeFile "_tools/<script>.py" -TimeoutMs 590000`
  - ⚠️ 파일은 `[System.IO.File]::ReadAllText`로 읽어야 함 (`Get-Content -Raw`는 메타가 붙어 깨짐).
- 결과 확인: Blender에서 PNG로 렌더 → Read 툴로 이미지 확인. (뷰포트 스크린샷 MCP도 브리지라 못 씀)
- **뷰포트가 SOLID 모드면 재질/색/꽃 분홍이 안 보인다** → Material Preview / Rendered 로 봐야 함.

**환경:** Blender 5.1.2 · 렌더 엔진 `BLENDER_EEVEE` · 뷰변환 **Standard**(AgX는 탈색됨) ·
카메라 `clip_end=1000`(스카이돔 안 잘리게) · **FFMPEG 없음**(이미지 시퀀스만 출력 가능).

---

## 제작 스크립트 (`_tools/`, 실행 순서)

1. **step1.py** — 나무 목질 골격. 엣지 스켈레톤 + Skin + Subsurf + Corrective Smooth.
   `branch()`가 가지 밑동에 **칼라(collar)**를 붙여 둥치에서 자연스럽게 흘러나오게 함.
   상부 **+Z 가지**로 정수리까지 채움. (재실행 시 BarkMat은 보존됨)
2. **petal_lib.py** — 공용 라이브러리(다른 스크립트가 `exec`로 불러씀).
   난형 꽃잎(끝 작은 V노치, 컵형) → 꽃(5장) → 군집. `petal_geom / bud_geom / build_cluster / blossom_material`.
   이 **꽃잎 메쉬가 캐노피와 낙화에 공용**.
3. **step2b.py** — 만개 캐노피. 가는 가지 노드에서 시드 추출 → 6색 변형 군집을 **정점 인스턴싱**.
   `CLUSTER_SCALE=0.056`(작은 꽃), `BLOSSOM_DENSITY`(0~1, **낙화 연동용 파라미터**). 현재 ~62만 인스턴스.
4. **step3_bark.py** — 절차적 벚나무 수피: 세로 Voronoi 주름 + 결 노이즈 + 가로 피목(끊긴 점선) + 강한 범프.
5. **step4_env.py** — 환경: 청록 그라데이션 스카이돔, 황금 잔디, 원경 벚꽃나무 26그루(줄기+수관), 따뜻한 sun.
6. **step5_petals.py** — 정적 낙화/누적 스틸(현재 step6로 대체, 미사용).
7. **step6_wind.py** — **공중 낙화 파티클 시뮬**: 약한 바람 + 살랑 난류 + 항력으로 지그재그 하강.
   넓은 평면(z6.5, 14x14)에서 face 방출, `count=2500/frame_end130`(≈19/frame, "양 적당" 승인됨),
   `gravity 0.8 / drag 0.12`(낮은 항력이라야 바닥에 닿음). `SIZE=0.10`. `ADD_GUST` 플래그(현재 False).
8. **ground_carpet.py** — **바닥 누적 카펫**: 작은 꽃잎 4,500장을 잔디에 직접 깔아 누적을 확실히 보이게(중심부 밀집).
   ⚠️ Blender 파티클 누적은 **점캐시가 신뢰성 있게 갱신 안 돼** 튜닝 비효율 → 누적은 파티클이 아닌 이 정적 카펫으로 처리(하이브리드). step6_wind 클린업이 "GroundCarpet"은 안 지움.
9. **step6b_anim.py** — 캐노피 숨기고 1~150프레임 PNG 시퀀스 렌더 → `renders/seq/`. (renders 순서: ground_carpet → step6_wind → step6b_anim)
10. **step7_stages.py** — `BLOSSOM_DENSITY` 단계 연동 데모: 만개(1.0/카펫250)→절반(0.5/2400)→앙상(0.12/4800) 3컷을 환경 유지한 채 렌더 → `renders/stage_{full,half,empty}.png`. (캐노피 build_canopy(density)/build_carpet(n) 함수로 step2b 로직 재사용)
9. **make_gif.ps1** — PNG 시퀀스 → 애니메이션 GIF(.NET GDI+). 경로는 **-Seq/-Out 인자로 전달**(파일 내 한글 리터럴 금지). `-MaxW`,`-Stride`로 경량화.
- 확인용: render_full.py, closeup.py, junction_closeup.py, diag_particles.py, verify_frame.py.

---

## 진행 상황 (2026-06-23)

**완료:** 나무 골격+자연스러운 이음새, 사실적 벚꽃잎/꽃/군집, 풍성한 만개 캐노피,
사실적 회갈색 수피(가로 피목+세로 주름), 환경(청록 하늘/황금 잔디/원경 나무/오후 햇살),
낙화 파티클(돌풍 없는 살랑바람·느린 지그재그 하강·얇은 누적·꽃잎 절반 크기).

**마지막 작업(완료):** 공중 낙화(파티클) + 바닥 누적(정적 카펫) 하이브리드 확정. 양·속도·카펫 밀도 사용자 승인.
`renders/petal_fall.gif`(150프레임) / `_small.gif` 생성, `cherry_blossom.blend` 저장 완료.

**v5 업그레이드(완료):** ①수형=문어형 폐기→`grow()` 재귀 분기로 자연스러운 둥근 크라운(둥치 2.8·주가지6+중앙3·depth2). ②낙화=수평 바람 0.04로 낮춰 나무 바로 밑으로 하강. ③배경=레퍼런스2 적용: 파란 하늘+흰 뭉게구름(노이즈 normalize), 싱그러운 초록 초원+들꽃+완만한 구릉(Subsurf SIMPLE+Displace CLOUDS), 초록 원경나무(분홍 22%). ④카메라 뒤로(loc (0,-40,5.5) lens40)로 나무가 화면 ~절반. ⑤웹 bloom 곡선 `(1-progress)^0.85`(20분 남으면 ~절반). render_stages/render_petal_tiers 카메라 동기화. 웹 전체 재렌더 완료.

**이전 레퍼런스 매칭(참고):** ①수형=낮게 분기·넓은 우산형·늘어지는 가지(step1 trunk 2.4/primaries up 0.5~0.95·spread×1.5·nprim12) ②수피=붉은 고목+밑동 이끼(step3_bark) ③꽃=CLUSTER_SCALE 0.072·진분홍 TINTS·12% 진분홍 산포(render_stages/framing_test) ④잔디 황금빛·원경 38그루(step4_env). step1이 모든 메쉬를 지우므로 재실행 시 step4_env→render_stages→step6_wind→render_petal_tiers 순으로 재구성. 웹 에셋 전체 재렌더 완료.

---

## 웹 빌드 (`web/`)

Vite + React + TS + **React-Three-Fiber + drei**. 실행: `cd web && npm run dev` (http://localhost:5173).
미리보기 MCP용 `.claude/launch.json`(name `cherry-web`, `npm --prefix web run dev`) 있음.

**에셋 파이프라인 (Blender → `web/public/assets/`):**
- `export_web_assets.py` — 꽃 위치 `blossoms.json`(~15,000, Z-up→Y-up 변환 `[x, z, -y]`, 그룹별 색) + 단일 꽃 `flower.glb`.
- `export_flower.py` — 꽃 GLB 재익스포트(정점 컬러 그라데이션 포함; 머티리얼이 Col을 써야 COLOR_0 익스포트됨, `export_vertex_color='ACTIVE'`).
- `bake_bark.py` — 절차적 수피를 **베이크**: 둥치 복제→모디파이어 적용→데시메이트0.3→Smart UV→Cycles로 base color(DIFFUSE/COLOR) + normal 베이크 → 이미지 머티리얼로 `trunk.glb` 익스포트(Draco). (~2.7MB)
- `export_trunk_opt.py` — 수피 없이 단색 둥치 빠른 익스포트(구버전, 참고용).
- Draco 디코더는 `web/public/draco/`에 복사됨(three 번들), `useGLTF(url,'/draco/')`.

**웹 구조 (현재 = 사전 렌더 플립북, 사용자 선택):** 실시간 3D는 Blender 근사치라, "Blender 그대로"를 위해 **사전 렌더 방식**으로 전환.
- `render_stages.py` — 만개→앙상 20단계(밀도↓·카펫↑)를 메인 카메라로 고품질 렌더 → `web/public/stages/stage_00..19.jpg`(**16:9 1600×900**, 공중 낙화는 숨김). 카메라는 뒤로 뺀 와이드 구도(loc (0,-30,5), lens 50)로 나무 전체+여백. `render_petal_tiers.py`도 동일 카메라+1280×720으로 정렬.
- `render_petal_tiers.py` — 낙화를 **3단계 밀도**(t0/t1/t2)로 메인 카메라·투명배경 렌더 → `web/public/petals_seq/t0..t2/petal_0001..0150.png`(1280×720). **방출 평면은 넓은 캐노피 전체(±11, z8)** (step6_wind, 옛 좁은 z6.5는 중앙 띠 버그). **음수 프레임(-60)부터 워밍업** 후 1~150만 저장 → 1프레임부터 꽉 차서 루프 끊김 없음(연속 낙화). 타일 카운트 [1500/6000/12000].
- **낙화 = 실시간 3D로 전환(중요).** 사전렌더 영상(PetalSequence)은 "따로 노는/루프/누적 없음" 한계로 폐기 → `PetalsLive.tsx`(투명 R3F Canvas 오버레이). Blender 스테이지 카메라(loc(0,-40,5.5) lens40 16:9)를 three에서 재현(CamRig: hfov 48.5° 매칭, cover 보정). 캐노피(반경~8.5, y4~13)에서 InstancedMesh 꽃잎이 실제로 낙하→바닥(y0) 착지·resting→재활용. **무한 연속·bloom 비례(amount=focus?bloom:0)·실제 누적**. meshBasicMaterial+instanceColor(분홍 4색), vertexColors 금지(인스턴스컬러 가림). petals_seq/render_petal_tiers는 이제 미사용.
- 벚꽃 **몽환적 밝기**: blossom_material에 Emission(Col 링크, strength 0.28) + render_stages `view_settings.exposure=0.35`. blossom_material()은 매번 재생성해야 발광 반영.
- `App.tsx` → `StageView`(bloom 크로스페이드) + `PetalsLive`(amount=bloom) + HUD. `usePomodoro.ts`(45/15분, bloom=`(1-progress)^0.85`, 미리보기 스크럽).
- 비주얼=Blender 100% 동일, 가벼움(JPG ~수MB), 단 카메라 고정.
- 구버전 실시간 3D 컴포넌트(`scene/`, Tree/Blossoms/Petals/SkyDome/Ground/DistantTrees)는 미사용으로 보존(참고/대안용). trunk.glb/flower.glb/blossoms.json도 그 용도.

## 다음 할 일

- (완료) 낙화 양/속도, 바닥 카펫, `BLOSSOM_DENSITY` 단계 연동(step7_stages) — 사용자 승인.
- (완료) 웹 v1: 씬·타이머·밀도연동·낙화, 꽃잎 색 그라데이션, 베이크 수피.
- 웹 다듬기: 바닥 누적 카펫(밀도연동), 알파 텍스처 꽃잎, 알람/사운드, 모바일 대응, 번들 코드분할.
- **웹 빌드** ← 다음 주요 단계: GLB 익스포트 + **폴리곤 최적화**(현재 수천만, 웹에 과중) → Three.js/R3F 씬,
  타이머 로직(45/15분), 낙화·누적·밀도연동을 웹 GPU 파티클로 실시간 재구현, 알람/사운드.
- (선택) "쌓인 꽃잎이 살랑바람에 다시 날림"은 웹에서 처리(Blender 파티클 캐시 한계로 보류).

## 주의점

- **단일 프레임 렌더는 파티클 캐시 때문에 부정확**. 시퀀스(`animation=True`)나 프레임을 1부터 순차 `frame_set` 한 뒤 측정할 것.
- 폴리곤이 매우 무거움 → 웹 익스포트 전 최적화 필수.
- 렌더가 도는 동안 Blender가 점유되어 소켓 명령이 막힘. 저장/추가 명령은 렌더 완료 후.
