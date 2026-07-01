import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { VitePWA } from 'vite-plugin-pwa'

// base must match the served path (https://ainsof.dev/cherryblossom-timer/).
// dev stays at '/' so `npm run dev` on localhost works unchanged.
// https://vite.dev/config/
export default defineConfig(({ command }) => ({
  base: command === 'build' ? '/cherryblossom-timer/' : '/',
  plugins: [
    react(),
    // installable PWA: "홈 화면에 추가"로 앱처럼 전체화면 실행 + 오프라인.
    VitePWA({
      registerType: 'autoUpdate',
      includeAssets: ['favicon.svg', 'pwa-icon.svg'],
      manifest: {
        name: '벚꽃이 지면',
        short_name: '벚꽃타이머',
        description: '꽃이 다 질 때까지 집중하는 3D 벚꽃 뽀모도로 타이머',
        lang: 'ko',
        theme_color: '#e79bb4',
        background_color: '#f5d9e2',
        display: 'standalone',
        orientation: 'any',
        icons: [
          { src: 'pwa-icon.svg', sizes: 'any', type: 'image/svg+xml', purpose: 'any' },
          { src: 'pwa-icon.svg', sizes: 'any', type: 'image/svg+xml', purpose: 'maskable' },
        ],
      },
      workbox: {
        // app shell is precached; the heavy 3D assets are cached on first use
        // (CacheFirst) so the app still works offline without a huge install.
        globPatterns: ['**/*.{js,css,html,svg,woff2}'],
        runtimeCaching: [
          {
            urlPattern: /\.(?:glb|json|png|jpe?g|bin)$/i,
            handler: 'CacheFirst',
            options: {
              cacheName: 'cbt-assets-v1',
              expiration: { maxEntries: 80, maxAgeSeconds: 60 * 60 * 24 * 30 },
              cacheableResponse: { statuses: [0, 200] },
            },
          },
        ],
      },
    }),
  ],
}))
