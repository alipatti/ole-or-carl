/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["src/app/**/*.html*"],
  safelist: [
    "text-carleton-maize",
    "bg-carleton-blue",
    "bg-carleton-maize",
    "text-stolaf-black",
    "bg-stolaf-manitou",
    "bg-stolaf-black",
    "bg-logo-stolaf",
    "bg-logo-carleton",
  ],
  theme: {
    extend: {
      colors: {
        stolaf: {
          manitou: "#e1a026",
          prairie: "#fec55e",
          grey: "#55575a",
          black: "#222222",
        },
        carleton: {
          blue: "#003e7e",
          maize: "#ffd24f",
          maizeDark: "#ee8111",
          maizeLight: "#ffefc8",
          blueLight: "#2d538f",
        },
      },
      backgroundImage: {
        'logo-stolaf': "url('/static/images/stolaf_logo.jpg')",
        'logo-carleton': "url('/static/images/carleton_logo_blue.svg')",
      }
    },
  },
  plugins: [
    require("tailwind-children"),
    require("tailwindcss-opentype"),
  ],
};
