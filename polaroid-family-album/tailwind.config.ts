import type { Config } from 'tailwindcss'

const config: Config = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        polaroid: {
          cream: '#FFF8DC',
          shadow: '#E8E8E8',
          border: '#D3D3D3',
          vintage: '#F5F5DC'
        }
      },
      fontFamily: {
        polaroid: ['Courier New', 'monospace'],
      },
      boxShadow: {
        'polaroid': '0 4px 8px rgba(0,0,0,0.1), 0 6px 20px rgba(0,0,0,0.1)',
        'polaroid-hover': '0 8px 16px rgba(0,0,0,0.15), 0 12px 40px rgba(0,0,0,0.15)',
      }
    },
  },
  plugins: [],
}
export default config