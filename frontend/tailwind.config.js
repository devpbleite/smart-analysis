/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        chatBg: '#0e1117',      /* Fundo da Tela Streamlit */
        panel: '#262730',       /* Sidebar e Caixa de Input Streamlit */
        userMsg: '#2b313e',     /* Fundo suave para mensagem do usuario */
        botMsg: '#ff4b4b',      /* Cor primária clásica vermelha do Streamlit */
        botTextMsg: '#ffffff'   /* Texto claro */
      }
    },
  },
  plugins: [
    require('@tailwindcss/typography'),
  ],
}
