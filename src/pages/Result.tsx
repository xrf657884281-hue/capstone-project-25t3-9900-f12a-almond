import { useLocation, useNavigate } from "react-router-dom";
import { useState, useEffect } from "react";
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
    state?: { source?: string; text?: string; analysis?: Analysis; record_id?: string; };
  };

  const text = state?.text ?? "";
  const analysis = state?.analysis ?? {};

  const [relatedNews, setRelatedNews] = useState<any[]>([]);
  const [loadingNews, setLoadingNews] = useState(false);

  useEffect(() => {
    const fetchRelatedNews = async () => {
      if (!text) return;
      
      setLoadingNews(true);
      try {
        // Use smart news finder with entity extraction
        const response = await fetch(
          `http://localhost:8000/api/news/find_related`,
          {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              text: text,
              detection_result: analysis.details || null,
              max_results: 4,
              language: 'en'
            })
          }
        );
        const data = await response.json();
        
        if (data.success && data.result?.articles) {
          setRelatedNews(data.result.articles);
          console.log('📰 Smart news search used query:', data.result.search_query);
          console.log('📝 Entities extracted:', data.result.entities_used);
          console.log('🔑 Keywords extracted:', data.result.keywords_used);
        }
      } catch (error) {
        console.error('Failed to fetch related news:', error);
      } finally {
        setLoadingNews(false);
      }
    };

    fetchRelatedNews();
  }, [text, analysis]);

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
  const handleGeneratePDF = async () => {
    if (!state?.record_id) {
      alert("⚠️ No record ID found for PDF generation.");
      return;
    }
    try {
      const baseUrl = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";
      const res = await fetch(`${baseUrl}/api/detection/history/${state.record_id}/generate_pdf`, {
        method: "POST",
      });
      const data = await res.json();
      if (!res.ok || !data.success) throw new Error(data.detail || "PDF generation failed");
      alert("✅ PDF generated successfully!");
    } catch (err) {
      console.error(err);
      alert("❌ Failed to generate PDF.");
    }
  };

  const handleExportPDF = async () => {
    if (!state?.record_id) {
      alert("⚠️ No record ID found for PDF export.");
      return;
    }
    try {
      const baseUrl = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";
      const res = await fetch(`${baseUrl}/api/detection/history/${state.record_id}/pdf`);
      if (!res.ok) throw new Error("Failed to fetch PDF");
      const blob = await res.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `detection_${state.record_id}.pdf`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      console.error(err);
      alert("❌ Failed to export PDF.");
    }
  };

  const handleDelete = async () => {
    if (!state?.record_id) {
      alert("No record ID found.");
      return;
    }
    const confirmDelete = window.confirm("Are you sure you want to delete this record?");
    if (!confirmDelete) return;

    try {
      const baseUrl = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";
      const res = await fetch(`${baseUrl}/api/detection/history/${state.record_id}`, {
        method: "DELETE",
      });
      if (!res.ok) throw new Error("Failed to delete record");
      alert("✅ Record deleted successfully!");
      navigate("/profile");
    } catch (err) {
      console.error(err);
      alert("❌ Failed to delete the record.");
    }
  };

  return (
    <div className="min-h-screen px-6 py-10 bg-background text-foreground">
      <div className="mx-auto w-full max-w-7xl grid grid-cols-1 lg:grid-cols-12 gap-6">
        <div className="lg:col-span-7 space-y-4">
          <h1 className="text-2xl font-bold text-center mb-4">Result</h1>

          <Card className="border border-gray-300 dark:border-border shadow">
            <CardContent className="p-4">
              <div className="flex justify-between mb-3">
                <div className="flex gap-2">
                  <Button
                    variant="secondary"
                    onClick={handleGeneratePDF}
                    className="border border-gray-300 dark:border-border shadow"
                  >
                    🧾 Generate PDF
                  </Button>
                  <Button
                    variant="secondary"
                    onClick={handleExportPDF}
                    className="border border-gray-300 dark:border-border shadow"
                  >
                    📤 Export PDF
                  </Button>
                  <Button
                    variant="destructive"
                    onClick={handleDelete}
                    className="border border-gray-300 dark:border-border shadow bg-red-600 hover:bg-red-700 text-white"
                  >
                    Delete Record
                  </Button>
                </div>
                <div className="flex gap-2">
                  <Button
                    variant="outline"
                    onClick={handleCopy}
                    className="border border-gray-300 dark:border-border shadow"
                  >
                    Copy
                  </Button>
                  <Button
                    variant="outline"
                    onClick={handleBack}
                    className="border border-gray-300 dark:border-border shadow"
                  >
                    Back to Profile
                  </Button>
                </div>
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
            {loadingNews ? (
              <div className="col-span-4 text-center py-8 text-muted-foreground">
                Loading related news...
              </div>
            ) : relatedNews.length > 0 ? (
              relatedNews.map((article, idx) => (
                <Card
                  key={idx}
                  className="border border-gray-300 dark:border-border shadow cursor-pointer hover:shadow-lg hover:scale-105 transition-all duration-200"
                  onClick={() => window.open(article.url, '_blank')}
                >
                  <CardContent className="p-4">
                    {article.urlToImage && (
                      <img
                        src={article.urlToImage}
                        alt={article.title}
                        className="w-full h-24 object-cover rounded mb-2"
                        onError={(e) => { (e.target as HTMLImageElement).style.display = 'none'; }}
                      />
                    )}
                    <h3 className="text-sm font-semibold mb-2 line-clamp-2">
                      {article.title || 'No title'}
                    </h3>
                    <p className="text-xs text-muted-foreground line-clamp-3 mb-2">
                      {article.description || 'No description available'}
                    </p>
                    <div className="text-xs text-blue-600 font-medium">
                      {article.source?.name || 'Unknown source'}
                    </div>
                  </CardContent>
                </Card>
              ))
            ) : (
              <div className="col-span-4 text-center py-8 text-muted-foreground">
                No related news found
              </div>
            )}
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
                            {(() => {
                              console.log('🔍 DEBUG: verification object:', verification);
                              console.log('🔍 DEBUG: entity_results exists?', verification?.entity_results);
                              console.log('🔍 DEBUG: entity_results length:', verification?.entity_results?.length);
                              
                              if (verification?.entity_results && verification.entity_results.length > 0) {
                                console.log('✅ Rendering entity results:', verification.entity_results);
                                return (
                                  <div className="mt-2 pt-2 border-t border-gray-200">
                                    <div className="text-[10px] text-gray-500 mb-1">Found entities:</div>
                                    <div className="space-y-1">
                                      {verification.entity_results.slice(0, 3).map((entity: any, idx: number) => (
                                        <div key={idx} className="flex items-center gap-1 text-[10px]">
                                          <span className={entity.exists ? "text-green-600" : "text-red-600"}>
                                            {entity.exists ? "✓" : "✗"}
                                          </span>
                                          <span className="text-gray-700 truncate">
                                            {entity.entity}
                                          </span>
                                        </div>
                                      ))}
                                      {verification.entity_results.length > 3 && (
                                        <div className="text-[10px] text-gray-400 italic">
                                          +{verification.entity_results.length - 3} more
                                        </div>
                                      )}
                                    </div>
                                  </div>
                                );
                              } else {
                                console.log('❌ Entity results not found or empty');
                                return null;
                              }
                            })()}
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
