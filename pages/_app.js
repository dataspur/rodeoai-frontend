import '../styles/globals.css'
import { useEffect, useState, createContext } from "react"

export const ThemeContext = createContext()

export default function App({ Component, pageProps }) {
  const [theme, setTheme] = useState("dark")

  useEffect(() => {
    document.body.setAttribute("data-theme", theme)
  }, [theme])

  return (
    <ThemeContext.Provider value={{ theme, setTheme }}>
      <Component {...pageProps} />
    </ThemeContext.Provider>
  )
}
