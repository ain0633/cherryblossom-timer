# 🌸 벚꽃이 지면 — Cherry Blossom Timer

> 꽃이 다 질 때까지 집중하는, 3D 벚꽃 뽀모도로 타이머.

**🔗 https://ainsof.dev/cherryblossom-timer**

집중 45분 동안 벚꽃이 한 잎씩 흩날려 떨어지고(낙화), 휴식 15분 동안 다시 만개합니다(개화).
시간의 흐름이 화면 속 벚꽃나무로 보이는, 조용하고 낭만적인 집중 도구예요.

## ✨ 특징

- **실시간 3D 벚꽃나무** — 집중하면 꽃잎이 나무에서 떨어져 바닥에 소복이 쌓입니다.
- **뽀모도로 흐름** — 집중 45분(낙화) ↔ 휴식 15분(개화). 한 단계가 끝나면 알람으로 알려줘요.
- **배경 나무도 함께** — 원경의 벚꽃나무들도 메인 나무에 맞춰 피고 집니다.
- Blender로 제작한 벚꽃나무 에셋을 웹으로 가져와 구현했습니다.

## 🛠 기술

React · TypeScript · Vite · React-Three-Fiber(Three.js) · drei
3D 에셋은 Blender(EEVEE/Cycles)로 제작 → glTF/Draco로 익스포트.

## 🚀 로컬 실행

```bash
cd web
npm install
npm run dev      # http://localhost:5173
```

## 📦 배포

`main` 브랜치에 푸시하면 GitHub Actions가 자동으로 빌드·배포합니다
(`.github/workflows/deploy.yml` → GitHub Pages, 커스텀 도메인 `ainsof.dev`).

---

🌳 Blender 에셋 제작 파이프라인과 상세 기획은 [CLAUDE.md](CLAUDE.md)와 [prd.md](prd.md) 참고.
