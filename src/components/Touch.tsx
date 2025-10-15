import {
  Card,
  CardContent,
} from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Button } from "./ui/button"
import { Send } from "lucide-react"


const Touch = () => {
  return (
        <main className="grid gap-8 bg-brand-gradient background-dark_orangegradient background-light_orangegradient transition-all duration-300">
            <section className="px-6 py-10">
                <h1 className="text-white text-3xl font-semibold text-black/90 sm:text-4xl md:text-5xl lg:text-6xl tracking-wider my-30">Keep touch with us</h1>

            </section>

            <section className="gap-6 p-10">
                <Card className="w-full">
                    <CardContent className="h-[600px] grid grid-cols-12">
                            
                    </CardContent>
                </Card>
               
            </section>
            
            <section className="gap-6 p-10">

            </section>

            <section className="gap-6 p-10">
                <Card className="w-full">
                    <CardContent className="grid grid-cols-1 sm:grid-cols-7 items-center p-8 h-[200px] ">
                        <h1 className="sm:col-span-3 text-white text-3xl font-semibold text-black/90 sm:text-2xl md:text-3xl lg:text-4xl tracking-wider text-left">
                            What problem are you up against?

                        </h1>

                        <div className="hidden sm:block sm:col-span-1"></div>

                        <div className="relative sm:col-span-3">
                            <Input className="w-full h-12 absolute right-1 top-1/2 -translate-y-1/2 h-10 px-4 h-[60px]" placeholder="How can I help you today?" />
                            <Button
                                type="submit"
                                className="absolute right-1 top-1/2 -translate-y-1/2 h-10 px-4 font-semibold bg-[#D97706] hover:opacity-75 right-[20px]"
                            >
                                <Send/>
                                Ask us
                            </Button>
                        </div>

                    <div className="hidden sm:block sm:col-span-1"></div>
                            
                    </CardContent>
                </Card>
               
            </section>

            <div className="pb-24 lg:pb-32"></div>
            

            
        
        </main>
      

  )
}

export default Touch
