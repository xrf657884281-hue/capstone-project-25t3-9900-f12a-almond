import { useRef, useState, useEffect } from "react";
import { motion } from "motion/react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "../components/ui/card";
import { apiService } from "@/services/api";

const Generate = () => {
  const [input, setInput] = useState("");
  const [image, setImage] = useState<File | null>(null);
  const [fileName, setFileName] = useState<string>("");
  const [imagePreview, setImagePreview] = useState<string | null>(null);
  const [generated, setGenerated] = useState<string>("");
  const [sourceUrl, setSourceUrl] = useState<string>("");
  const [visionText, setVisionText] = useState<string>("");
  const [isVisionLoading, setIsVisionLoading] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [tone, setTone] = useState("Normal");
  const [topic, setTopic] = useState("General");
  const inputRef = useRef<HTMLInputElement | null>(null);

  useEffect(() => {
    const savedNews = localStorage.getItem("generatedNews");
    if (savedNews) setGenerated(savedNews);

    const savedSourceUrl = localStorage.getItem("sourceUrl");
    if (savedSourceUrl) setSourceUrl(savedSourceUrl);

    const savedInput = localStorage.getItem("newsInput");
    if (savedInput) setInput(savedInput);

    const savedTone = localStorage.getItem("newsTone");
    if (savedTone) setTone(savedTone);

    const savedTopic = localStorage.getItem("newsTopic");
    if (savedTopic) setTopic(savedTopic);

    const savedVision = localStorage.getItem("visionText");
    if (savedVision) setVisionText(savedVision);
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

  const handleUpload = (file?: File | null) => {
    if (!file) return;
    setImage(file);
    setFileName(file.name);
    setVisionText("");
    const previewUrl = URL.createObjectURL(file);
    setImagePreview(previewUrl);
    console.log("Selected file:", file);
  };

  const triggerFileDialog = () => inputRef.current?.click();

  const fileToBase64 = (file: File): Promise<string> =>
    new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = () => resolve(reader.result as string);
      reader.onerror = reject;
      reader.readAsDataURL(file);
    });

  const handleDescribe = async () => {
    if (!image) {
      setError("Please upload an image first.");
      return;
    }
    setIsVisionLoading(true);
    setError(null);

    try {
      const base64 = await fileToBase64(image);
      const res = await apiService.visionDescribe({
        image_url_or_b64: base64,
        detail_level: "high",
        output_mode: "detailed",
      });

      if (res.success && res.description) {
        setVisionText(res.description);
        localStorage.setItem("visionText", res.description);
      } else {
        setError(res.error || "Failed to describe image.");
      }
    } catch (err) {
      console.error("Vision describe error:", err);
      setError(
        `Vision failed: ${err instanceof Error ? err.message : String(err)}`
      );
    } finally {
      setIsVisionLoading(false);
    }
  };

  const handleGenerate = async () => {
    const basePrompt = [input.trim(), visionText.trim()]
      .filter(Boolean)
      .join(". ");

    if (!basePrompt) {
      setError("Please enter a topic or use an image description first.");
      return;
    }

    setError(null);
    setIsLoading(true);

    try {
      const parts: string[] = [];
      if (topic !== "General")
        parts.push(`Write a ${topic} news article`);
      else parts.push("Write a general news article");

      if (tone !== "Normal") parts.push(`in a ${tone} tone`);

      const finalPrompt = `${parts.join(" ")} about: ${basePrompt}`;

      const response = await apiService.generateSingle({
        topic: finalPrompt,
        image_url_or_b64: image ? await fileToBase64(image) : undefined,
      });

      if (response.success && response.result.article) {
        let articleText = response.result.article;
        let extractedUrl = "";
        
        // Extract source_url from result or from last line of article
        if (response.result.source_url) {
          extractedUrl = response.result.source_url;
        } else {
          // Fallback: extract URL from last line if it starts with "Original report:"
          const lines = articleText.split('\n');
          const lastLine = lines[lines.length - 1].trim();
          if (lastLine.toLowerCase().startsWith('original report:')) {
            extractedUrl = lastLine.replace(/^original report:\s*/i, '').trim();
            lines.pop(); // Remove the last line
            articleText = lines.join('\n').trim();
          }
        }
        
        setGenerated(articleText);
        setSourceUrl(extractedUrl);
        localStorage.setItem("generatedNews", articleText);
        if (extractedUrl) {
          localStorage.setItem("sourceUrl", extractedUrl);
        }
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
    setSourceUrl("");
    setVisionText("");
    setImagePreview(null); 
    setError(null);
    setTone("Normal");
    setTopic("General");
    if (inputRef.current) inputRef.current.value = "";
    localStorage.clear();
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
          Enter a topic or upload an image. The system will combine both to
          generate realistic fake news using AI.
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
              placeholder="Enter your topic or idea for the fake news..."
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
                <Button variant="outline" onClick={triggerFileDialog}>
                  Choose Image
                </Button>
                <span className="text-sm text-muted-foreground">
                  {fileName ? fileName : "No image chosen"}
                </span>
              </div>

              <Button
                variant="default"
                onClick={handleDescribe}
                disabled={!image || isVisionLoading}
              >
                {isVisionLoading ? "Analyzing..." : "Describe Image"}
              </Button>
            </div>

            {imagePreview && (
              <div className="mt-3 flex justify-center">
                <img
                  src={imagePreview}
                  alt="Preview"
                  className="max-h-64 rounded-md border border-gray-300 dark:border-border shadow-sm object-contain"
                />
              </div>
            )}

            {visionText && (
              <div className="mt-3">
                <label className="text-sm font-medium">Image Description:</label>
                <textarea
                  value={visionText}
                  onChange={(e) => {
                    setVisionText(e.target.value);
                    localStorage.setItem("visionText", e.target.value);
                  }}
                  className="w-full h-32 mt-1 p-3 rounded-md border border-gray-300 dark:border-input bg-gray-50 dark:bg-background text-foreground focus:ring-2 focus:ring-blue-400 dark:focus:ring-ring focus:outline-none resize-none"
                />
              </div>
            )}

            <div className="flex justify-end gap-3 pt-2">
              <Button variant="outline" onClick={handleClear}>
                Clear
              </Button>
              <Button variant="default" onClick={handleGenerate} disabled={isLoading}>
                {isLoading ? "Generating..." : "Generate News"}
              </Button>
            </div>

            {error && (
              <div className="mt-2 p-3 border border-red-500 rounded-md bg-red-50 text-red-700 text-sm">
                {error}
              </div>
            )}

            {sourceUrl && (
              <div className="mt-6 p-4 border border-gray-300 dark:border-border rounded-md bg-gray-50 dark:bg-background transition-colors">
                <label className="text-sm font-medium mb-2 block">Original Source URL:</label>
                <a
                  href={sourceUrl}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-blue-600 dark:text-blue-400 hover:underline break-all"
                >
                  {sourceUrl}
                </a>
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
                  <Button variant="outline" onClick={handleCopy}>
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
