const nextConfig = {
  output: "standalone",
  experimental: {
    serverActions: {
      allowedOrigins: ["localhost:3000", "193.168.0.6:3000"]
    }
  }
};

export default nextConfig;
