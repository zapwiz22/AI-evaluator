# import google.genai as genai
# import json
# import os
# from utils.config import get_gemini_api_key

# # A fallback function to ensure the app doesn't crash if the LLM fails.
# # It returns a valid, but minimal, JSON structure.
# def _safe_fallback(text: str) -> dict:
#     return {
#         "summary": "No summary available.",
#         "key_findings": [],
#         "table_data": {
#             "columns": ["Note", "Value"],
#             "rows": [["LLM", "No findings returned"]]
#         },
#         "mermaid_flowchart": "",
#         "requires_verification": []
#     }

# def evaluate_document_with_ai(text: str) -> dict:
#     """Sends extracted text to an LLM to get summary, table, and flowchart data."""
#     api_key = get_gemini_api_key()
#     if not api_key:
#         print("Error: No API key found in config.")
#         return _safe_fallback(text)

#     genai.configure(api_key=api_key)
#     model = _build_model()
    
#     prompt = f"""
#     You are an expert AI Evaluator. Analyze the following document text.
#     Extract the key information and return it strictly as a JSON object with the following schema:
#     {{
#         "summary": "A concise, 3-4 sentence brief of the entire document.",
#         "key_findings": ["Finding 1", "Finding 2", "Finding 3"],
#         "table_data": {{
#             "columns": ["Column Name 1", "Column Name 2", "Column Name 3"],
#             "rows": [["cell1", "cell2", "cell3"], ["cell1", "cell2", "cell3"]]
#         }},
#         "mermaid_flowchart": "A valid Mermaid.js graph TD string representing the core process or logic flow found in the text. Do not include markdown formatting blocks (like ```mermaid), just the raw code.",
#         "requires_verification": ["A testable claim from the text", "Another testable claim"]
#     }}
    
#     Document Text:
#     {text[:15000]}
#     """
    
#     try:
#         response = model.generate_content(prompt)
#         raw_text = response.text
        
#         # FIX: Clean the response text in case Gemini wraps it in markdown code blocks
#         if raw_text.startswith("```json"):
#             raw_text = raw_text.replace("```json\n", "").replace("```", "").strip()
#         elif raw_text.startswith("```"):
#             raw_text = raw_text.replace("```\n", "").replace("```", "").strip()

#         result_dict = json.loads(raw_text)

#         if "table_data" not in result_dict:
#             result_dict["table_data"] = {
#                 "columns": ["Note", "Value"],
#                 "rows": [["LLM", "No table_data returned"]]
#             }
#         return result_dict
        
#     except Exception as e:
#         # This will print the exact reason it failed to your backend terminal!
#         print(f"\n--- LLM Processing Error ---")
#         print(f"Error Details: {str(e)}")
#         print(f"----------------------------\n")
#         return _safe_fallback(text)

# def _build_model() -> genai.GenerativeModel:
#     # Use gemini-1.5-flash. It is highly stable, incredibly fast, 
#     # and has native support for JSON generation and large contexts.
#     return genai.GenerativeModel(
#         "gemini-1.5-flash",
#         generation_config={"response_mime_type": "application/json"},
#     )


import json
import os
import re
import base64
from io import BytesIO
import google.genai as genai
from google.genai import types
from utils.config import get_gemini_api_key

try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
except Exception:
    plt = None


MODEL_CANDIDATES = [
    "gemini-2.5-flash",
    "gemini-2.0-flash",
    "gemini-2.0-flash-lite",
]


def _to_float(value: str) -> float:
    try:
        return float(str(value).replace(",", "").strip())
    except Exception:
        return 0.0


def _clamp(value: float, low: float = 0.0, high: float = 100.0) -> float:
    return max(low, min(high, value))


def _extract_report_metrics(text: str, result_dict: dict) -> dict:
    corpus = " ".join([
        text or "",
        result_dict.get("summary", ""),
        " ".join(result_dict.get("key_findings") or []),
    ])

    dataset_matches = re.findall(r"(\d+(?:\.\d+)?)\s+(?:datasets?|benchmarks?)", corpus, flags=re.IGNORECASE)
    sample_matches = re.findall(r"(\d{1,3}(?:,\d{3})+|\d+)\s+(?:samples?|records?|rows?|images?|instances?)", corpus, flags=re.IGNORECASE)
    metric_matches = re.findall(
        r"(?:accuracy|f1|precision|recall|auc|mcc|bleu|rouge)[^\d%]{0,25}(\d+(?:\.\d+)?)\s*%",
        corpus,
        flags=re.IGNORECASE,
    )

    dataset_count = int(_to_float(max(dataset_matches, default="0")))
    sample_count = int(_to_float(max(sample_matches, default="0")))
    best_metric_percent = _clamp(max([_to_float(m) for m in metric_matches], default=0.0))

    has_train_val_test = bool(re.search(r"train(?:ing)?\s*/\s*val(?:idation)?\s*/\s*test", corpus, flags=re.IGNORECASE))
    has_baseline = bool(re.search(r"baseline|comparison", corpus, flags=re.IGNORECASE))
    has_variance = bool(re.search(r"std(?:\.|\s*dev)?|confidence interval|\+/-", corpus, flags=re.IGNORECASE))

    return {
        "dataset_count": dataset_count,
        "sample_count": sample_count,
        "best_metric_percent": best_metric_percent,
        "has_train_val_test": has_train_val_test,
        "has_baseline": has_baseline,
        "has_variance": has_variance,
    }


