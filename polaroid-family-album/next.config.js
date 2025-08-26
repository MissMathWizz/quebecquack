/** @type {import('next').NextConfig} */
const nextConfig = {
  images: {
    domains: ['replicate.delivery', 'pbxt.replicate.delivery'],
  },
  experimental: {
    serverActions: true,
  },
}

module.exports = nextConfig