/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["oleorcarl/templates/**/*.html"],
  safelist: [
    // carleton colors
    "text-carleton-primary",
    "text-carleton-secondary",
    "text-carleton-tertiary",
    "bg-carleton-primary",
    "bg-carleton-secondary",
    "bg-carleton-tertiary",

    // stolaf colors
    "text-stolaf-primary",
    "text-stolaf-secondary",
    "text-stolaf-tertiary",
    "bg-stolaf-primary",
    "bg-stolaf-secondary",
    "bg-stolaf-tertiary",

    // bg images for both local development and github pages
    "bg-[url('/static/images/carleton_logo.svg')]",
    "bg-[url('/static/images/stolaf_logo.svg')]",
    "bg-[url('/oleorcarl/static/images/carleton_logo.svg')]",
    "bg-[url('/oleorcarl/static/images/stolaf_logo.svg')]",
  ],
  theme: {
    extend: {
      colors: {
        // adapted from pantone values
        // https://webtemple.io/all-pantone-c-colors-with-hex-and-rgb-codes/

        // https://wp.stolaf.edu/brand/files/2017/07/Typography-and-Color.pdf
        stolaf: {
          primary: "#CC8A00", // manitou (131)
          secondary: "#54585A", // heritage gray (425)
          tertiary: "#F2C75C", // prairie (141)
          // black: "#222223", // neutral black
        },

        // https://www.carleton.edu/communications/resources/college-wordmark-identity-graphics/college-colors/
        carleton: {
          primary: "#002F6C", // blue (294)
          secondary: "#dddddd",
          tertiary: "#FED141", // maize (122)
        },
        green: "#588745",
      },
    },
  },
  plugins: [require("tailwind-children"), require("tailwindcss-opentype")],
};
