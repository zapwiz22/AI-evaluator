import React, { useState, useEffect } from "react";
import { uploadDocument } from "../services/api";
import Flowchart from "./Flowchart";
import MetricsGauge from "./MetricsGauge";
import FactChecker from "./FactChecker";
import SummaryCard from "./SummaryCard";

const fallbackChartCode = [
  "graph TD",
  "  A[Document Uploaded] --> B[Text Extracted]",
  "  B --> C[Analysis Complete]",
  "  C --> D[Results Displayed]",
].join("\n");

const statusMessages = [
  "Extracting text from document...",
  "Running AI analysis...",
  "Detecting AI generation and plagiarism...",
  "Fact-checking key claims...",
  "Finalizing report...",
];

const FileUpload = () => {
  const [file, setFile] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [loadingMessage, setLoadingMessage] = useState("");
  const [error, setError] = useState(null);

  // Messages to cycle through while waiting for the AI
  // Cycle through messages every 5 seconds while loading is true
  useEffect(() => {
    let interval;
    if (loading) {
      let messageIndex = 0;
      setLoadingMessage(statusMessages[0]);
      interval = setInterval(() => {
        messageIndex++;
        if (messageIndex < statusMessages.length) {
          setLoadingMessage(statusMessages[messageIndex]);
        }
      }, 5000); // Change message every 5 seconds
    }
    return () => clearInterval(interval);
  }, [loading]);

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];

    // Frontend File Size Validation (5MB Limit)
    if (selectedFile && selectedFile.size > 5 * 1024 * 1024) {
      setError("File is too large. Please select a PDF under 5MB.");
      setFile(null);
      e.target.value = null; // Clear the input
      return;
    }

    setFile(selectedFile);
    setError(null);
  };

  const handleUpload = async () => {
    if (!file) return setError("Please select a valid file first.");

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const data = await uploadDocument(file);
      setResult(data);
    } catch (err) {
      setError(err);
    } finally {
      setLoading(false);
      setLoadingMessage("");
    }
  };

  return (
    <div style={{ padding: "20px", maxWidth: "800px", margin: "0 auto" }}>
      {/* Polished Upload UI Box */}
      <div
        style={{
          marginBottom: "20px",
          padding: "30px",
          border: "2px dashed #007bff",
          borderRadius: "12px",
          backgroundColor: "#f8fafd",
          textAlign: "center",
          transition: "all 0.3s",
        }}
      >
        <h2 style={{ marginTop: 0, color: "#333" }}>AI Document Evaluator</h2>
        <p style={{ color: "#666", marginBottom: "20px" }}>
          Upload a PDF report (Max 5MB) to generate a brief, check authenticity,
          and verify claims.
        </p>

        <input
          type="file"
          accept=".pdf"
          onChange={handleFileChange}
          style={{ marginBottom: "15px" }}
        />
        <br />
        <button
          onClick={handleUpload}
          disabled={loading || !file}
          style={{
            padding: "10px 24px",
            fontSize: "16px",
            cursor: loading || !file ? "not-allowed" : "pointer",
            backgroundColor: loading || !file ? "#ccc" : "#007bff",
            color: "white",
            border: "none",
            borderRadius: "6px",
            fontWeight: "bold",
            transition: "background-color 0.2s",
          }}
        >
          {loading ? "Evaluating..." : "Upload & Evaluate"}
        </button>

        {/* Dynamic Loading Text */}
        {loading && (
          <div
            style={{
              marginTop: "15px",
              color: "#007bff",
              fontWeight: "bold",
              animation: "pulse 1.5s infinite",
            }}
          >
            ⏳ {loadingMessage}
          </div>
        )}

        {/* Error Display */}
        {error && (
          <div
            style={{
              marginTop: "15px",
              padding: "10px",
              backgroundColor: "#ffebee",
              color: "#c62828",
              borderRadius: "4px",
              border: "1px solid #ef9a9a",
            }}
          >
            ❌ {error}
          </div>
        )}
      </div>

      {/* Main Results Container (Remains unchanged) */}
      {result && (
        <div
          style={{
            textAlign: "left",
            display: "flex",
            flexDirection: "column",
            gap: "20px",
            animation: "fadeIn 0.5s ease-in",
          }}
        >
          {result.authenticity && (
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
                Authenticity Report
              </h3>
              <MetricsGauge
                label="AI Generation Probability"
                percentage={result.authenticity.ai_probability_percent}
                isDanger={true}
              />
              <MetricsGauge
                label="Plagiarism Detected"
                percentage={result.authenticity.plagiarism_percent}
                isDanger={true}
              />
            </div>
          )}

          {result.verification && <FactChecker claims={result.verification} />}

          {result.evaluation && (
            <>
              <SummaryCard evaluation={result.evaluation} />

              {/* <div
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
                  Process Flowchart
                </h3>
                <Flowchart
                  chartCode={
                    result.evaluation.mermaid_flowchart || fallbackChartCode
                  }
                />
              </div> */}
            </>
          )}
        </div>
      )}

      {/* Quick inline style for the pulse/fade animations */}
      <style>{`
                @keyframes pulse { 0% { opacity: 1; } 50% { opacity: 0.5; } 100% { opacity: 1; } }
                @keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
            `}</style>
    </div>
  );
};

export default FileUpload;
