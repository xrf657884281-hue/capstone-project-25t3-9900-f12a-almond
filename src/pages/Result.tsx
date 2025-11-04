import { useLocation, useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { HighlightedText } from "@/components/HighlightedText";

type Analysis = {
  isFake?: boolean;
  verdict?: string;
  aiConfidence?: number;
  humanConfidence?: number;
  readability?: number;
  mostAISentences?: string[];
  notes?: string;
  confidence?: number;
  fake_probability?: number;
  explanation?: string;
  details?: any;
};

const clamp01 = (v: number | undefined) => {
  if (typeof v !== "number" || Number.isNaN(v)) return 0;
  return Math.max(0, Math.min(100, v));
};

const Progress = ({ value }: { value?: number }) => {
  const v = clamp01(value);
  return (
    <div className="w-full h-2 rounded bg-muted/60">
      <div
        className="h-2 rounded bg-primary transition-all"
        style={{ width: `${v}%` }}
      />
    </div>
  );
};

const Result = () => {
  const navigate = useNavigate();
  const { state } = useLocation() as {
    state?: { source?: string; text?: string; analysis?: Analysis };
  };

  const text = state?.text ?? "";
  const analysis = state?.analysis ?? {};

  // FAKE / TRUE
  const verdict: "FAKE" | "TRUE" | "" =
    typeof analysis.isFake === "boolean"
      ? analysis.isFake
        ? "FAKE"
        : "TRUE"
      : typeof analysis.verdict === "string"
      ? (analysis.verdict.toUpperCase() as "FAKE" | "TRUE")
      : "";

  const handleCopy = async () => {
    if (!text) return;
    try {
      await navigator.clipboard.writeText(text);
      alert("Copied to clipboard!");
    } catch {
      alert("Failed to copy.");
    }
  };

  const handleBack = () => {
    navigate("/profile");
  };

  const handleCardClick = (cardNumber: number) => {
    console.log(`Card ${cardNumber} clicked`);
    // Add your click logic here
    // e.g., navigate to another page or show a modal
  };

  return (
    <div className="min-h-screen px-6 py-10 bg-background text-foreground">
      <div className="mx-auto w-full max-w-7xl grid grid-cols-1 lg:grid-cols-12 gap-6">
        <div className="lg:col-span-7 space-y-4">
          <h1 className="text-2xl font-bold text-center mb-4">Result</h1>

          <Card className="border border-gray-300 dark:border-border shadow">
            <CardContent className="p-4">
              <div className="flex justify-end mb-3 gap-2">
                <Button variant="outline" onClick={handleCopy} className="border border-gray-300 dark:border-border shadow">
                  Copy
                </Button>
                <Button variant="outline" onClick={handleBack} className="border border-gray-300 dark:border-border shadow">
                  Back to Profile
                </Button>
              </div>

              {(analysis.readability ?? 0) > 0 &&
                analysis.details?.baseline_results?.text_detection?.detectgpt
                  ?.reasoning &&
                analysis.details.baseline_results.text_detection.detectgpt.reasoning
                  .length > 0 && (
                  <div className="mb-3 p-2 bg-yellow-50 border border-yellow-200 rounded-md">
                    <p className="text-xs text-yellow-800">
                      Detected errors are highlighted in red, hover to view detailed
                      error information.
                    </p>
                  </div>
                )}

              {text ? (
                <div className="rounded-md border border-gray-300 dark:border-border bg-gray-50 dark:bg-card p-4 text-card-foreground max-h-[60vh] overflow-auto">
                  <div className="text-sm">
                    <HighlightedText
                      text={text}
                      errors={
                        (analysis.readability ?? 0) > 0
                          ? analysis.details?.baseline_results?.text_detection
                              ?.detectgpt?.reasoning || []
                          : []
                      }
                      className="text-sm"
                    />
                  </div>
                </div>
              ) : (
                <div className="text-sm text-muted-foreground">
                  No content provided. Please go back and run a scan or generate
                  something first.
                </div>
              )}
            </CardContent>
          </Card>

          <h1 className='font-bold text-3lg'>Related News</h1>

          <div className="grid grid-cols-4 gap-4">
            <Card
              className="border border-gray-300 dark:border-border shadow cursor-pointer hover:shadow-lg hover:scale-105 transition-all duration-200"
              onClick={() => handleCardClick(1)}
            >
              <CardContent className="p-4">
                <h3 className="text-sm font-semibold mb-2">Card 1</h3>
                <p className="text-xs text-muted-foreground">Content here</p>
              </CardContent>
            </Card>

            <Card
              className="border border-gray-300 dark:border-border shadow cursor-pointer hover:shadow-lg hover:scale-105 transition-all duration-200"
              onClick={() => handleCardClick(2)}
            >
              <CardContent className="p-4">
                <h3 className="text-sm font-semibold mb-2">Card 2</h3>
                <p className="text-xs text-muted-foreground">Content here</p>
              </CardContent>
            </Card>

            <Card
              className="border border-gray-300 dark:border-border shadow cursor-pointer hover:shadow-lg hover:scale-105 transition-all duration-200"
              onClick={() => handleCardClick(3)}
            >
              <CardContent className="p-4">
                <h3 className="text-sm font-semibold mb-2">Card 3</h3>
                <p className="text-xs text-muted-foreground">Content here</p>
              </CardContent>
            </Card>

            <Card
              className="border border-gray-300 dark:border-border shadow cursor-pointer hover:shadow-lg hover:scale-105 transition-all duration-200"
              onClick={() => handleCardClick(4)}
            >
              <CardContent className="p-4">
                <h3 className="text-sm font-semibold mb-2">Card 4</h3>
                <p className="text-xs text-muted-foreground">Content here</p>
              </CardContent>
            </Card>
          </div>
        </div>
      
        <div className="lg:col-span-5 space-y-4">
          <h2 className="text-lg font-semibold">Basic Scan</h2>
          <Card className="border border-gray-300 dark:border-border shadow">
            <CardContent className="p-4 space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium">Detection Result</span>
                {verdict ? (
                  <span
                    className={
                      "px-2 py-1 rounded text-xs font-semibold border " +
                      (verdict === "FAKE" && (analysis.readability ?? 0) > 0
                        ? "bg-red-100 text-red-800 border-red-300"
                        : "bg-green-100 text-green-800 border-green-300")
                    }
                  >
                    {verdict}
                  </span>
                ) : (
                  <span className="text-sm text-muted-foreground">&nbsp;</span>
                )}
              </div>

              {/* Confidence */}
              <div className="flex items-center justify-between pt-2">
                <span className="text-sm font-medium">Confidence</span>
                <span className="text-sm">
                  {typeof analysis.humanConfidence === "number"
                    ? `${clamp01(analysis.humanConfidence)}%`
                    : "--"}
                </span>
              </div>
              <Progress value={analysis.humanConfidence} />

              {/* Fake Probability */}
              <div className="flex items-center justify-between pt-2">
                <span className="text-sm font-medium">Fake Probability</span>
                <span className="text-sm">
                  {typeof analysis.readability === "number"
                    ? `${clamp01(analysis.readability)}%`
                    : "--"}
                </span>
              </div>
              <Progress value={analysis.readability} />
            </CardContent>
          </Card>
          <Card className="border border-gray-300 dark:border-border shadow">
            <CardContent className="p-4 space-y-4">
              <div className="flex items-center gap-2">
                <h3 className="font-semibold text-sm">🤖 Analysis</h3>
                {analysis.details?.baseline_results?.text_detection?.detectgpt
                  ?.verdict && (
                  <span className="px-2 py-0.5 rounded text-xs font-medium bg-blue-100 text-blue-800 border border-blue-300">
                    {analysis.details.baseline_results.text_detection.detectgpt.verdict.toUpperCase()}
                  </span>
                )}
              </div>

              {analysis.details?.baseline_results?.text_detection?.detectgpt
                ?.reasoning && (
                <div className="space-y-2">
                  {analysis.details.baseline_results.text_detection.detectgpt.reasoning.map(
                    (reason: string, i: number) => {
                      const titleMatch = reason.match(/\*\*(.*?)\*\*/);
                      if (titleMatch) {
                        const title = titleMatch[1];
                        let content = reason
                          .replace(/\*\*(.*?)\*\*/, "")
                          .trim();
                        content = content.replace(/^:\s*/, "");
                        return (
                          <div
                            key={i}
                            className="text-sm bg-blue-50 rounded-md border border-blue-300 p-3"
                          >
                            <p className="text-gray-700">
                              <span className="font-bold text-gray-800">
                                {title}:
                              </span>{" "}
                              {content}
                            </p>
                          </div>
                        );
                      }
                      return (
                        <div
                          key={i}
                          className="text-sm bg-blue-50 rounded-md border border-blue-300 p-3"
                        >
                          <p className="text-gray-700">{reason}</p>
                        </div>
                      );
                    }
                  )}
                </div>
              )}

              {Array.isArray(analysis.mostAISentences) &&
                analysis.mostAISentences.length > 0 && (
                  <div className="space-y-2">
                    <h4 className="text-xs font-bold text-gray-700 uppercase tracking-wide">
                      Key Factors
                    </h4>
                    {analysis.mostAISentences.map((s, i) => (
                      <div
                        key={i}
                        className="text-sm bg-gray-50 rounded-md border border-gray-300 p-2"
                      >
                        <strong>{s}</strong>
                      </div>
                    ))}
                  </div>
                )}

              {analysis.details?.baseline_results?.text_detection?.detectgpt && (
                <div className="pt-3 border-t border-gray-300">
                  <div className="flex items-center justify-between text-xs text-gray-500">
                    <span>
                      Model:{" "}
                      {
                        analysis.details.baseline_results.text_detection
                          .detectgpt.model
                      }
                    </span>
                    <span>
                      Confidence:{" "}
                      {(
                        analysis.details.baseline_results.text_detection.detectgpt
                          .confidence * 100
                      ).toFixed(0)}
                      %
                    </span>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Fact Verification */}
          {(analysis.details?.tavily_verification ||
            analysis.details?.wikipedia_verification) && (
            <Card className="border border-gray-300 dark:border-border shadow">
              <CardContent className="p-4">
                <div className="flex items-center gap-2 mb-3">
                  <h3 className="font-semibold text-sm">🔍 Fact Verification</h3>
                  <span className="px-2 py-0.5 rounded text-xs font-medium bg-purple-100 text-purple-800 border border-purple-300">
                    TAVILY
                  </span>
                </div>
                <div className="space-y-2">
                  {(() => {
                    const verification =
                      analysis.details?.tavily_verification ||
                      analysis.details?.wikipedia_verification;
                    const coverage =
                      verification?.tavily_coverage ||
                      verification?.wikipedia_coverage ||
                      0;
                    const score = verification?.overall_score || 0;
                    const entitiesFound = verification?.entities_found || 0;
                    const entitiesChecked = verification?.entities_checked || 1;

                    return (
                      <>
                        <div className="flex items-center justify-between text-sm">
                          <span className="text-gray-600">
                            Verification Score
                          </span>
                          <span
                            className={`font-semibold ${
                              score * 100 < 30
                                ? "text-red-600"
                                : score * 100 < 60
                                ? "text-yellow-600"
                                : "text-green-600"
                            }`}
                          >
                            {(score * 100).toFixed(1)}%
                          </span>
                        </div>
                        <Progress value={score * 100} />

                        <div className="grid grid-cols-2 gap-2 mt-3 text-xs">
                          <div className="bg-gray-50 rounded p-2 border border-gray-300">
                            <div className="text-gray-500 mb-1 font-bold">
                              Coverage
                            </div>
                            <div className="font-semibold text-lg mb-1">
                              {(coverage * 100).toFixed(0)}%
                            </div>
                            <div className="text-gray-400 text-[10px]">
                              {coverage >= 0.8
                                ? "✅ High coverage"
                                : coverage >= 0.5
                                ? "⚠️ Moderate coverage"
                                : "❌ Low coverage"}
                            </div>
                          </div>
                          <div className="bg-gray-50 rounded p-2 border border-gray-300">
                            <div className="text-gray-500 mb-1 font-bold">
                              Entities Found
                            </div>
                            <div className="font-semibold text-lg mb-1">
                              {entitiesFound}/{entitiesChecked}
                            </div>
                            <div className="text-gray-400 text-[10px]">
                              {entitiesChecked > 0
                                ? `${(
                                    (entitiesFound / entitiesChecked) *
                                    100
                                  ).toFixed(0)}% verified`
                                : "No entities checked"}
                            </div>
                          </div>
                        </div>
                      </>
                    );
                  })()}
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
};

export default Result;
