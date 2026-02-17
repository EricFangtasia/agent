/** @type {import('next').NextConfig} */
const nextConfig = {
  experimental: {
    // Next.js 15新特性
    turbo: {
      resolveAlias: {
        canvas: './empty-module.ts',
      },
    },
  },
  webpack: (config) => {
    // 处理PixiJS和Live2D的特殊需求
    config.externals = config.externals || [];
    config.externals.push({
      canvas: 'canvas',
    });
    return config;
  },
};

module.exports = nextConfig;
