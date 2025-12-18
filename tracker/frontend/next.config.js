import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // images: { unoptimized: true },
  output: "standalone",
  productionBrowserSourceMaps: true,
  reactCompiler:true,
  turbopack: {
    rules: {
      "*.svg": {
        as: "*.ts",
        loaders: ["@svgr/webpack"],
      },
    },
  },
  webpack(config) {
    config.module.rules.push({
      test: /\.svg$/i,
      use: ["@svgr/webpack"],
    });
    return config;
  },
};

export default nextConfig;
