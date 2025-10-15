import { useRef, useState } from "react";
import { motion } from "motion/react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { useNavigate } from "react-router-dom"; 

const MAX_LEN = 10000;

const Detection = () => {
  const navigate = useNavigate(); 
  const [text, setText] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [fileName, setFileName] = useState<string>("");
  const [url, setUrl] = useState("");
  const inputRef = useRef<HTMLInputElement | null>(null);

  const onTextChange = (v: string) => {
    if (v.length > MAX_LEN) {
      setError(`Text too long. Max ${MAX_LEN} characters.`);
    } else {
      setError(null);
    }
    setText(v.slice(0, MAX_LEN));
  };

  const handleUpload = async (file?: File | null) => {
    if (!file) return;
    setFileName(file.name);
    if (file.type && file.type !== "text/plain") {
      setError("Only .txt files are supported for upload.");
      return;
    }
    try {
      const content = await file.text();
      onTextChange(content);
    } catch {
      setError("Failed to read file.");
    }
  };

  const handleFetchFromUrl = async () => {
    if (!url.trim()) {
      setError("Please enter a valid URL first.");
      return;
    }
    try {
      setError(null);
      const res = await fetch(url);
      const html = await res.text();
      const stripped = html.replace(/<[^>]*>?/gm, "").slice(0, MAX_LEN);
      onTextChange(stripped);
      console.log("Fetched content from URL:", url, stripped.slice(0, 100));
    } catch (err) {
      setError("Failed to fetch content from URL.");
    }
  };

  const handleScan = () => {
    if (!text.trim()) {
      setError("Please paste, upload, or fetch some text first.");
      return;
    }
    setError(null);

    const ok = window.confirm("Scan finished. Do you want to view result?");
    if (ok) {
      navigate("/result", { state: { source: "detection", text } });
    }
  };

  const handleClear = () => {
    setText("");
    setError(null);
    setFileName("");
    setUrl("");
    if (inputRef.current) inputRef.current.value = "";
  };

  const triggerFileDialog = () => inputRef.current?.click();

  return (
    <div className="min-h-screen flex flex-col lg:flex-row items-start justify-center gap-8 px-6 py-12 bg-background text-foreground">

      <motion.section
        initial={{ opacity: 0, x: -30 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ duration: 0.5 }}
        className="flex-1 max-w-xl"
      >
        <h1 className="text-4xl font-bold mb-6 leading-snug">
          AI Text Detection
        </h1>
        <p className="text-lg text-muted-foreground mb-4">
          Paste, upload, or fetch text from a URL and we'll run <strong>AI-generated content detection</strong> on it.
        </p>
        <ul className="list-disc pl-5 text-muted-foreground space-y-2">
          <li>Support direct pasting of text, uploading <code>.txt</code> files, or fetching from URL.</li>
          <li>A maximum of {MAX_LEN.toLocaleString()} characters per entry.</li>
          <li>Results can be linked with the Generate page to form a “Generate → Detect” workflow.</li>
        </ul>
      </motion.section>

      <motion.section
        initial={{ opacity: 0, x: 30 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ duration: 0.5 }}
        className="flex-1 w-full max-w-2xl"
      >
        <Card className="w-full shadow-lg border border-border">
          <CardContent className="p-6 flex flex-col gap-4">
            <div className="flex items-center justify-between">
              <div className="text-sm text-muted-foreground">
                Please paste your text, upload a .txt file, or fetch from URL
              </div>
            </div>

            <div className="flex gap-3">
              <input
                type="url"
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                placeholder="Enter a webpage URL..."
                className="flex-1 rounded-md px-3 py-2 border border-input bg-background text-foreground focus:ring-2 focus:ring-ring focus:outline-none"
              />
              <Button variant="outline" onClick={handleFetchFromUrl}>
                Fetch
              </Button>
            </div>

            <textarea
              value={text}
              onChange={(e) => onTextChange(e.target.value)}
              placeholder="Paste your text here..."
              className="w-full h-56 rounded-md p-4 border border-input bg-background text-foreground focus:ring-2 focus:ring-ring focus:outline-none resize-none"
            />

            <div className="flex items-center justify-between gap-4">
              <input
                ref={inputRef}
                type="file"
                accept=".txt,text/plain"
                className="hidden"
                onChange={(e) => handleUpload(e.target.files?.[0])}
              />

              <div className="flex items-center gap-3">
                <Button variant="outline" onClick={triggerFileDialog}>
                  Choose File
                </Button>
                <span className="text-sm text-muted-foreground">
                  {fileName ? fileName : "No file chosen"}
                </span>
              </div>

              <div className="flex gap-3">
                <Button variant="outline" onClick={handleClear}>
                  Clear
                </Button>
                <Button variant="default" onClick={handleScan}>
                  Scan
                </Button>
              </div>
            </div>

            {error && <div className="text-sm text-red-500">{error}</div>}
          </CardContent>
        </Card>
      </motion.section>
    </div>
  );
};

export default Detection;