def _build_report_assessment(text: str, result_dict: dict) -> dict:
    metrics = _extract_report_metrics(text, result_dict)

    dataset_score = _clamp((metrics["dataset_count"] / 10.0) * 100.0)
    sample_score = _clamp((metrics["sample_count"] / 10000.0) * 100.0)
    performance_score = metrics["best_metric_percent"]

    reproducibility_score = 0.0
    reproducibility_score += 40.0 if metrics["has_train_val_test"] else 0.0
    reproducibility_score += 30.0 if metrics["has_baseline"] else 0.0
    reproducibility_score += 30.0 if metrics["has_variance"] else 0.0

    overall_score = round((dataset_score + sample_score + performance_score + reproducibility_score) / 4.0, 1)

    strengths = []
    weaknesses = []

    if metrics["dataset_count"] >= 3:
        strengths.append(f"Covers {metrics['dataset_count']} datasets/benchmarks, which improves generalization confidence.")
    else:
        weaknesses.append("Limited dataset coverage detected; evaluate on at least 3 datasets/benchmarks.")

    if metrics["sample_count"] >= 5000:
        strengths.append(f"Large evaluation volume ({metrics['sample_count']} samples/records) suggests stable estimates.")
    elif metrics["sample_count"] > 0:
        weaknesses.append(f"Only about {metrics['sample_count']} samples/records detected; larger test sets would improve reliability.")
    else:
        weaknesses.append("No clear sample/record count detected in the report.")

    if metrics["best_metric_percent"] >= 80:
        strengths.append(f"Strong headline performance detected (best metric around {metrics['best_metric_percent']:.1f}%).")
    elif metrics["best_metric_percent"] > 0:
        weaknesses.append(f"Moderate model performance detected (best metric around {metrics['best_metric_percent']:.1f}%).")
    else:
        weaknesses.append("No explicit percentage-based model metric (accuracy/F1/precision/recall) was detected.")

    if metrics["has_train_val_test"]:
        strengths.append("Report references train/validation/test split structure.")
    else:
        weaknesses.append("Missing explicit train/validation/test split details.")

    if metrics["has_baseline"]:
        strengths.append("Includes baseline or comparative evaluation language.")
    else:
        weaknesses.append("No clear baseline/comparison section detected.")

    visual_metrics = [
        {"label": "Dataset Coverage", "value": round(dataset_score, 1)},
        {"label": "Sample Size", "value": round(sample_score, 1)},
        {"label": "Performance", "value": round(performance_score, 1)},
        {"label": "Reproducibility", "value": round(reproducibility_score, 1)},
    ]

    plot_image = _build_metrics_plot_image(visual_metrics, overall_score)

    return {
        "overall_score": overall_score,
        "metrics": {
            "dataset_count": metrics["dataset_count"],
            "sample_count": metrics["sample_count"],
            "best_metric_percent": round(metrics["best_metric_percent"], 1),
        },
        "strengths": strengths,
        "weaknesses": weaknesses,
        "visual_metrics": visual_metrics,
        "plot_image_base64": plot_image,
    }


def _build_metrics_plot_image(visual_metrics: list[dict], overall_score: float) -> str:
    if plt is None or not visual_metrics:
        return ""

    labels = [item.get("label", "Metric") for item in visual_metrics]
    values = [float(item.get("value", 0.0)) for item in visual_metrics]

    fig, ax = plt.subplots(figsize=(8, 4.2), dpi=120)
    bars = ax.bar(labels, values, color=["#38bdf8", "#22c55e", "#f59e0b", "#a78bfa"])

    ax.set_ylim(0, 100)
    ax.set_ylabel("Score (%)")
    ax.set_title(f"Report Quality Metrics (Overall: {overall_score:.1f}/100)")
    ax.grid(axis="y", linestyle="--", alpha=0.25)

    for bar, value in zip(bars, values):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 1.5,
            f"{value:.1f}%",
            ha="center",
            va="bottom",
            fontsize=9,
        )

    fig.tight_layout()

    buffer = BytesIO()
    fig.savefig(buffer, format="png")
    plt.close(fig)
    buffer.seek(0)

    encoded = base64.b64encode(buffer.read()).decode("ascii")
    return f"data:image/png;base64,{encoded}"

