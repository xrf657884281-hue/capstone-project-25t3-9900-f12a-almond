import { useState } from "react"
import {
  Card,
  CardContent,
} from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Button } from "./ui/button"
import { Send, Loader2 } from "lucide-react"
import { useUserProfile } from "@/hooks/useProfileData"
import { toast } from "sonner"  
import emailjs from '@emailjs/browser'


const Touch = () => {
  const { userData } = useUserProfile()
  const [message, setMessage] = useState("")
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!message.trim()) {
      toast.error("Please enter your message before sending")  
      return
    }

    setLoading(true)

    try {
      const serviceID = import.meta.env.VITE_EMAILJS_SERVICE_ID
      const templateID = import.meta.env.VITE_EMAILJS_TEMPLATE_ID
      const publicKey = import.meta.env.VITE_EMAILJS_PUBLIC_KEY

      if (!serviceID || !templateID || !publicKey) {
        throw new Error("EmailJS configuration missing")
      }

      const result = await emailjs.send(
        serviceID,
        templateID,
        {
          to_name: "Admin",
          from_name: userData.username,
          from_email: userData.email,
          message: message,
        },
        publicKey
      )

      console.log('Email sent successfully:', result)
      
      toast.success("Message sent! We'll get back to you soon.")  
      
      setMessage("")
      
    } catch (error: any) {
      console.error('EmailJS Error:', error)
      toast.error(error.text || "Failed to send. Please try again later.")  
    } finally {
      setLoading(false)
    }
  }

  return (
    <main className="grid">
      <section className="px-6 py-5">
        <h1 className="dark:text-white text-3xl font-semibold text-black/90 sm:text-4xl md:text-5xl lg:text-6xl tracking-wider">
          Keep touch with us
        </h1>
      </section>

      <section className="gap-6 p-10">
        <Card className="w-full">
          <CardContent className="grid grid-cols-1 sm:grid-cols-7 items-center p-8 h-[200px]">
            <h1 className="sm:-mt-10 lg:mt-0 sm:col-span-3 dark:text-white text-3xl font-semibold text-black/90 sm:text-2xl md:text-3xl lg:text-4xl tracking-wider text-left">
              What problem are you up against?
            </h1>

            <div className="hidden sm:block sm:col-span-1"></div>

            <form onSubmit={handleSubmit} className="relative sm:col-span-3">
              <Input
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                disabled={loading}
                className="w-full h-12 absolute right-1 top-1/2 -translate-y-1/2 px-4 h-[60px] pr-32"
                placeholder="How can I help you today?"
              />
              <Button
                type="submit"
                disabled={loading}
                className="absolute right-1 top-1/2 -translate-y-1/2 h-10 px-4 font-semibold bg-[#D97706] hover:opacity-75 right-[20px] disabled:opacity-50"
              >
                {loading ? (
                  <>
                    <Loader2 className="animate-spin mr-2" />
                    Sending...
                  </>
                ) : (
                  <>
                    <Send className="mr-2" />
                    Ask us
                  </>
                )}
              </Button>
            </form>

            <div className="hidden sm:block sm:col-span-1"></div>
          </CardContent>
        </Card>
      </section>

      <div className="pb-24 lg:pb-32"></div>
    </main>
  )
}

export default Touch