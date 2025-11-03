import { useRef, useState, useEffect } from "react";
import { motion } from "motion/react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "../components/ui/card";
import { apiService } from "@/services/api";

const Generate = () => {
  const [input, setInput] = useState("");
  const [image, setImage] = useState<File | null>(null);
  const [fileName, setFileName] = useState<string>("");
  const [generated, setGenerated] = useState<string>("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [tone, setTone] = useState("Normal");
  const [topic, setTopic] = useState("General");
  const inputRef = useRef<HTMLInputElement | null>(null);

  useEffect(() => {
    const savedNews = localStorage.getItem("generatedNews");
    if (savedNews) setGenerated(savedNews);

    const savedInput = localStorage.getItem("newsInput");
    if (savedInput) setInput(savedInput);

    const savedTone = localStorage.getItem("newsTone");
    if (savedTone) setTone(savedTone);

    const savedTopic = localStorage.getItem("newsTopic");
    if (savedTopic) setTopic(savedTopic);
  }, []);

  const handleInputChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setInput(e.target.value);
    localStorage.setItem("newsInput", e.target.value);
  };

  const handleToneChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    setTone(e.target.value);
    localStorage.setItem("newsTone", e.target.value);
  };

  const handleTopicChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    setTopic(e.target.value);
    localStorage.setItem("newsTopic", e.target.value);
  };

  const handleGenerate = async () => {
    if (!input.trim()) {
      setError("Please enter a topic first.");
      return;
    }

    setError(null);
    setIsLoading(true);

    try {
      const basePrompt = input.trim();

      const parts: string[] = [];
      if (topic !== "General") {
        parts.push(`Write a ${topic} news article`);
      } else {
        parts.push(`Write a general news article`);
      }

      if (tone !== "Normal") {
        parts.push(`in a ${tone} tone`);
      }

      const finalPrompt = `${parts.join(" ")} about: ${basePrompt}`;

      const response = await apiService.generateSingle({
        topic: finalPrompt,
      });

      if (response.success && response.result.article) {
        setGenerated(response.result.article);
        localStorage.setItem("generatedNews", response.result.article);
      } else {
        setError("Generation failed. Please try again.");
      }
    } catch (err) {
      console.error("Generation error:", err);
      setError(
        `Failed to generate: ${
          err instanceof Error ? err.message : String(err)
        }`
      );
    } finally {
      setIsLoading(false);
    }
  };

  const handleClear = () => {
    setInput("");
    setImage(null);
    setFileName("");
    setGenerated("");
    setError(null);
    setTone("Normal");
    setTopic("General");
    if (inputRef.current) inputRef.current.value = "";
    localStorage.removeItem("generatedNews");
    localStorage.removeItem("newsInput");
    localStorage.removeItem("newsTone");
    localStorage.removeItem("newsTopic");
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
    <div className="min-h-screen flex flex-col items-center justify-center gap-8 px-6 py-12 bg-background text-foreground">
      <motion.div
        initial={{ opacity: 0, y: -30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="flex-1 w-full max-w-2xl text-center"
      >
        <h1 className="text-4xl font-bold mb-6 leading-snug">
          AI Fake News Generator
          <span className="text-lg font-normal ml-2 text-blue-600 dark:text-blue-400">
            Powered by Chat-GPT-4o
          </span>
        </h1>
        <p className="text-lg text-muted-foreground mb-4">
          This project explores the potential of{" "}
          <strong>AI-powered fake news generation and detection.</strong>
        </p>
        <p className="text-base text-muted-foreground">
          Enter text or upload an image. The system will use Chat-GPT-4o to
          generate related fake news content, which can then be tested in the
          detection module.
        </p>
      </motion.div>

      <motion.div
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="flex-1 w-full max-w-2xl"
      >
        <Card className="w-full shadow-md border border-gray-300 dark:border-border bg-gray-50 dark:bg-background transition-colors">
          <CardContent className="p-6 flex flex-col gap-4">
            <textarea
              value={input}
              onChange={handleInputChange}
              placeholder="Paste your text or write a prompt..."
              className="w-full h-40 rounded-md p-4 border border-gray-300 dark:border-input bg-gray-50 dark:bg-background text-foreground focus:ring-2 focus:ring-blue-400 dark:focus:ring-ring focus:outline-none resize-none"
            />

            <div className="flex flex-col gap-2">
              <label className="text-sm font-medium">Choose Style:</label>
              <select
                value={tone}
                onChange={handleToneChange}
                className="w-full p-2 rounded-md border border-gray-300 dark:border-input bg-gray-50 dark:bg-background text-foreground focus:ring-2 focus:ring-blue-400 dark:focus:ring-ring focus:outline-none"
              >
                <option value="Formal">Formal — Professional and neutral.</option>
                <option value="Sensational">Sensational — Dramatic and emotional.</option>
                <option value="Fun">Fun — Playful and light-hearted.</option>
                <option value="Normal">Normal — Standard news tone.</option>
              </select>
            </div>

            <div className="flex flex-col gap-2">
              <label className="text-sm font-medium">Choose Topic:</label>
              <select
                value={topic}
                onChange={handleTopicChange}
                className="w-full p-2 rounded-md border border-gray-300 dark:border-input bg-gray-50 dark:bg-background text-foreground focus:ring-2 focus:ring-blue-400 dark:focus:ring-ring focus:outline-none"
              >
                <option value="Politics">Politics — Government and elections.</option>
                <option value="Business">Business — Markets and economics.</option>
                <option value="Sports">Sports — Games and events.</option>
                <option value="Technology">Technology — Innovations and trends.</option>
                <option value="General">General — No specific topic.</option>
              </select>
            </div>

            <div className="flex items-center justify-between gap-4">
              <input
                ref={inputRef}
                type="file"
                accept="image/*"
                className="hidden"
                onChange={(e) => handleUpload(e.target.files?.[0])}
              />

              <div className="flex items-center gap-3">
                <Button
                  variant="outline"
                  onClick={triggerFileDialog}
                  className="border border-gray-300 dark:border-border bg-gray-50 dark:bg-background hover:bg-gray-100 dark:hover:bg-muted transition-colors"
                >
                  Choose Image
                </Button>
                <span className="text-sm text-muted-foreground">
                  {fileName ? fileName : "No file chosen"}
                </span>
              </div>

              <div className="flex gap-3">
                <Button
                  variant="outline"
                  onClick={handleClear}
                  disabled={isLoading}
                  className="border border-gray-300 dark:border-border bg-gray-50 dark:bg-background hover:bg-gray-100 dark:hover:bg-muted transition-colors"
                >
                  Clear
                </Button>
                <Button
                  variant="default"
                  onClick={handleGenerate}
                  disabled={isLoading}
                >
                  {isLoading ? "Generating..." : "Generate"}
                </Button>
              </div>
            </div>

            {error && (
              <div className="mt-2 p-3 border border-red-500 rounded-md bg-red-50 text-red-700 text-sm">
                {error}
              </div>
            )}

            {generated && (
              <div className="mt-6 p-4 border border-gray-300 dark:border-border rounded-md bg-gray-50 dark:bg-muted transition-colors">
                <h3 className="font-semibold mb-2">
                  Generated News ({topic} | {tone})
                </h3>
                <p className="text-sm text-foreground whitespace-pre-wrap">
                  {generated}
                </p>
                <div className="flex justify-end mt-3">
                  <Button
                    variant="outline"
                    onClick={handleCopy}
                    className="border border-gray-300 dark:border-border bg-gray-50 dark:bg-background hover:bg-gray-100 dark:hover:bg-muted transition-colors"
                  >
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