# A fallback function to ensure the app doesn't crash if the LLM fails.
# It returns a valid, but minimal, JSON structure.
def _safe_fallback(text: str) -> dict:
    fallback_payload = {
        "summary": "No summary available.",
        "key_findings": [],
        "table_data": {
            "columns": ["Note", "Value"],
            "rows": [["LLM", "No findings returned"]]
        },
        "mermaid_flowchart": "",
        "requires_verification": []
    }
    fallback_payload["report_assessment"] = _build_report_assessment(text, fallback_payload)
    fallback_payload["mermaid_flowchart"] = _build_safe_flowchart(fallback_payload)
    return fallback_payload


def _clean_flowchart_label(value: str) -> str:
    label = re.sub(r"\s+", " ", str(value or "")).strip()
    label = label.replace('"', "'")
    label = label.replace("[", "(").replace("]", ")")
    label = label.replace("{", "(").replace("}", ")")
    label = label.replace("<", "(").replace(">", ")")
    return label[:90] or "Step"


def _build_safe_flowchart(result_dict: dict) -> str:
    summary = _clean_flowchart_label(result_dict.get("summary", "Document Analysis"))
    findings = [
        _clean_flowchart_label(finding)
        for finding in (result_dict.get("key_findings") or [])
        if str(finding).strip()
    ][:4]

    nodes = [
        ("N1", "Document Uploaded"),
        ("N2", "Text Extracted"),
        ("N3", "AI Analysis"),
        ("N4", summary),
    ]

    for index, finding in enumerate(findings, start=5):
        nodes.append((f"N{index}", finding))

    nodes.append((f"N{len(nodes) + 1}", "Review Complete"))

    lines = ["graph TD"]
    for left, right in zip(nodes, nodes[1:]):
        lines.append(f'    {left[0]}["{left[1]}"] --> {right[0]}["{right[1]}"]')
    return "\n".join(lines)


def _normalize_flowchart(raw_flowchart: str, result_dict: dict) -> str:
    chart = (raw_flowchart or "").strip()
    chart = re.sub(r"^```(?:mermaid|json)?\s*", "", chart, flags=re.IGNORECASE)
    chart = re.sub(r"\s*```$", "", chart).strip()

    if not chart:
        return _build_safe_flowchart(result_dict)

    if chart.lower().startswith("graph ") and "-->" in chart:
        return chart

    return _build_safe_flowchart(result_dict)

def evaluate_document_with_ai(text: str) -> dict:
    """Sends extracted text to an LLM to get summary, table, and flowchart data."""
    api_key = get_gemini_api_key()
    if not api_key:
        print("Error: No API key found in config.")
        return _safe_fallback(text)

    # Initialize the new Client architecture
    client = genai.Client(api_key=api_key)
    
    prompt = f"""
    You are an expert AI Evaluator. Analyze the following document text.
    Extract the key information and return it strictly as a JSON object with the following schema:
    {{
        "summary": "A concise, 3-4 sentence brief of the entire document.",
        "key_findings": ["Finding 1", "Finding 2", "Finding 3"],
        "table_data": {{
            "columns": ["Column Name 1", "Column Name 2", "Column Name 3"],
            "rows": [["cell1", "cell2", "cell3"], ["cell1", "cell2", "cell3"]]
        }},
        "mermaid_flowchart": "A valid Mermaid.js graph TD string representing the core process or logic flow found in the text. Do not include markdown formatting blocks (like ```mermaid), just the raw code.",
        "requires_verification": ["A testable claim from the text", "Another testable claim"]
    }}
    
    Document Text:
    {text[:15000]}
    """
    
    try:
        response = None
        for model_name in MODEL_CANDIDATES:
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                    ),
                )
                break
            except Exception:
                continue

        if response is None:
            raise RuntimeError("No supported Gemini model responded successfully.")
        
        raw_text = response.text
        
        # FIX: Clean the response text in case Gemini wraps it in markdown code blocks
        if raw_text.startswith("```json"):
            raw_text = raw_text.replace("```json\n", "").replace("```", "").strip()
        elif raw_text.startswith("```"):
            raw_text = raw_text.replace("```\n", "").replace("```", "").strip()

        result_dict = json.loads(raw_text)

        if "table_data" not in result_dict:
            result_dict["table_data"] = {
                "columns": ["Note", "Value"],
                "rows": [["LLM", "No table_data returned"]]
            }

        result_dict["mermaid_flowchart"] = _normalize_flowchart(
            result_dict.get("mermaid_flowchart", ""),
            result_dict,
        )

        result_dict["report_assessment"] = _build_report_assessment(text, result_dict)
        return result_dict
        
    except Exception as e:
        # This will print the exact reason it failed to your backend terminal!
        print(f"\n--- LLM Processing Error ---")
        print(f"Error Details: {str(e)}")
        print(f"----------------------------\n")
        return _safe_fallback(text)