import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// base must match the served path (https://ainsof.dev/cherryblossom-timer/).
// dev stays at '/' so `npm run dev` on localhost works unchanged.
// https://vite.dev/config/
export default defineConfig(({ command }) => ({
  base: command === 'build' ? '/cherryblossom-timer/' : '/',
  plugins: [react()],
}))
