import { useLocation, useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";

type Analysis = {
  isFake?: boolean;              
  verdict?: string;             
  aiConfidence?: number;      
  humanConfidence?: number;   
  readability?: number;       
  mostAISentences?: string[];  
  notes?: string;
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

  // FAKE/TRUE
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
    if (state?.source === "detection") navigate("/detection");
    else if (state?.source === "generate") navigate("/generate");
    else navigate("/profile");
  };

  return (
    <div className="min-h-screen px-6 py-10 bg-background text-foreground">
      <div className="mx-auto w-full max-w-7xl grid grid-cols-1 lg:grid-cols-12 gap-6">
        <div className="lg:col-span-7 space-y-4">
          <h1 className="text-2xl font-bold">Result</h1>

          <Card className="border border-border">
            <CardContent className="p-4">
              <div className="flex items-center justify-between mb-3">
                <p className="text-sm text-muted-foreground">
                  {state?.source ? `Source: ${state.source}` : "Preview of the content"}
                </p>
                <div className="flex gap-2">
                  <Button variant="outline" onClick={handleCopy}>Copy</Button>
                  <Button variant="outline" onClick={handleBack}>Back</Button>
                </div>
              </div>

              {text ? (
                <div className="rounded-md border p-4 bg-card text-card-foreground max-h-[60vh] overflow-auto">
                  <pre className="whitespace-pre-wrap break-words text-sm">
                    {text}
                  </pre>
                </div>
              ) : (
                <div className="text-sm text-muted-foreground">
                  No content provided. Please go back and run a scan or generate something first.
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        <div className="lg:col-span-5 space-y-4">
          <h2 className="text-lg font-semibold">Basic scan</h2>

          {/* Detection Result */}
          <Card className="border border-border">
            <CardContent className="p-4 space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium">Detection Result</span>
                {verdict ? (
                  <span
                    className={
                      "px-2 py-1 rounded text-xs font-semibold border " +
                      (verdict === "FAKE"
                        ? "bg-red-100 text-red-800 border-red-200"
                        : "bg-green-100 text-green-800 border-green-200")
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

          {/* Analysis */}
          <Card className="border border-border">
            <CardContent className="p-4 space-y-3">
              <h3 className="font-semibold text-sm">Analysis</h3>

              {Array.isArray(analysis.mostAISentences) && analysis.mostAISentences.length > 0 ? (
                <div className="space-y-2">
                  {analysis.mostAISentences.map((s, i) => (
                    <div key={i} className="text-sm bg-muted/70 rounded-md border p-2">
                      {s}
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-sm text-muted-foreground">none.</div>
              )}
            </CardContent>
          </Card>

          {/* Notes */}
          <Card className="border border-border">
            <CardContent className="p-4">
              <h3 className="font-semibold text-sm mb-2">Notes</h3>
              {analysis.notes ? (
                <p className="text-sm text-muted-foreground">{analysis.notes}</p>
              ) : (
                <p className="text-sm text-muted-foreground">No notes.</p>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default Result;
