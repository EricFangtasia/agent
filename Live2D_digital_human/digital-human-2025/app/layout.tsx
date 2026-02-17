import './globals.css'

export const metadata = {
  title: '实时互动数字人',
  description: '基于 OpenAI Realtime API + Live2D · 2025最新技术',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <head>
        {/* Cubism Core必须同步加载 */}
        <script src="/libs/live2dcubismcore.min.js" />
        {/* 立即初始化全局变量 */}
        <script dangerouslySetInnerHTML={{
          __html: `
            // 将Cubism Core的所有内容展开到全局作用域
            if (typeof window !== 'undefined' && window.Live2DCubismCore) {
              for (let key in window.Live2DCubismCore) {
                if (window.Live2DCubismCore.hasOwnProperty(key)) {
                  window[key] = window.Live2DCubismCore[key];
                }
              }
              console.log('✅ Cubism Core 全局变量已展开');
            }
          `
        }} />
      </head>
      <body className="antialiasing">
        {children}
      </body>
    </html>
  )
}