// Prefix runtime asset URLs with Vite's base so they resolve both locally ('/') and under
// GitHub Pages ('/Cherry-Blossom-Timer/'). import.meta.env.BASE_URL always ends with '/'.
export const asset = (p: string) => import.meta.env.BASE_URL + p.replace(/^\//, '')
