/// <reference types="vite/client" />

// 1) 声明你会用到的环境变量（必须以 VITE_ 开头）
interface ImportMetaEnv {
  readonly VITE_API_BASE_URL: string
  readonly VITE_FEATURE_FLAG?: 'on' | 'off'
  // ...继续加你自己的
}

// 2) 把它挂到 ImportMeta 上
interface ImportMeta {
  readonly env: ImportMetaEnv
}

// 3) （可选）静态资源导入的类型，避免 “Cannot find module '*.jpg'”
declare module '*.png'  { const src: string; export default src }
declare module '*.jpg'  { const src: string; export default src }
declare module '*.jpeg' { const src: string; export default src }
declare module '*.webp' { const src: string; export default src }
declare module '*.gif'  { const src: string; export default src }
