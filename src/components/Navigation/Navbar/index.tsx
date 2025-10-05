import { Button } from "../../ui/button"



const Navbar = () => {
  return (
    <header className="flex justify-between items-center py-4 px-4 lg:px-20">
        <h1 className="text-3xl md:text-4xl lg:text-5xl font-light-m-0">
            DETECTI
        </h1>

        <ul className="hidden md:flex items-center gap-12">
            <li>Detection</li>
            <li>Generate</li>
            <li>About Us</li>
        </ul>

        <Button className="hidden md:block py-2 px-8 rounded-full border-none 
          font-bold transition-all duration-500 cursor-pointer z-50">
            SIGNIN
        </Button>
      
    </header>
  )
}

export default Navbar
