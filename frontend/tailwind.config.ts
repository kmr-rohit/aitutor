import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{js,ts,jsx,tsx}", "./components/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#101323",
        signal: "#1f9d8f",
        accent: "#ff8a00",
        cream: "#f7f3ec",
      },
    },
  },
  plugins: [],
};

export default config;
