import { useRef, useState } from "react";
import { motion } from "motion/react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { useNavigate } from "react-router-dom";
import { apiService } from "@/services/api";

const MAX_LEN = 10000;

const Detection = () => {
  const navigate = useNavigate();
  const [text, setText] = useState("");
  const [visionText, setVisionText] = useState("");
  const [url, setUrl] = useState("");
  const [image, setImage] = useState<File | null>(null);
  const [imagePreview, setImagePreview] = useState<string | null>(null);
  const [fileName, setFileName] = useState<string>("");
  const [error, setError] = useState<string | null>(null);
  const [isVisionLoading, setIsVisionLoading] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const inputRef = useRef<HTMLInputElement | null>(null);

  const onTextChange = (v: string) => {
    if (v.length > MAX_LEN) {
      setError(`Text too long. Max ${MAX_LEN} characters.`);
    } else {
      setError(null);
    }
    setText(v.slice(0, MAX_LEN));
  };

  const handleUpload = (file?: File | null) => {
    if (!file) return;
    setImage(file);
    setFileName(file.name);
    setVisionText("");
    const previewUrl = URL.createObjectURL(file);
    setImagePreview(previewUrl);
    console.log("Selected image:", file);
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

  const handleFetchFromUrl = async () => {
    if (!url.trim()) {
      setError("Please enter a valid URL first.");
      return;
    }
    try {
      setError(null);
      setIsLoading(true);

      const apiUrl = `${import.meta.env.VITE_API_BASE_URL || "http://localhost:8000"}/api/url/fetch`;
      const response = await fetch(apiUrl, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ url: url.trim() }),
      });
      
      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(errorText || `Backend returned ${response.status}`);
      }
      
      const result = await response.json();
      
      if (result.fetched_content) {
        onTextChange(result.fetched_content);
        setError(null);
      } else {
        onTextChange(url.trim());
        setError("Backend could not extract content from URL. URL has been copied to text field.");
      }
    } catch (err) {
      console.error("Failed to fetch URL content:", err);
      setError("Failed to fetch content from URL. You can still paste the URL directly and click Detect.");
      onTextChange(url.trim());
    } finally {
      setIsLoading(false);
    }
  };

  const handleScan = async () => {
    let contentToDetect = visionText.trim()
      ? visionText.trim()
      : text.trim();

    if (!contentToDetect) {
      setError("Please enter text or describe an image first.");
      return;
    }

    setError(null);
    setIsLoading(true);
    

    try {
      const token = localStorage.getItem("access_token");
      const apiUrl = `${import.meta.env.VITE_API_BASE_URL || "http://localhost:8000"}/api/detect/improved`;

      console.log("Sending detection request to:", apiUrl);
      console.log("Content to detect:", contentToDetect.substring(0, 100) + "...");

      const response = await fetch(apiUrl, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": token ? `Bearer ${token}` : "",
        },
        body: JSON.stringify({
          text: contentToDetect,
          use_improved_detection: true,
        }),
      });

      console.log("Response status:", response.status, response.statusText);

      if (!response.ok) {
        const errorText = await response.text();
        console.error("API error response:", errorText);
        throw new Error(`API returned ${response.status}: ${errorText.substring(0, 200)}`);
      }

      const result = await response.json();
      console.log("Detection result received:", result.success ? "Success" : "Failed");


      if (result.success) {
        // If backend fetched URL content, display it in the text box
        if ((result as any).fetched_content && (result as any).original_url) {
          onTextChange((result as any).fetched_content);
          console.log("Backend fetched content from URL, displayed in text box");
        }
        
        const finalPrediction = result.result.final_prediction;
        const predictionValue =
          typeof finalPrediction === "string"
            ? finalPrediction
            : (finalPrediction as any).prediction;

        const analysis = {
          isFake: predictionValue === "fake",
          verdict: predictionValue.toUpperCase(),
          humanConfidence:
            (typeof finalPrediction === "object"
              ? (finalPrediction as any).confidence
              : result.result.confidence) * 100,
          readability:
            (typeof finalPrediction === "object"
              ? (finalPrediction as any).fake_probability
              : result.result.fake_probability) * 100,
          notes: result.result.explanation
            ? `Key factors: ${result.result.key_factors.join(", ")}`
            : "No analysis available",
          mostAISentences: result.result.key_factors || [],
          details: result.result,
        };

        const recordId =
          (result as any).record_id ||
          (result as any).result?.record_id ||
          (result as any)._id ||
          (result as any).result?._id ||
          undefined;
        navigate("/result", {
          state: {
            source: "detection",
            text: contentToDetect,
            analysis: analysis,
            record_id: recordId,
          },
        });
      } else {
        setError("Detection failed. Please try again.");
      }
    } catch (err) {
      console.error("Detection error:", err);
      const errorMessage = err instanceof Error ? err.message : String(err);
      
      // Check if it's a network/CORS error
      if (errorMessage.includes("CORS") || errorMessage.includes("Failed to fetch") || errorMessage.includes("NetworkError") || errorMessage.includes("Network request failed")) {
        setError(
          `Network error: Cannot connect to backend. Please check:
          1. Backend is running on http://localhost:8000
          2. No firewall blocking the connection
          3. Check browser console for more details`
        );
      } else if (errorMessage.includes("API returned")) {
        setError(
          `Backend API error: ${errorMessage}. Please check backend logs.`
        );
      } else {
        setError(
          `Detection failed: ${errorMessage}. Please try again or check browser console for details.`
        );
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleClear = () => {
    setText("");
    setVisionText("");
    setImage(null);
    setImagePreview(null);
    setFileName("");
    setUrl("");
    setError(null);
    if (inputRef.current) inputRef.current.value = "";
  };

  return (
    <div className="min-h-screen flex flex-col lg:flex-row items-start justify-center gap-8 px-6 py-12 bg-background text-foreground">
      <motion.section
        initial={{ opacity: 0, x: -30 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ duration: 0.5 }}
        className="flex-1 max-w-xl"
      >
        <h1 className="text-4xl font-bold mb-6 leading-snug">
          AI Content Detection
        </h1>
        <p className="text-lg text-muted-foreground mb-4">
          Detect AI-generated content from text or image.  
          (Webpage detection via URL will be available soon.)
        </p>
        <ul className="list-disc pl-5 text-muted-foreground space-y-2">
          <li>Supports text or image detection.</li>
          <li>Image analysis uses the same model as generator.</li>
          <li>Maximum {MAX_LEN.toLocaleString()} characters per entry.</li>
        </ul>
      </motion.section>

      <motion.section
        initial={{ opacity: 0, x: 30 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ duration: 0.5 }}
        className="flex-1 w-full max-w-2xl"
      >
        <Card className="w-full shadow-md border border-gray-300 dark:border-border bg-gray-50 dark:bg-background transition-colors">
          <CardContent className="p-6 flex flex-col gap-4">
            <div className="flex gap-3">
              <input
                type="url"
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                placeholder="Enter a webpage URL..."
                className="flex-1 rounded-md px-3 py-2 border border-gray-300 dark:border-input bg-gray-50 dark:bg-background text-foreground focus:ring-2 focus:ring-blue-400 dark:focus:ring-ring focus:outline-none"
              />
              <Button
                variant="outline"
                onClick={handleFetchFromUrl}
                disabled={isLoading}
                className="border border-gray-300 dark:border-border bg-gray-50 dark:bg-background hover:bg-gray-100 dark:hover:bg-muted transition-colors"
              >
                Fetch
              </Button>
            </div>

            <textarea
              value={text}
              onChange={(e) => onTextChange(e.target.value)}
              placeholder="Paste or write text for detection..."
              className="w-full h-56 rounded-md p-4 border border-gray-300 dark:border-input bg-gray-50 dark:bg-background text-foreground focus:ring-2 focus:ring-blue-400 dark:focus:ring-ring focus:outline-none resize-none"
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
                <Button
                  variant="outline"
                  onClick={triggerFileDialog}
                  className="border border-gray-300 dark:border-border bg-gray-50 dark:bg-background hover:bg-gray-100 dark:hover:bg-muted transition-colors"
                >
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
                  onChange={(e) => setVisionText(e.target.value)}
                  className="w-full h-32 mt-1 p-3 rounded-md border border-gray-300 dark:border-input bg-gray-50 dark:bg-background text-foreground focus:ring-2 focus:ring-blue-400 dark:focus:ring-ring focus:outline-none resize-none"
                />
              </div>
            )}

            <div className="flex justify-end gap-3 pt-2">
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
                onClick={handleScan}
                disabled={isLoading}
              >
                {isLoading ? "Scanning..." : "Scan"}
              </Button>
            </div>

            {error && <div className="text-sm text-red-500">{error}</div>}
          </CardContent>
        </Card>
      </motion.section>
    </div>
  );
};

export default Detection;
