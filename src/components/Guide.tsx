import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import {
  Card,
  CardAction,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { ScrollArea } from "@/components/ui/scroll-area"
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion"
import { Detection_Items, Generation_Items } from "@/constants/Guide_introduction"
import { useAtom } from "jotai";
import { Book } from "./Book/Book"
import { getPagesByTab, pageAtom} from "./Book/UI"
import type { TabScene } from "./Book/UI"
import { useMemo, useState } from "react"
import { Canvas } from "@react-three/fiber"

const Guide = () => {
  const [currentTab, setCurrentTab] = useState<TabScene>("generate");
  const [, setPage] = useAtom(pageAtom);

  const currentPages = useMemo(() => {
    return getPagesByTab(currentTab);
  }, [currentTab]);

  const handleTabChange = (value: string) => {
    setCurrentTab(value as TabScene);
    setPage(0); 
  };
  return (
    <main className="grid gap-8 transition-all duration-300">
        <section className="px-6 py-10">
            <h1 className="dark:text-white text-3xl font-semibold text-black/90 sm:text-4xl md:text-5xl lg:text-6xl tracking-wider my-30">How you can start?</h1>
        </section>

        <section className="gap-6 p-10">
            <Tabs 
              defaultValue="generate" 
              className="w-full"
              onValueChange={handleTabChange}
            >
                <TabsList>
                    <TabsTrigger value="generate">Generate</TabsTrigger>
                    <TabsTrigger value="detection">Detection</TabsTrigger>
                    <TabsTrigger value="visualization">Visualization</TabsTrigger>
                    <TabsTrigger value="Q&A">Q&A</TabsTrigger>
                </TabsList>

                <TabsContent value="generate" className="w-full">
                    <Card>
                        <CardContent className="h-[600px] grid grid-cols-12">
                            <div className="col-span-7">
                                <Canvas camera={{ position: [0, 0, 3], fov: 45 }}>
                                    <ambientLight intensity={0.5} />
                                    <directionalLight position={[10, 10, 5]} intensity={1} />
                                    <Book pageImages={currentPages} />
                                </Canvas>
                            </div>

                            <ScrollArea className="col-start-8 col-end-12 h-[600px] w-full rounded-md border p-4">
                                <Accordion type="multiple">
                                    {Generation_Items.map(({ id, title, content }) => (
                                        <AccordionItem key={id} value={id}>
                                            <AccordionTrigger className="text-left text-lg font-semibold">{title}</AccordionTrigger>
                                            <AccordionContent className="text-justify leading-loose text-base text-gray-700 pt-3">{content}</AccordionContent>
                                        </AccordionItem>
                                    ))}
                                </Accordion>
                            </ScrollArea>
                        </CardContent>
                    </Card>
                </TabsContent>

                <TabsContent value="detection" className="w-full">
                    <Card>
                        <CardContent className="h-[800px] grid grid-cols-12">
                            <ScrollArea className="col-start-2 col-end-6 justify-self-end h-[800px] w-full rounded-md border p-4">
                                <Accordion type="multiple">
                                    {Detection_Items.map(({ id, title, content }) => (
                                        <AccordionItem key={id} value={id}>
                                            <AccordionTrigger className="text-left text-lg font-semibold">{title}</AccordionTrigger>
                                            <AccordionContent className="text-justify leading-loose text-base text-gray-400 pt-3">{content}</AccordionContent>
                                        </AccordionItem>
                                    ))}
                                </Accordion>
                            </ScrollArea>
                        </CardContent>
                    </Card>
                </TabsContent>

                <TabsContent value="visualization">
                    <Card className="h-[800px]">
                        <CardHeader>
                            <CardTitle>Card Title</CardTitle>
                            <CardDescription>Card Description</CardDescription>
                            <CardAction>Card Action</CardAction>
                        </CardHeader>
                        <CardContent>
                            <p>Card Content</p>
                        </CardContent>
                        <CardFooter>
                            <p>Card Footer</p>
                        </CardFooter>
                    </Card>
                </TabsContent>

                <TabsContent value="Q&A">
                    <Card className="h-[800px]">
                        <CardHeader>
                            <CardTitle>Card Title</CardTitle>
                            <CardDescription>Card Description</CardDescription>
                            <CardAction>Card Action</CardAction>
                        </CardHeader>
                        <CardContent>
                            <p>Card Content</p>
                        </CardContent>
                        <CardFooter>
                            <p>Card Footer</p>
                        </CardFooter>
                    </Card>
                </TabsContent>

            </Tabs>

        </section>

        <section className="pb-24 lg:pb-32"></section>
      
    </main>
  )
}

export default Guide
