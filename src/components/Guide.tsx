import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import {
  Card,
  CardContent,
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
    <main className="grid transition-all duration-300">
      <section className="px-6">
        <h1 className="dark:text-white text-3xl font-semibold text-black/90 sm:text-4xl md:text-5xl lg:text-6xl tracking-wider">
          How our system work?
        </h1>
      </section>

      <section className="gap-6 p-4 lg:p-10">
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
              {/* Small window location */}
              <CardContent className="lg:hidden p-4">
                <div className="flex flex-col gap-4">
                  <div className="w-full h-[400px]">
                    <Canvas camera={{ position: [0, 0, 3], fov: 45 }}>
                      <ambientLight intensity={0.5} />
                      <directionalLight position={[10, 10, 5]} intensity={1} />
                      <Book pageImages={currentPages} />
                    </Canvas>
                  </div>

                  <ScrollArea className="w-full h-[500px] rounded-md border p-4">
                    <Accordion type="multiple">
                      {Generation_Items.map(({ id, title, content }) => (
                        <AccordionItem key={id} value={id}>
                          <AccordionTrigger className="text-left text-base font-semibold">
                            {title}
                          </AccordionTrigger>
                          <AccordionContent className="text-justify leading-loose text-sm text-gray-700 pt-3">
                            {content}
                          </AccordionContent>
                        </AccordionItem>
                      ))}
                    </Accordion>
                  </ScrollArea>
                </div>
              </CardContent>

              {/* Big window location */}
              <CardContent className="hidden lg:block h-[500px] lg:grid lg:grid-cols-12">
                <div className="col-span-7">
                  <Canvas camera={{ position: [0, 0, 3], fov: 35 }}>
                    <ambientLight intensity={0.5} />
                    <directionalLight position={[10, 10, 5]} intensity={1} />
                    <Book pageImages={currentPages} />
                  </Canvas>
                </div>

                <ScrollArea className="col-start-8 col-end-12 h-[500px] w-full rounded-md border p-4">
                  <Accordion type="multiple">
                    {Generation_Items.map(({ id, title, content }) => (
                      <AccordionItem key={id} value={id}>
                        <AccordionTrigger className="text-left text-lg font-semibold">
                          {title}
                        </AccordionTrigger>
                        <AccordionContent className="text-justify leading-loose text-base text-gray-700 pt-3">
                          {content}
                        </AccordionContent>
                      </AccordionItem>
                    ))}
                  </Accordion>
                </ScrollArea>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="detection" className="w-full">
            <Card>
              {/* Small window location */}
              <CardContent className="lg:hidden p-4">
                <div className="flex flex-col gap-4">
                  <div className="w-full h-[400px]">
                    <Canvas camera={{ position: [0, 0, 3], fov: 45 }}>
                      <ambientLight intensity={0.5} />
                      <directionalLight position={[10, 10, 5]} intensity={1} />
                      <Book pageImages={currentPages} />
                    </Canvas>
                  </div>

                  <ScrollArea className="w-full h-[600px] rounded-md border p-4">
                    <Accordion type="multiple">
                      {Detection_Items.map(({ id, title, content }) => (
                        <AccordionItem key={id} value={id}>
                          <AccordionTrigger className="text-left text-base font-semibold">
                            {title}
                          </AccordionTrigger>
                          <AccordionContent className="text-justify leading-loose text-sm text-gray-400 pt-3">
                            {content}
                          </AccordionContent>
                        </AccordionItem>
                      ))}
                    </Accordion>
                  </ScrollArea>
                </div>
              </CardContent>

              {/* Big window location */}
              <CardContent className="hidden lg:block h-[500px] lg:grid lg:grid-cols-12">
                <ScrollArea className="col-start-2 col-end-6 justify-self-end h-[500px] w-full rounded-md border p-4">
                  <Accordion type="multiple">
                    {Detection_Items.map(({ id, title, content }) => (
                      <AccordionItem key={id} value={id}>
                        <AccordionTrigger className="text-left text-lg font-semibold">
                          {title}
                        </AccordionTrigger>
                        <AccordionContent className="text-justify leading-loose text-base text-gray-400 pt-3">
                          {content}
                        </AccordionContent>
                      </AccordionItem>
                    ))}
                  </Accordion>
                </ScrollArea>

                <div className="col-start-6 col-end-13">
                  <Canvas camera={{ position: [0, 0, 3], fov: 35 }}>
                    <ambientLight intensity={0.5} />
                    <directionalLight position={[10, 10, 5]} intensity={1} />
                    <Book pageImages={currentPages} />
                  </Canvas>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="visualization" className="w-full">
            <Card>
                {/* Small window location */}
              <CardContent className="lg:hidden p-4">
                <div className="flex flex-col gap-4">
                  <div className="w-full h-[400px]">
                    <Canvas camera={{ position: [0, 0, 3], fov: 45 }}>
                      <ambientLight intensity={0.5} />
                      <directionalLight position={[10, 10, 5]} intensity={1} />
                      <Book pageImages={currentPages} />
                    </Canvas>
                  </div>

                  <ScrollArea className="w-full h-[500px] rounded-md border p-4">
                    <Accordion type="multiple">
                      {Generation_Items.map(({ id, title, content }) => (
                        <AccordionItem key={id} value={id}>
                          <AccordionTrigger className="text-left text-base font-semibold">
                            {title}
                          </AccordionTrigger>
                          <AccordionContent className="text-justify leading-loose text-sm text-gray-700 pt-3">
                            {content}
                          </AccordionContent>
                        </AccordionItem>
                      ))}
                    </Accordion>
                  </ScrollArea>
                </div>
              </CardContent>

              {/* Big window location */}
              <CardContent className="hidden lg:block h-[500px] lg:grid lg:grid-cols-12">
                <div className="col-span-7">
                  <Canvas camera={{ position: [0, 0, 3], fov: 35 }}>
                    <ambientLight intensity={0.5} />
                    <directionalLight position={[10, 10, 5]} intensity={1} />
                    <Book pageImages={currentPages} />
                  </Canvas>
                </div>

                <ScrollArea className="col-start-8 col-end-12 h-[500px] w-full rounded-md border p-4">
                  <Accordion type="multiple">
                    {Generation_Items.map(({ id, title, content }) => (
                      <AccordionItem key={id} value={id}>
                        <AccordionTrigger className="text-left text-lg font-semibold">
                          {title}
                        </AccordionTrigger>
                        <AccordionContent className="text-justify leading-loose text-base text-gray-700 pt-3">
                          {content}
                        </AccordionContent>
                      </AccordionItem>
                    ))}
                  </Accordion>
                </ScrollArea>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="Q&A" className="w-full">
            <Card>
              {/* Small window location */}
              <CardContent className="lg:hidden p-4">
                <div className="flex flex-col gap-4">
                  <div className="w-full h-[400px]">
                    <Canvas camera={{ position: [0, 0, 3], fov: 45 }}>
                      <ambientLight intensity={0.5} />
                      <directionalLight position={[10, 10, 5]} intensity={1} />
                      <Book pageImages={currentPages} />
                    </Canvas>
                  </div>

                  <ScrollArea className="w-full h-[600px] rounded-md border p-4">
                    <Accordion type="multiple">
                      {Detection_Items.map(({ id, title, content }) => (
                        <AccordionItem key={id} value={id}>
                          <AccordionTrigger className="text-left text-base font-semibold">
                            {title}
                          </AccordionTrigger>
                          <AccordionContent className="text-justify leading-loose text-sm text-gray-400 pt-3">
                            {content}
                          </AccordionContent>
                        </AccordionItem>
                      ))}
                    </Accordion>
                  </ScrollArea>
                </div>
              </CardContent>

              {/* Big window location */}
              <CardContent className="hidden lg:block h-[500px] lg:grid lg:grid-cols-12">
                <ScrollArea className="col-start-2 col-end-6 justify-self-end h-[500px] w-full rounded-md border p-4">
                  <Accordion type="multiple">
                    {Detection_Items.map(({ id, title, content }) => (
                      <AccordionItem key={id} value={id}>
                        <AccordionTrigger className="text-left text-lg font-semibold">
                          {title}
                        </AccordionTrigger>
                        <AccordionContent className="text-justify leading-loose text-base text-gray-400 pt-3">
                          {content}
                        </AccordionContent>
                      </AccordionItem>
                    ))}
                  </Accordion>
                </ScrollArea>

                <div className="col-start-6 col-end-13">
                  <Canvas camera={{ position: [0, 0, 3], fov: 35 }}>
                    <ambientLight intensity={0.5} />
                    <directionalLight position={[10, 10, 5]} intensity={1} />
                    <Book pageImages={currentPages} />
                  </Canvas>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </section>
    </main>
  )
}

export default Guide