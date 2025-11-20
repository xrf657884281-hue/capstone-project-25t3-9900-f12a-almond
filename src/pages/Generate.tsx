import { useRef, useState, useEffect, useCallback } from "react";
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
  const [isToneAuto, setIsToneAuto] = useState(true);
  const [isTopicAuto, setIsTopicAuto] = useState(true);
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

    const savedToneAuto = localStorage.getItem("newsToneAuto");
    if (savedToneAuto !== null) {
      setIsToneAuto(savedToneAuto !== "false");
    } else {
      localStorage.setItem("newsToneAuto", "true");
    }

    const savedTopicAuto = localStorage.getItem("newsTopicAuto");
    if (savedTopicAuto !== null) {
      setIsTopicAuto(savedTopicAuto !== "false");
    } else {
      localStorage.setItem("newsTopicAuto", "true");
    }

    const savedVision = localStorage.getItem("visionText");
    if (savedVision) setVisionText(savedVision);
  }, []);

  const inferAttributes = useCallback((text: string) => {
    if (!text) {
      return { topic: "General", tone: "Normal" };
    }

    const lower = text.toLowerCase();

    const domainKeywords: Record<
      string,
      Array<{ keyword: string; weight: number }>
    > = {
      Politics: [
        { keyword: "government", weight: 1.5 },
        { keyword: "election", weight: 1.7 },
        { keyword: "policy", weight: 1.1 },
        { keyword: "president", weight: 1.4 },
        { keyword: "minister", weight: 1.2 },
        { keyword: "parliament", weight: 1.4 },
        { keyword: "congress", weight: 1.4 },
        { keyword: "senate", weight: 1.2 },
        { keyword: "campaign", weight: 1.1 },
        { keyword: "diplomatic", weight: 1.1 },
        { keyword: "legislation", weight: 1.2 },
        { keyword: "bill", weight: 0.8 }
      ],
      Business: [
        { keyword: "market", weight: 1.4 },
        { keyword: "economy", weight: 1.3 },
        { keyword: "finance", weight: 1.3 },
        { keyword: "company", weight: 1.0 },
        { keyword: "startup", weight: 1.0 },
        { keyword: "investment", weight: 1.2 },
        { keyword: "revenue", weight: 1.3 },
        { keyword: "profit", weight: 1.3 },
        { keyword: "corporate", weight: 1.1 },
        { keyword: "stock", weight: 1.2 },
        { keyword: "merger", weight: 1.2 },
        { keyword: "shareholder", weight: 1.2 },
        { keyword: "earnings", weight: 1.3 },
        { keyword: "quarter", weight: 0.9 }
      ],
      Sports: [
        { keyword: "match", weight: 1.2 },
        { keyword: "game", weight: 1.0 },
        { keyword: "tournament", weight: 1.4 },
        { keyword: "league", weight: 1.3 },
        { keyword: "player", weight: 1.0 },
        { keyword: "coach", weight: 1.0 },
        { keyword: "season", weight: 1.1 },
        { keyword: "score", weight: 1.0 },
        { keyword: "championship", weight: 1.5 },
        { keyword: "olympic", weight: 1.5 },
        { keyword: "victory", weight: 1.1 },
        { keyword: "defeat", weight: 1.1 },
        { keyword: "goal", weight: 1.0 },
        { keyword: "playoff", weight: 1.3 }
      ],
      Technology: [
        { keyword: "technology", weight: 1.3 },
        { keyword: "tech", weight: 1.3 },
        { keyword: "software", weight: 1.2 },
        { keyword: "hardware", weight: 1.2 },
        { keyword: "ai", weight: 1.5 },
        { keyword: "artificial intelligence", weight: 1.7 },
        { keyword: "robot", weight: 1.1 },
        { keyword: "digital", weight: 1.0 },
        { keyword: "cyber", weight: 1.2 },
        { keyword: "innovation", weight: 1.2 },
        { keyword: "cloud", weight: 1.1 },
        { keyword: "algorithm", weight: 1.3 },
        { keyword: "data", weight: 1.0 }
      ],
      Health: [
        { keyword: "hospital", weight: 1.2 },
        { keyword: "vaccine", weight: 1.5 },
        { keyword: "disease", weight: 1.3 },
        { keyword: "health", weight: 1.1 },
        { keyword: "medical", weight: 1.3 },
        { keyword: "doctor", weight: 1.2 },
        { keyword: "patients", weight: 1.1 },
        { keyword: "virus", weight: 1.4 },
        { keyword: "therapy", weight: 1.1 },
        { keyword: "clinical", weight: 1.2 },
        { keyword: "public health", weight: 1.4 }
      ],
      Environment: [
        { keyword: "climate", weight: 1.4 },
        { keyword: "environment", weight: 1.2 },
        { keyword: "wildfire", weight: 1.6 },
        { keyword: "sustainability", weight: 1.2 },
        { keyword: "pollution", weight: 1.3 },
        { keyword: "ecosystem", weight: 1.2 },
        { keyword: "emissions", weight: 1.3 },
        { keyword: "renewable", weight: 1.1 },
        { keyword: "conservation", weight: 1.2 },
        { keyword: "carbon", weight: 1.1 },
        { keyword: "earthquake", weight: 1.3 },
        { keyword: "flood", weight: 1.3 },
        { keyword: "drought", weight: 1.3 }
      ],
      Science: [
        { keyword: "research", weight: 1.2 },
        { keyword: "scientists", weight: 1.3 },
        { keyword: "study", weight: 1.2 },
        { keyword: "laboratory", weight: 1.1 },
        { keyword: "discovered", weight: 1.2 },
        { keyword: "experiment", weight: 1.1 },
        { keyword: "nasa", weight: 1.3 },
        { keyword: "space", weight: 1.1 },
        { keyword: "astronomy", weight: 1.3 },
        { keyword: "physics", weight: 1.2 },
        { keyword: "biology", weight: 1.2 },
        { keyword: "university", weight: 0.9 }
      ],
      Crime: [
        { keyword: "investigation", weight: 1.2 },
        { keyword: "suspect", weight: 1.2 },
        { keyword: "police", weight: 1.1 },
        { keyword: "fraud", weight: 1.3 },
        { keyword: "arrested", weight: 1.2 },
        { keyword: "charges", weight: 1.1 },
        { keyword: "lawsuit", weight: 1.1 },
        { keyword: "corruption", weight: 1.2 },
        { keyword: "security breach", weight: 1.4 }
      ],
      Entertainment: [
        { keyword: "festival", weight: 1.3 },
        { keyword: "film", weight: 1.1 },
        { keyword: "movie", weight: 1.1 },
        { keyword: "celebrity", weight: 1.2 },
        { keyword: "concert", weight: 1.3 },
        { keyword: "award", weight: 1.2 },
        { keyword: "music", weight: 1.1 },
        { keyword: "premiere", weight: 1.2 },
        { keyword: "hollywood", weight: 1.4 },
        { keyword: "box office", weight: 1.3 },
        { keyword: "red carpet", weight: 1.2 }
      ]
    };

    const sensationalPatterns = [
      { keyword: "breaking", weight: 1.2 },
      { keyword: "crisis", weight: 1.3 },
      { keyword: "disaster", weight: 1.3 },
      { keyword: "urgent", weight: 1.1 },
      { keyword: "scandal", weight: 1.2 },
      { keyword: "shocking", weight: 1.2 },
      { keyword: "attack", weight: 1.2 },
      { keyword: "protest", weight: 1.0 },
      { keyword: "violence", weight: 1.2 },
      { keyword: "emergency", weight: 1.2 },
      { keyword: "explosion", weight: 1.3 },
      { keyword: "tragedy", weight: 1.3 },
      { keyword: "threatens", weight: 1.4 },
      { keyword: "wildfire", weight: 1.4 }
    ];

    const funPatterns = [
      { keyword: "festival", weight: 1.3 },
      { keyword: "celebration", weight: 1.2 },
      { keyword: "party", weight: 1.1 },
      { keyword: "music", weight: 1.0 },
      { keyword: "concert", weight: 1.2 },
      { keyword: "holiday", weight: 1.1 },
      { keyword: "comedy", weight: 1.0 },
      { keyword: "event", weight: 1.0 },
      { keyword: "kids", weight: 1.0 },
      { keyword: "fun", weight: 1.0 },
      { keyword: "parade", weight: 1.1 },
      { keyword: "picnic", weight: 1.0 },
      { keyword: "festival-goers", weight: 1.0 }
    ];

    const styleScores: Record<string, number> = {
      Formal: 0,
      Sensational: 0,
      Fun: 0,
      Normal: 0
    };

    const domainScores: Record<string, number> = {};
    Object.keys(domainKeywords).forEach((key) => {
      domainScores[key] = 0;
    });

    Object.entries(domainKeywords).forEach(([domainKey, keywords]) => {
      keywords.forEach(({ keyword, weight }) => {
        if (lower.includes(keyword)) {
          domainScores[domainKey] += weight;
        }
      });
    });

    const bestDomain = Object.entries(domainScores).reduce(
      (best, current) => (current[1] > best[1] ? current : best),
      ["General", 0]
    );

    let inferredTopic =
      bestDomain[1] >= 1.0 ? (bestDomain[0] as string) : "General";

    sensationalPatterns.forEach(({ keyword, weight }) => {
      if (lower.includes(keyword)) {
        styleScores.Sensational += weight;
      }
    });
    styleScores.Sensational += (lower.match(/!/g) || []).length * 0.4;
    if (lower.includes("breaking news")) styleScores.Sensational += 1;

    funPatterns.forEach(({ keyword, weight }) => {
      if (lower.includes(keyword)) {
        styleScores.Fun += weight;
      }
    });

    const formalMarkers = [
      { keyword: "according to", weight: 1.0 },
      { keyword: "official", weight: 0.8 },
      { keyword: "statement", weight: 0.7 },
      { keyword: "report", weight: 0.8 },
      { keyword: "conference", weight: 0.7 },
      { keyword: "authorities", weight: 0.9 },
      { keyword: "analysis", weight: 0.8 },
      { keyword: "research", weight: 0.8 },
      { keyword: "study", weight: 0.7 }
    ];
    formalMarkers.forEach(({ keyword, weight }) => {
      if (lower.includes(keyword)) {
        styleScores.Formal += weight;
      }
    });

    if (["Politics", "Business", "Science"].includes(inferredTopic)) {
      styleScores.Formal += 0.6;
    }

    const neutralMarkers = [
      { keyword: "community", weight: 0.4 },
      { keyword: "local", weight: 0.4 },
      { keyword: "everyday", weight: 0.3 },
      { keyword: "routine", weight: 0.3 },
      { keyword: "update", weight: 0.3 }
    ];
    neutralMarkers.forEach(({ keyword, weight }) => {
      if (lower.includes(keyword)) {
        styleScores.Normal += weight;
      }
    });

    const bestStyle = Object.entries(styleScores).reduce(
      (best, current) => (current[1] > best[1] ? current : best),
      ["Normal", 0]
    );

    let inferredTone =
      bestStyle[1] >= 0.6 ? (bestStyle[0] as string) : "Normal";

    return {
      topic: inferredTopic,
      tone: inferredTone
    };
  }, []);

  useEffect(() => {
    const combined = `${input} ${visionText}`.trim();
    if (!combined) {
      if (isTopicAuto && topic !== "General") {
        setTopic("General");
        localStorage.setItem("newsTopic", "General");
      }
      if (isToneAuto && tone !== "Normal") {
        setTone("Normal");
        localStorage.setItem("newsTone", "Normal");
      }
      return;
    }

    const inferred = inferAttributes(combined);

    if (isTopicAuto && inferred.topic !== topic) {
      setTopic(inferred.topic);
      localStorage.setItem("newsTopic", inferred.topic);
    }

    if (isToneAuto && inferred.tone !== tone) {
      setTone(inferred.tone);
      localStorage.setItem("newsTone", inferred.tone);
    }
  }, [
    input,
    visionText,
    inferAttributes,
    isTopicAuto,
    isToneAuto,
    topic,
    tone
  ]);

  const handleInputChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setInput(e.target.value);
    localStorage.setItem("newsInput", e.target.value);
  };

  const handleToneChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    setTone(e.target.value);
    setIsToneAuto(false);
    localStorage.setItem("newsTone", e.target.value);
    localStorage.setItem("newsToneAuto", "false");
  };

  const handleTopicChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    setTopic(e.target.value);
    setIsTopicAuto(false);
    localStorage.setItem("newsTopic", e.target.value);
    localStorage.setItem("newsTopicAuto", "false");
  };

  const resetToneToAuto = () => {
    const combined = `${input} ${visionText}`.trim();
    const inferred = inferAttributes(combined);
    setTone(inferred.tone);
    setIsToneAuto(true);
    localStorage.setItem("newsTone", inferred.tone);
    localStorage.setItem("newsToneAuto", "true");
  };

  const resetTopicToAuto = () => {
    const combined = `${input} ${visionText}`.trim();
    const inferred = inferAttributes(combined);
    setTopic(inferred.topic);
    setIsTopicAuto(true);
    localStorage.setItem("newsTopic", inferred.topic);
    localStorage.setItem("newsTopicAuto", "true");
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
      if (!isTopicAuto && topic !== "General")
        parts.push(`Write a ${topic} news article`);
      else parts.push("Write a general news article");

      if (!isToneAuto && tone !== "Normal") parts.push(`in a ${tone} tone`);

      const finalPrompt = `${parts.join(" ")} about: ${basePrompt}`;

      const token = localStorage.getItem("access_token");
      const rawUser = localStorage.getItem("user");
      const parsedUser = rawUser ? JSON.parse(rawUser) : {};
      const userId = parsedUser.uid ?? null;

      const response = await fetch(`${import.meta.env.VITE_API_BASE_URL || "http://localhost:8000"}/api/generate/single`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": token ? `Bearer ${token}` : "",
        },
        body: JSON.stringify({
          user_id: userId, 
          topic: finalPrompt,
          image_url_or_b64: image ? await fileToBase64(image) : undefined,
          params: {
            style: tone,    // "Formal" | "Sensational" | "Fun" | "Normal"
            domain: topic,  // "Politics" | "Business" | ... | "General"
          },
        }),
      }).then((r) => r.json());


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
    setIsToneAuto(true);
    setIsTopicAuto(true);
    if (inputRef.current) inputRef.current.value = "";
    [
      "generatedNews",
      "newsInput",
      "newsTone",
      "newsTopic",
      "visionText",
      "sourceUrl",
      "newsToneAuto",
      "newsTopicAuto"
    ].forEach((key) => localStorage.removeItem(key));
    localStorage.setItem("newsToneAuto", "true");
    localStorage.setItem("newsTopicAuto", "true");
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
            Powered by LLM
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
              <div className="flex items-center justify-between">
                <label className="text-sm font-medium">
                  Style{" "}
                  <span className="text-xs text-muted-foreground">
                    {isToneAuto ? "(auto-selected)" : "(manual override)"}
                  </span>
                </label>
                {!isToneAuto && (
                  <Button
                    type="button"
                    variant="ghost"
                    size="sm"
                    onClick={resetToneToAuto}
                  >
                    Reset
                  </Button>
                )}
              </div>
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
              <div className="flex items-center justify-between">
                <label className="text-sm font-medium">
                  Topic{" "}
                  <span className="text-xs text-muted-foreground">
                    {isTopicAuto ? "(auto-selected)" : "(manual override)"}
                  </span>
                </label>
                {!isTopicAuto && (
                  <Button
                    type="button"
                    variant="ghost"
                    size="sm"
                    onClick={resetTopicToAuto}
                  >
                    Reset
                  </Button>
                )}
              </div>
              <select
                value={topic}
                onChange={handleTopicChange}
                className="w-full p-2 rounded-md border border-gray-300 dark:border-input bg-gray-50 dark:bg-background text-foreground focus:ring-2 focus:ring-blue-400 dark:focus:ring-ring focus:outline-none"
              >
                <option value="Politics">Politics — Government and elections.</option>
                <option value="Business">Business — Markets and economics.</option>
                <option value="Sports">Sports — Games and events.</option>
                <option value="Technology">Technology — Innovations and trends.</option>
                <option value="Health">Health — Medical and wellness topics.</option>
                <option value="Environment">Environment — Climate and ecology.</option>
                <option value="Science">Science — Research and discovery.</option>
                <option value="Crime">Crime — Security and legal incidents.</option>
                <option value="Entertainment">Entertainment — Culture and events.</option>
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
