const deployVersion = process.env.NEXT_PUBLIC_DEPLOY_VERSION ?? "local-dev";

const nextConfig = {
  output: "standalone",
  async headers() {
    return [
      {
        source: "/:path*",
        headers: [
          {
            key: "X-Intranet-Deploy-Version",
            value: deployVersion
          }
        ]
      }
    ];
  },
  experimental: {
    serverActions: {
      allowedOrigins: ["localhost:3000", "193.168.0.6:3000"]
    }
  }
};

export default nextConfig;
