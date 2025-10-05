import { BrowserRouter, Route, Routes } from "react-router-dom";
import Home from "./pages/Home";
import Theme from "./components/Navigation/Navbar/Theme";
import Navbar from "./components/Navigation/Navbar";
import Detection from "./pages/Detection";
import Generate from "./pages/Generate";
import About from "./pages/About";


const App = () => {
  return (
    <main>
      <Theme/>
      <Navbar/>

      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/Detection" element={<Detection />} />
        <Route path="/Generate" element={<Generate />} />
        <Route path="/About" element={<About />} />

      </Routes>
    </main>
  )
}

export default App
