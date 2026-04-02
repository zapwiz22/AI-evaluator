import React from "react";

const AssessmentChart = ({ visualMetrics = [] }) => {
  if (!Array.isArray(visualMetrics) || visualMetrics.length === 0) {
    return null;
  }

  const width = 700;
  const barHeight = 24;
  const gap = 16;
  const leftPad = 180;
  const rightPad = 30;
  const topPad = 12;
  const usableWidth = width - leftPad - rightPad;
  const height = topPad * 2 + visualMetrics.length * (barHeight + gap);

  return (
    <svg
      width="100%"
      viewBox={`0 0 ${width} ${height}`}
      role="img"
      aria-label="Report quality metrics chart"
    >
      {visualMetrics.map((metric, index) => {
        const y = topPad + index * (barHeight + gap);
        const safeValue = Math.max(0, Math.min(100, Number(metric.value) || 0));
        const barWidth = (safeValue / 100) * usableWidth;

        return (
          <g key={`${metric.label}-${index}`}>
            <text x={10} y={y + 17} fill="#334155" fontSize="13">
              {metric.label}
            </text>
            <rect
              x={leftPad}
              y={y}
              width={usableWidth}
              height={barHeight}
              rx={6}
              fill="#e2e8f0"
            />
            <rect
              x={leftPad}
              y={y}
              width={barWidth}
              height={barHeight}
              rx={6}
              fill="#0ea5e9"
            />
            <text
              x={leftPad + usableWidth + 8}
              y={y + 17}
              fill="#0f172a"
              fontSize="12"
            >
              {safeValue.toFixed(1)}%
            </text>
          </g>
        );
      })}
    </svg>
  );
};

const SummaryCard = ({ evaluation }) => {
  if (!evaluation) {
    return null;
  }

  const findings = Array.isArray(evaluation.key_findings)
    ? evaluation.key_findings
    : [];
  const tableColumns = evaluation.table_data?.columns || [];
  const tableRows = evaluation.table_data?.rows || [];
  const assessment = evaluation.report_assessment || {};
  const strengths = Array.isArray(assessment.strengths)
    ? assessment.strengths
    : [];
  const weaknesses = Array.isArray(assessment.weaknesses)
    ? assessment.weaknesses
    : [];
  const visualMetrics = Array.isArray(assessment.visual_metrics)
    ? assessment.visual_metrics
    : [];
  const plotImage = assessment.plot_image_base64 || "";

  return (
    <div
      style={{
        background: "#ffffff",
        padding: "20px",
        borderRadius: "8px",
        border: "1px solid #dee2e6",
        boxShadow: "0 2px 4px rgba(0,0,0,0.05)",
      }}
    >
      <h3
        style={{
          marginTop: 0,
          borderBottom: "1px solid #eee",
          paddingBottom: "10px",
        }}
      >
        Document Brief
      </h3>
      <p style={{ lineHeight: "1.6", marginBottom: "16px" }}>
        {evaluation.summary || "No summary available."}
      </p>

      <h3
        style={{
          marginTop: 0,
          borderBottom: "1px solid #eee",
          paddingBottom: "10px",
        }}
      >
        Key Findings
      </h3>
      <ul
        style={{ lineHeight: "1.6", paddingLeft: "20px", marginBottom: "16px" }}
      >
        {findings.map((finding, index) => (
          <li key={`${finding}-${index}`} style={{ marginBottom: "8px" }}>
            {finding}
          </li>
        ))}
      </ul>

      {visualMetrics.length > 0 && (
        <>
          <h3
            style={{
              marginTop: 0,
              borderBottom: "1px solid #eee",
              paddingBottom: "10px",
            }}
          >
            Report Quality Visual
          </h3>
          <p style={{ margin: "0 0 10px 0", color: "#334155" }}>
            Overall Score:{" "}
            <strong>
              {Number(assessment.overall_score || 0).toFixed(1)} / 100
            </strong>
          </p>
          <AssessmentChart visualMetrics={visualMetrics} />

          {plotImage && (
            <div style={{ marginTop: "14px" }}>
              <h4 style={{ margin: "0 0 8px 0", color: "#0f172a" }}>
                Generated Plot (Matplotlib)
              </h4>
              <img
                src={plotImage}
                alt="Report metrics plot"
                style={{
                  width: "100%",
                  maxWidth: "760px",
                  border: "1px solid #e2e8f0",
                  borderRadius: "8px",
                }}
              />
            </div>
          )}
        </>
      )}

      {(strengths.length > 0 || weaknesses.length > 0) && (
        <>
          <h3
            style={{
              marginTop: "18px",
              borderBottom: "1px solid #eee",
              paddingBottom: "10px",
            }}
          >
            Strengths and Weaknesses
          </h3>
          <div
            style={{
              display: "grid",
              gridTemplateColumns: "1fr 1fr",
              gap: "14px",
            }}
          >
            <div
              style={{
                background: "#ecfdf3",
                border: "1px solid #bbf7d0",
                borderRadius: "8px",
                padding: "12px",
              }}
            >
              <h4 style={{ margin: "0 0 8px 0", color: "#166534" }}>
                Strengths
              </h4>
              <ul style={{ margin: 0, paddingLeft: "20px", lineHeight: "1.5" }}>
                {(strengths.length
                  ? strengths
                  : ["No major strengths were automatically detected."]
                ).map((item, idx) => (
                  <li key={`strength-${idx}`}>{item}</li>
                ))}
              </ul>
            </div>
            <div
              style={{
                background: "#fef2f2",
                border: "1px solid #fecaca",
                borderRadius: "8px",
                padding: "12px",
              }}
            >
              <h4 style={{ margin: "0 0 8px 0", color: "#991b1b" }}>
                Weaknesses
              </h4>
              <ul style={{ margin: 0, paddingLeft: "20px", lineHeight: "1.5" }}>
                {(weaknesses.length
                  ? weaknesses
                  : ["No major weaknesses were automatically detected."]
                ).map((item, idx) => (
                  <li key={`weakness-${idx}`}>{item}</li>
                ))}
              </ul>
            </div>
          </div>
        </>
      )}

      {tableColumns.length > 0 && (
        <>
          <h3
            style={{
              marginTop: 0,
              borderBottom: "1px solid #eee",
              paddingBottom: "10px",
            }}
          >
            Extracted Table
          </h3>
          <div style={{ overflowX: "auto" }}>
            <table style={{ width: "100%", borderCollapse: "collapse" }}>
              <thead>
                <tr>
                  {tableColumns.map((column, idx) => (
                    <th
                      key={`${column}-${idx}`}
                      style={{
                        textAlign: "left",
                        borderBottom: "1px solid #ddd",
                        padding: "8px",
                      }}
                    >
                      {column}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {tableRows.map((row, rowIndex) => (
                  <tr key={`row-${rowIndex}`}>
                    {row.map((cell, cellIndex) => (
                      <td
                        key={`cell-${rowIndex}-${cellIndex}`}
                        style={{
                          borderBottom: "1px solid #f2f2f2",
                          padding: "8px",
                        }}
                      >
                        {cell}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      )}
    </div>
  );
};

export default SummaryCard;
