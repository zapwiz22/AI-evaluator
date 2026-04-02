import React, { useEffect, useId, useRef } from "react";
import mermaid from "mermaid";

mermaid.initialize({
  startOnLoad: true,
  theme: "default",
  securityLevel: "loose",
});

const normalizeChartCode = (chartCode) => {
  if (!chartCode) return "";

  return chartCode
    .replace(/^```(?:mermaid|json)?\s*/i, "")
    .replace(/\s*```$/i, "")
    .trim();
};

const fallbackChartCode = [
  "graph TD",
  "  A[Document Uploaded] --> B[Text Extracted]",
  "  B --> C[AI Analysis]",
  "  C --> D[Review Complete]",
].join("\n");

const Flowchart = ({ chartCode }) => {
  const containerRef = useRef(null);
  const renderId = useId().replace(/:/g, "-");

  useEffect(() => {
    if (chartCode && containerRef.current) {
      // Clear previous chart
      containerRef.current.innerHTML = "";
      // Render new chart
      const normalizedCode = normalizeChartCode(chartCode);

      mermaid
        .render(`mermaid-chart-${renderId}`, normalizedCode)
        .then((result) => {
          containerRef.current.innerHTML = result.svg;
        })
        .catch((err) => {
          console.error("Mermaid syntax error:", err);
          mermaid
            .render(`mermaid-chart-${renderId}-fallback`, fallbackChartCode)
            .then((result) => {
              containerRef.current.innerHTML = result.svg;
            })
            .catch((fallbackErr) => {
              console.error("Fallback Mermaid syntax error:", fallbackErr);
              containerRef.current.innerHTML =
                '<p style="color:red;">Error rendering flowchart.</p>';
            });
        });
    }
  }, [chartCode, renderId]);

  return <div ref={containerRef} className="mermaid-container" />;
};

export default Flowchart;
