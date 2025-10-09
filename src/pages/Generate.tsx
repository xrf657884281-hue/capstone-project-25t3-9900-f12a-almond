import { useState } from "react";
import { motion } from "motion/react";
import { Button } from "@/components/ui/button"; 
import { Card, CardContent } from "../components/ui/card";

const Generate = () => {
  const [input, setInput] = useState("");

  const handleGenerate = () => {
    console.log("Generating fake news with input:", input);
    // 后端接口
  };

  const handleClear = () => {
    setInput("");
  };

  return (
    <div className="min-h-screen flex flex-col lg:flex-row items-start justify-center gap-8 px-6 py-12 bg-background text-foreground">
      
      <motion.div
        initial={{ opacity: 0, x: -30 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ duration: 0.5 }}
        className="flex-1 max-w-xl"
      >
        <h1 className="text-4xl font-bold mb-6 leading-snug">
          AI Fake News Generator
        </h1>
        <p className="text-lg text-muted-foreground mb-4">
          This project explores the potential of<strong>AI-powered fake news generation and detection.</strong>
          We built a multi-agent generator that simulates news text and tests the robustness of detection models.
        </p>
        <p className="text-base text-muted-foreground">
          Here, you can enter a prompt or news snippet, and the system will help generate relevant text. We will then feed the results into the detection module for verification.
        </p>
      </motion.div>

      <motion.div
        initial={{ opacity: 0, x: 30 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ duration: 0.5 }}
        className="flex-1 w-full max-w-2xl"
      >
        <Card className="w-full shadow-lg border border-border">
          <CardContent className="p-6 flex flex-col gap-4">
            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Paste your text or write a prompt..."
              className="w-full h-56 rounded-md p-4 border border-input bg-background text-foreground focus:ring-2 focus:ring-ring focus:outline-none resize-none"
            />
            <div className="flex gap-4 justify-end">
              <Button variant="secondary" onClick={handleClear}>Clear</Button>
              <Button variant="default" onClick={handleGenerate}>Generate</Button>

            </div>
          </CardContent>
        </Card>
      </motion.div>
    </div>
  );
};

export default Generate;
