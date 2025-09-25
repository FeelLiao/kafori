// tailwind.config.js
const { fontFamily } = require('tailwindcss/defaultTheme')

module.exports  = {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  darkMode: 'class', // 启用基于类的暗色模式
  theme: {
    opacities: {
      100: "1",
      80: ".80",
      60: ".60",
      40: ".40",
      20: ".20",
      10: ".10",
      5: ".05",
    },
    sizes: {
      1: "0.25rem",
      2: "0.5rem",
      4: "1rem",
      6: "1.5rem",
      8: "2rem",
      16: "4rem",
      20: "5rem",
      24: "6rem",
      32: "8rem",
    },

    extend: {
      colors: {
        // 生物数据专用色板
        dna: {
          primary: '#2e7d32',
          secondary: '#6a1b9a',
          helix: '#2196f3',
          cytosine: '#ff9800',
          adenine: '#f44336',
          guanine: '#4caf50',
          thymine: '#9c27b0'
        },
      },
      fontFamily: {
        scientific: ['"Fira Code"', ...fontFamily.mono],
      },
      backgroundImage: {
        'dna-pattern': "url('@/assets/dna-bg.svg')",
        'cell-pattern': "radial-gradient(circle, rgba(46,125,50,0.1) 1px, transparent 1px)"
      },
      backgroundSize: {
        'bio': '40px 40px'
      }
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
    require('@tailwindcss/typography'),
    require('tailwindcss-bg-patterns'),
  ]
}