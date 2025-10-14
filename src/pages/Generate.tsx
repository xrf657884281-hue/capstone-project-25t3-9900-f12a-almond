import { useRef, useState } from "react";
import { motion } from "motion/react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "../components/ui/card";

const Generate = () => {
  const [input, setInput] = useState("");
  const [image, setImage] = useState<File | null>(null);
  const [fileName, setFileName] = useState<string>("");
  const [generated, setGenerated] = useState<string>(""); 
  const inputRef = useRef<HTMLInputElement | null>(null);

  const handleGenerate = () => {
    console.log("Generating fake news with input:", input);
    if (image) {
      console.log("Using image:", image.name);
    }

    const fakeResult =
      "\"" +
      input.slice(0, 50) +
      (input.length > 50 ? "..." : "") +
      "\"";

    setGenerated(fakeResult);
  };

  const handleClear = () => {
    setInput("");
    setImage(null);
    setFileName("");
    setGenerated("");
    if (inputRef.current) inputRef.current.value = "";
  };

  const triggerFileDialog = () => inputRef.current?.click();

  const handleUpload = (file?: File | null) => {
    if (!file) return;
    setImage(file);
    setFileName(file.name);
    console.log("Selected file:", file);
  };

  const handleCopy = async () => {
    if (!generated) return;
    try {
      await navigator.clipboard.writeText(generated);
      alert("Copied to clipboard!");
    } catch {
      alert("Failed to copy");
    }
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
          This project explores the potential of <strong>AI-powered fake news generation and detection.</strong>
          We built a multi-agent generator that simulates news text and tests the robustness of detection models.
        </p>
        <p className="text-base text-muted-foreground">
          Enter text or upload an image. The system will use your input to generate related fake news content, 
          which can then be tested in the detection module.
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
              className="w-full h-40 rounded-md p-4 border border-input bg-background text-foreground focus:ring-2 focus:ring-ring focus:outline-none resize-none"
            />

            <div className="flex items-center justify-between gap-4">
              <input
                ref={inputRef}
                type="file"
                accept="image/*"
                className="hidden"
                onChange={(e) => handleUpload(e.target.files?.[0])}
              />

              <div className="flex items-center gap-3">
                <Button variant="secondary" onClick={triggerFileDialog}>
                  Choose Image
                </Button>
                <span className="text-sm text-muted-foreground">
                  {fileName ? fileName : "No file chosen"}
                </span>
              </div>

              <div className="flex gap-3">
                <Button variant="secondary" onClick={handleClear}>
                  Clear
                </Button>
                <Button variant="default" onClick={handleGenerate}>
                  Generate
                </Button>
              </div>
            </div>

            {generated && (
              <div className="mt-6 p-4 border rounded-md bg-muted">
                <h3 className="font-semibold mb-2">Generated News</h3>
                <p className="text-sm text-foreground whitespace-pre-wrap">
                  {generated}
                </p>
                <div className="flex justify-end mt-3">
                  <Button variant="secondary" onClick={handleCopy}>
                    Copy
                  </Button>
                </div>
              </div>
            )}

          </CardContent>
        </Card>
      </motion.div>
    </div>
  );
};

export default Generate;
