import { navItems } from "../../../constants"
import { Button } from "../../ui/button"

import { Link, useNavigate } from "react-router-dom"
import Theme from "./Theme"
import MobileNavigarion from "../MobileNavigarion"

const Navbar = () => {
    const navigate = useNavigate()
  return (
    <header className="flex justify-between items-center px-4 lg:px-20 py-4 relative">
      {/* Logo / Brand */}
      <h1 className="text-3xl md:text-4xl lg:text-5xl font-light m-0">
        <Link to="/">DETECTI</Link>
      </h1>

      {/* 中间菜单（md 及以上） */}
      <ul className="hidden md:flex items-center gap-12 mx-auto">
        {navItems.map((item) => (
          <li key={item.path}>
            <Link to={item.path}>{item.label}</Link>
          </li>
        ))}
      </ul>

      <div className="flex items-center space-x-4">

        <Button 
          className="hidden md:block py-2 px-8 rounded-full border-none font-bold transition-all duration-500 cursor-pointer z-50"
          onClick={() => navigate('/sign-in')}
        >
          SIGNIN
        </Button>


        <Theme />


        <MobileNavigarion />
      </div>
    </header>
  )
}

export default Navbar
