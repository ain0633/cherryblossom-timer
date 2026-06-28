import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// base must match the GitHub Pages path (https://<user>.github.io/Cherry-Blossom-Timer/).
// dev stays at '/' so `npm run dev` on localhost works unchanged.
// https://vite.dev/config/
export default defineConfig(({ command }) => ({
  base: command === 'build' ? '/Cherry-Blossom-Timer/' : '/',
  plugins: [react()],
}))
