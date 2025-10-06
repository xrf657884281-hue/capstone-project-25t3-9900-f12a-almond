import { Route, Routes } from "react-router-dom";
import Navbar from "./components/Navigation/Navbar";
import { NavRoutes } from "./constants";


const App = () => {
  return (
    <main>
      <Navbar/>

      <Routes>
        {NavRoutes.map((route) => (
          <Route key={route.path} path={route.path} element={route.element} />
        ))}
    </Routes>
    </main>
  )
}

export default App
