import { Book, ExternalLink } from "lucide-react"
import { Link } from "react-router-dom"
import { Button } from "./ui/button"
import Spline from '@splinetool/react-spline'


const Hero = () => {
  return (
    <main className='relative flex lg:mt-20 flex-col lg:flex-row items-center justify-between min-h-[calc(90vh-6rem)] overflow-hidden'>
        <div className="max-w-xl ml-[5%] z-10 mt-[90%] md:mt-[60%] lg:mt-[-8%] lg:ml-[13%]">
            <Link to="/about">
              <div className="relative w-[95%] sm:w-48 h-10 bg-gradient-to-r from-[#656565] to-[#e99b63] dark:shadow-[0_0_15px_rgba(255,255,255,0.4)] rounded-full hover:opacity-75">
                  <div className="absolute inset-[3px] dark:bg-black rounded-full flex items-center justify-center gap-1 text-white ">
                    <Book className="w-4 h-4 text-white"/>
                    INTRODUCING
                  </div>
              </div>
            </Link>

            <h1 className="text-3xl sm:text-4xl md:text-5xl lg:text-6xl font-semibold tracking-wider my-8 text-left">
                START TO 
                <br />
                DETECTION
            </h1>

            <p className="text-base sm:text-lg tracking-wider text-gray-400 max-w-[25rem] lg:max-w-[30rem] text-left">
                Can AI detect its own lies? Detection, generate, and reveal Ai-driven fake news.
            </p>

            <div className="flex gap-6 mt-12">
                <Link to="/generate">
                  <Button className="border border-[#2a2a2a] !py-6 !sm:py-3 !px-11 !sm:px-10 rounded-full sm:text-lg text-sm font-semibold tracking-wider transition-all duration-300 dark:bg-black text-white">
                    Generate<ExternalLink className="w-4 h-4 text-white"/>
                  </Button>
                </Link>

                <Link to="/detection" >
                  <Button className="border border-[#2a2a2a] !py-6 !sm:py-3 !px-11 !sm:px-10 rounded-full sm:text-lg text-sm font-semibold tracking-wider transition-all duration-300 dark:hover:bg-[#1a1a1a] dark:bg-gray-300 dark:text-black dark:hover:text-white">
                    Detection<ExternalLink className="w-4 h-4 dark:text-black"/>
                  </Button>
                </Link>
            </div>
        </div>
        <Spline 
          className="absolute top-[-20%] bottom-0 lg:left-[25%] sm:left-[-2%] h-full w-auto" 
          scene="https://prod.spline.design/FDHcSpYgnuaP1u4Y/scene.splinecode" 
        />
    </main>
  )
}

export default Hero