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
import { Generation_Items } from "@/constants"

const Guide = () => {
  return (
    <main className="grid gap-8 transition-all duration-300">
        <section className="px-6 py-10">
            <h1 className="dark:text-white text-3xl font-semibold text-black/90 sm:text-4xl md:text-5xl lg:text-6xl tracking-wider my-30">How you can start?</h1>

        </section>

        <section className="gap-6 p-10">
            <Tabs defaultValue="generate" className="w-full">
                <TabsList>
                    <TabsTrigger value="generate">Generate</TabsTrigger>
                    <TabsTrigger value="detection">Detection</TabsTrigger>
                    <TabsTrigger value="visualization">Visualization</TabsTrigger>
                    <TabsTrigger value="Q&A">Q&A</TabsTrigger>
                </TabsList>

                <TabsContent value="generate" className="w-full">
                    <Card>
                        <CardContent className="h-[600px] grid grid-cols-12">
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
                            <ScrollArea className="col-start-2 col-end-7 justify-self-end h-[800px] max-w-[600px]  rounded-md border p-4">
                                Project ID: 34
                                Project Title
                                Can Ai See Through Its Own Lies? Generating And Detecting Ai-Driven Fake News
                                Client Name
                                Jiaojiao Jiang, Yucheng Lin, Ziyu Yang
                                Group Capacity
                                3 groups
                                Project Tags
                                Artificial Intelligence (Machine/Deep Learning, NLP), Software Development, Generative AI
                                (GenAI)
                                Company/Organization Name (Including Department)
                                UNSW/CSE
                                Project Background
                                The rapid advancement of large language models (LLMs) and multimodal generative
                                systems has transformed the landscape of information creation. These systems are capable
                                of producing news-like articles, persuasive narratives, and even synthetic images with
                                unprecedented fluency and realism. While such progress has positive applications, it also
                                presents a critical challenge: adversaries can harness AI to generate highly convincing fake
                                news at scale, threatening public trust, information integrity, and democratic resilience. Recent research has highlighted the dual role of AI in this domain. On the one hand, LLMs
                                can be powerful content forgers, generating disinformation that is often indistinguishable
                                from authentic news (FakeGPT [1]; Fighting Fire with Fire [3]). On the other hand, AI also
                                offers potential as a defensive tool. Works such as Defending Against Neural Fake News [2]
                                and Detecting and Grounding Multi-Modal Media Manipulation [4] demonstrate that
                                advanced detection models-spanning text-only and multimodal approaches-can flag
                                manipulated content with varying success. Still, as Each Fake News is Fake in its Own Way
                                [5] shows, fake news comes in diverse forms, each exploiting different linguistic, rhetorical, or visual cues, making robust detection a moving target. Against this backdrop, our project
                                investigates a central question: Can AI-generated fake news be reliably identified by AI? To
                                answer this, we adopt a systematic four-phase approach. First, we will build a multi-agent
                                fake news generator capable of producing synthetic articles and multimodal news content
                                with a variety of manipulation strategies. Second, we will stress test state-of-the-art (SOTA)
                                detection systems on this generated dataset, measuring their strengths and vulnerabilities. Third, we will conduct a comprehensive error analysis, identifying the manipulation
                                strategies and linguistic/visual features that most often cause detectors to fail. Finally, informed by these findings, we will develop an improved detection method designed to
                                address the most salient failure cases. The goals of this project are both technical and
                                practical. Technically, it seeks to contribute new insights into the adversarial dynamics
                                between generative and discriminative AI in the fake news domain, providing a rigorous
                                evaluation of how well SOTA systems hold up under targeted stress. Practically, it aims to
                                deliver a working tool that integrates fake news generation, testing, error analysis, and
                                improved detection into one platform. Such a tool will support future research, teaching, and even policy evaluation by offering a reproducible environment where new fake news
                                detection strategies can be benchmarked against evolving generative threats. [1] Huang, Y. and Sun, L., 2023. FakeGPT: fake news generation, explanation and detection of large
                                language models. arXiv preprint arXiv:2310.05046. [2] Zellers, R., Holtzman, A., Rashkin, H., Bisk, Y., Farhadi, A., Roesner, F. and Choi, Y., 2019. Defending against neural fake news. Advances in neural information processing systems, 32. [3] Lucas, J., Uchendu, A., Yamashita, M., Lee, J., Rohatgi, S. and Lee, D., 2023. Fighting fire
                                with fire: The dual role of LLMs in crafting and detecting elusive disinformation. arXiv
                                preprint arXiv:2310.15515. [4] Shao, R., Wu, T. and Liu, Z., 2023. Detecting and grounding multi-modal media
                                manipulation. In Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern
                                Recognition (pp. 6904-6913). [5] Guo, H., Ma, Z., Zeng, Z., Luo, M., Zeng, W., Tang, J. and Zhao, X., 2025, April. Each fake
                                news is fake in its own way: An attribution multi-granularity benchmark for multimodal
                                fake news detection. In Proceedings of the AAAI Conference on Artificial Intelligence (Vol. 39, No. 1, pp. 228-236). Project Scope
                                This project investigates whether AI-generated fake news can be reliably identified by AI
                                through a structured four-phase process. The scope covers both generation and detection, ensuring that the study not only stresses existing detection models but also contributes
                                toward advancing detection capability. The project will first focus on the generation of fake
                                news using a multi-agent system capable of producing both single-modal (text) and multi- modal (text-image) disinformation. Generation will incorporate diverse manipulation
                                strategies such as loaded language, conspiracy framing, fabricated evidence, and cross- modal inconsistency. This synthetic dataset will provide a controlled yet realistic
                                benchmark to probe detection systems. The second phase will evaluate a range of state-of- the-art fake news detection methods, including text-only approaches such as RoBERTa- based classifiers, DetectGPT, and GLTR, as well as multimodal detectors that assess image- text consistency. These models will be systematically benchmarked against the generated
                                dataset to assess their accuracy, robustness, and failure patterns. In the third phase, the
                                team will conduct a comprehensive error analysis to identify why detectors fail, with
                                particular attention to the manipulation strategies that consistently evade detection. This
                                analysis will produce a taxonomy of weaknesses in current models, offering both theoretical
                                and practical insights into the evolving arms race between generative and discriminative AI. Finally, the project will design and prototype a new detection method that addresses some
                                of the most significant failure cases. This may involve integrating rhetorical profiling, cross-
                                modal consistency checks, or attribution-based explanations to improve transparency and
                                resilience. The project deliverables will be consolidated in a web-based tool that integrates
                                all four phases-generation, detection, error analysis, and improved detection-into an
                                interactive platform. The scope is deliberately limited to text and image modalities, with a
                                focus on feasibility for a three-month postgraduate project, but the design will remain
                                extensible for future expansion to video or audio-based disinformation. Project Requirements
                                The project requires the development of a web-based research tool that integrates four core
                                modules: fake news generation, detection, error analysis, and improved detection. The
                                generation module will employ a multi-agent system capable of producing both text-only
                                and text-image fake news with diverse manipulation strategies, such as loaded language, conspiracy framing, or cross-modal inconsistencies. Detection will integrate state-of-the-art
                                (SOTA) models, including text-based systems (e.g., RoBERTa, DetectGPT, GLTR) and
                                multimodal detectors for image-text alignment. An error analysis module will categorize
                                failure cases by manipulation strategy and provide visual summaries, while the improved
                                detection module will prototype a hybrid system that integrates rhetorical profiling and
                                multimodal consistency checks. The user interface will support input of articles or URLs, highlight propaganda techniques, display detection results, and export reports. Required Skills
                                To successfully complete the project, students should possess a solid background in
                                machine learning and NLP, including familiarity with training and fine-tuning transformer- based models (e.g., BERT, RoBERTa) using frameworks such as PyTorch or TensorFlow. Since the project involves testing and extending state-of-the-art models, students must be
                                comfortable working with pre-trained models from Hugging Face and applying transfer
                                learning methods. Additionally, students will need practical software engineering and
                                system development skills. Expected Outcomes
                                source code, documentation, and user guide
                                Disciplines
                                Artificial Intelligence (Machine/Deep Learning, NLP);Generative AI (GenAI);Web
                                Application Development
                                Other Resources
                                None
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
