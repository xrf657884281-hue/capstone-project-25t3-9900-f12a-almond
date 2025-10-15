import { Separator } from "@radix-ui/react-separator"
import { BarChart3, FileSearch, Wand2 } from "lucide-react"


const Product = () => {
  return (
    <main className="grid gap-8 bg-brand-gradient background-dark_orangegradient background-light_orangegradient transition-all duration-300">
        <section className="px-6 py-10">
            <h1 className="text-white text-3xl font-semibold text-black/90 sm:text-4xl md:text-5xl lg:text-6xl tracking-wider my-30">Why choose us?</h1>

        </section>

        <section className="grid gap-6 p-6 md:grid-cols-[1fr_2fr]">
            <div className="mx-2">
                <Separator className="my-10 bg-white/20 h-[2px]" />
                <div className="inline-flex items-center gap-2">
                    <Wand2/>
                    <span className="text-2xl font-semibold">Generate</span>
                </div>
                <p className="text-justify">
                    Safe sandbox generation. From chosen keywords and images, our engine creates controlled synthetic articles that simulate styles—loaded language, conspiracy framing, cross-modal inconsistencies—to stress-test detectors and auto-document results for research and training only.
                </p>

                <Separator className="my-10 bg-white/20 h-[2px]" />
                <div className="inline-flex items-center gap-2">
                    <FileSearch/>
                    <span className="text-2xl font-semibold">Detection</span>
                </div>
                <p className="text-justify">
                    Instant credibility, explained. Our hybrid AI flags risk in seconds, delivers a clear score with source-linked evidence, and highlights what matters—actionable, audit-ready, built for real-world news.
                </p>


                <Separator className="my-10 bg-white/20 h-[2px]" />
                <div className="inline-flex items-center gap-2">
                    <BarChart3/>
                    <span className="text-2xl font-semibold">Visualization</span>
                </div>
                <p className="text-justify">
                    Insight, visualized. Turn text analysis into clear, interactive charts and story-led dashboards—then auto-generate shareable, cited reports with key takeaways. Align faster, decide smarter, and save hours from data to decision.
                </p>

            <div className="pb-24 lg:pb-32"></div>

            </div>

        </section>
      
    </main>
  )
}

export default Product
