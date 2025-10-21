#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LLM-based Report Accuracy Evaluator

Overview
--------
This script evaluates the factual accuracy of a generated report against a ground-truth report.
Both reports are markdown files. The evaluation has two stages that *both* use an LLM:

1) Extraction: For each document (generated and ground-truth), the LLM extracts the content
   for every required subsection into a strict JSON schema.
2) Judging: For each subsection, the LLM compares the "submitted answer" (generated) to the
   "ground truth" and returns a score in [0, 1], a categorical verdict, and a brief rationale.

Supported LLM providers
-----------------------
- OpenAI (API)       : set OPENAI_API_KEY and choose provider="openai"
- Ollama (local)     : ensure `ollama` is running; choose provider="ollama"

Usage
-----
python llm_report_evaluator.py \
  --groundtruth /path/to/groundtruth.md \
  --generated   /path/to/generated.md \
  --provider openai --model "gpt-4o-mini" \
  --out-json /path/to/eval_result.json \
  --out-md   /path/to/eval_result.md

Or with Ollama:
python llm_report_evaluator.py \
  --groundtruth /path/to/groundtruth.md \
  --generated   /path/to/generated.md \
  --provider ollama --model "qwen2.5:32b-instruct"

Notes
-----
- The extraction prompt is "schema-first": the model *must* return valid JSON for each subsection.
- The judge prompt instructs the model to do careful numeric and textual comparisons, handle
  rounding tolerance for numbers, and to be strict about units and sign.
- You can tune tolerance and scoring policy in `JUDGE_POLICY` below.

Author: ChatGPT
License: MIT
"""
from __future__ import annotations

import os
import json
import math
import time
import argparse
from dataclasses import dataclass, asdict
from typing import Dict, Any, List, Optional, Tuple, Union
from dotenv import load_dotenv
load_dotenv()

# =============== CONFIGURATION ===============

DEFAULT_PROVIDER = "openai"
DEFAULT_MODEL    = "gpt-4o-mini"

# Rounding/numeric tolerance suggestions for the judge
JUDGE_POLICY = {
    "numeric_tolerance_relative": 0.01,   # 1% relative tolerance
    "numeric_tolerance_absolute": 1e-6,   # absolute tolerance for near-zero
    "case_insensitive_text": True,
    "whitespace_insensitive_text": True,
    "treat_empty_as_missing": True,
    "accept_synonyms_for_words": True,    # allows small wording changes for text answers
}

# ----------- Section schema based on user spec -----------
SECTION_SCHEMA = [
    {'id': '1.1.1', 'section': 'Basic Information - Company Name'},
    {'id': '1.1.2', 'section': 'Basic Information - Establishment Date'},
    {'id': '1.1.3', 'section': 'Basic Information - Headquarters Location (CIty and Country)'},
    {'id': '1.2.1', 'section': 'Core Competencies - Innovation Advantages'},
    {'id': '1.2.2', 'section': 'Core Competencies - Product Advantages'},
    {'id': '1.2.3', 'section': 'Core Competencies - Brand Recognition'},
    {'id': '1.2.4', 'section': 'Core Competencies - Reputation Ratings'},
    {'id': '1.3.1', 'section': 'Mission & Vision - Mission Statement'},
    {'id': '1.3.2', 'section': 'Mission & Vision - Vision Statement'},
    {'id': '1.3.3', 'section': 'Mission & Vision - Core Value'},
    {'id': '2.1.1', 'section': 'Income Statement - Revenue'},
    {'id': '2.1.2', 'section': 'Income Statement - Cost of Goods Sold (COGS)'},
    {'id': '2.1.3', 'section': 'Income Statement - Gross Profit'},
    {'id': '2.1.4', 'section': 'Income Statement - Operating Expenses'},
    {'id': '2.1.5', 'section': 'Income Statement - Operating Income'},
    {'id': '2.1.6', 'section': 'Income Statement - Net Income'},
    {'id': '2.1.7', 'section': 'Income Statement - Income before income taxes'},
    {'id': '2.1.8', 'section': 'Income Statement - Income tax expense (benefit)'},
    {'id': '2.2.1', 'section': 'Balance Sheet - Total Assets'},
    {'id': '2.2.2', 'section': 'Balance Sheet - Current Assets'},
    {'id': '2.2.3', 'section': 'Balance Sheet - Non-Current Assets'},
    {'id': '2.2.4', 'section': 'Balance Sheet - Total Liabilities'},
    {'id': '2.2.5', 'section': 'Balance Sheet - Current Liabilities'},
    {'id': '2.2.6', 'section': 'Balance Sheet - Non-Current Liabilities'},
    {'id': '2.2.7', 'section': 'Balance Sheet - Shareholders\' Equity'},
    {'id': '2.2.8', 'section': 'Balance Sheet - Retained Earnings'},
    {'id': '2.2.9', 'section': 'Balance Sheet - Total Equity and Liabilities'},
    {'id': '2.2.10', 'section': 'Balance Sheet - Inventories'},
    {'id': '2.2.11', 'section': 'Balance Sheet - Prepaid Expenses'},
    {'id': '2.3.1', 'section': 'Cash Flow Statement - Net Cash Flow from Operations'},
    {'id': '2.3.2', 'section': 'Cash Flow Statement - Net Cash Flow from Investing'},
    {'id': '2.3.3', 'section': 'Cash Flow Statement - Net Cash Flow from Financing'},
    {'id': '2.3.4', 'section': 'Cash Flow Statement - Net Increase/Decrease in Cash'},
    {'id': '2.3.5', 'section': 'Cash Flow Statement - Dividends'},
    {'id': '2.4.1', 'section': 'Key Financial Metrics - Gross Margin = (Revenue − COGS) ÷ Revenue'},
    {'id': '2.4.2', 'section': 'Key Financial Metrics - Operating Margin = Operating Income ÷ Revenue'},
    {'id': '2.4.3', 'section': 'Key Financial Metrics - Net Profit Margin = Net Income ÷ Revenue'},
    {'id': '2.4.4', 'section': 'Key Financial Metrics - Current Ratio = Current Assets ÷ Current Liabilities'},
    {'id': '2.4.5', 'section': 'Key Financial Metrics - Quick Ratio = (Current Assets − Inventories − Prepaid expenses) ÷ Current Liabilities'},
    {'id': '2.4.6', 'section': 'Key Financial Metrics - Interest Coverage = Operating Income ÷ Interest Expense'},
    {'id': '2.4.7', 'section': 'Key Financial Metrics - Asset Turnover = Revenue ÷ Average Total Assets'},
    {'id': '2.4.8', 'section': 'Key Financial Metrics - Debt-to-Equity = Total Liabilities ÷ Shareholders’ Equity'},
    {'id': '2.4.9', 'section': 'Key Financial Metrics - Return on Equity (RoE) = Net Income ÷ Average Shareholders’ Equity'},
    {'id': '2.4.10', 'section': 'Key Financial Metrics - Return on Assets (RoA) = Net Income ÷ Average Total Assets'},
    {'id': '2.4.11', 'section': 'Key Financial Metrics - Effective Tax Rate = Income tax expense (benefit) ÷ Income before income taxes'},
    {'id': '2.4.12', 'section': 'Key Financial Metrics - Dividend Payout Ratio = Dividends ÷ Net Income'},
    {'id': '2.5.1', 'section': 'Operating Performance - Revenue by Product/Service: What is the revenue breakdown by product/service?'},
    {'id': '2.5.2', 'section': 'Operating Performance - Revenue by Geographic Region: What is the revenue breakdown by geographic region?'},
    {'id': '3.1.1', 'section': 'Profitability Analysis  - Revenue & Direct-Cost Dynamics'},
    {'id': '3.1.2', 'section': 'Profitability Analysis  - Operating Efficiency'},
    {'id': '3.1.3', 'section': 'Profitability Analysis  - External & One-Off Impact'},
    {'id': '3.2.1', 'section': 'Financial Performance Summary - Comprehensive financial health'},
    {'id': '3.2.2', 'section': 'Financial Performance Summary - Profitabilitiy and earnings quality'},
    {'id': '3.2.3', 'section': 'Financial Performance Summary - Operational efficiency'},
    {'id': '3.2.4', 'section': 'Financial Performance Summary - Financial risk identification and early warning'},
    {'id': '3.2.5', 'section': 'Financial Performance Summary - Future financial performance projection'},
    {'id': '3.3.1', 'section': 'Business Competitiveness - Business Model: What is the company\'s primary business model (e.g., subscription, freemium, sales)?'},
    {'id': '3.3.2', 'section': 'Business Competitiveness - Market Position: What is the company\'s market share in each of its key markets? Is the company a leader, challenger, or niche player?'},
    {'id': '4.1.1', 'section': 'Risk Factors - Market Risks'},
    {'id': '4.1.2', 'section': 'Risk Factors - Operational Risks'},
    {'id': '4.1.3', 'section': 'Risk Factors - Financial Risks'},
    {'id': '4.1.4', 'section': 'Risk Factors - Compliance Risks'},
    {'id': '5.1.1', 'section': 'Board Composition - Name'},
    {'id': '5.1.2', 'section': 'Board Composition - Position'},
    {'id': '5.1.3', 'section': 'Board Composition - Total Income'},
    {'id': '5.2.1', 'section': 'Internal Controls - Risk assessment procedures'},
    {'id': '5.2.2', 'section': 'Internal Controls - Control activities'},
    {'id': '5.2.3', 'section': 'Internal Controls - Monitoring mechanisms'},
    {'id': '5.2.4', 'section': 'Internal Controls - Identified material weaknesses or deficiencies'},
    {'id': '5.2.5', 'section': 'Internal Controls - Improvements'},
    {'id': '5.2.6', 'section': 'Internal Controls - Effectiveness'},
    {'id': '6.1.1', 'section': 'Strategic Direction - Mergers and acquisitions (M&A) to expand market share'},
    {'id': '6.1.2', 'section': 'Strategic Direction - Acquire new technologies'},
    {'id': '6.1.3', 'section': 'Strategic Direction - Potential for organizational restructuring'},
    {'id': '6.2.1', 'section': 'Challenges and Uncertainties - Economic challenges such as inflation, recession risks, and shifting consumer behavior that could impact revenue and profitability.'},
    {'id': '6.2.2', 'section': 'Challenges and Uncertainties - Competitive pressures from both established industry players and new, disruptive market entrants that the company faces'},
    {'id': '6.3.1', 'section': 'Innovation and Development Plans - R&D investments, with a focus on advancing technology, improving products, and creating new solutions to cater to market trends'},
    {'id': '6.3.2', 'section': 'Innovation and Development Plans - New product launches, emphasizing the company’s commitment to continuously introducing differentiated products'},
]

# =============== LLM CLIENTS ===============

class LLMClient:
    """Simple pluggable client for OpenAI or Ollama."""
    def __init__(self, provider: str = DEFAULT_PROVIDER, model: str = DEFAULT_MODEL,
                 temperature: float = 0.0, timeout: int = 120):
        provider = provider.lower()
        if provider not in {"openai", "ollama"}:
            raise ValueError("provider must be 'openai' or 'ollama'")
        self.provider = provider
        self.model = model
        self.temperature = temperature
        self.timeout = timeout

        if provider == "openai":
            try:
                from openai import OpenAI  # type: ignore
            except Exception:
                raise RuntimeError("Please install openai>=1.0.0 and set OPEN_AI_API_KEY")
            self._client = OpenAI(api_key=os.environ["OPEN_AI_API_KEY"], timeout=timeout)
        else:  # ollama
            try:
                import requests  # type: ignore
            except Exception:
                raise RuntimeError("Please `pip install requests` for Ollama provider")
            self._session = requests.Session()
            self._base_url = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")

    def complete_json(self, system_prompt: str, user_prompt: str) -> str:
        """Return the raw text completion (expected to be JSON)."""
        if self.provider == "openai":
            # Using the new responses API or chat.completions depending on version
            # We'll try `chat.completions` for broad compatibility.
            from openai import OpenAI  # type: ignore
            # Reuse client created in __init__
            chat = self._client.chat.completions.create(
                model=self.model,
                temperature=self.temperature,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
            )
            return chat.choices[0].message.content or ""
        else:
            # Ollama: POST /api/chat with JSON body
            import requests  # type: ignore
            payload = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                "options": {"temperature": self.temperature},
                "stream": False,
            }
            r = self._session.post(f"{self._base_url}/api/chat", json=payload, timeout=self.timeout)
            r.raise_for_status()
            data = r.json()
            # Ollama returns the last message in "message"
            return data.get("message", {}).get("content", "")

# =============== PROMPTS ===============

EXTRACTION_SYSTEM = """You are a careful information extraction model.
You will read a markdown report and extract answers for the requested fields.
Return STRICT JSON (no prose) following the exact key names you are given.
If a value is missing or not stated, return null."""


EXTRACTION_USER_TMPL = """You are given a markdown report below.

--- BEGIN REPORT ---
{doc_text}
--- END REPORT ---

Extract answers for these fields, mapping each `id` to its `answer`.
Return EXACT JSON with this schema:
{{
  "items": [
    {{
      "id": "<use id from the list>",
      "section": "<copy the section text>",
      "answer": "<string or number or object; null if missing>"
    }},
    ...
  ]
}}

Fields to extract (id, section):
{fields_list}

Guidelines:
- Work section-agnostically: the report might not use the same headers. Search the entire document.
- Preserve units and currency symbols that appear alongside numbers.
- Make sure to extract all the content for the required section, whether it contains paragraphs, lists or table rows.
- For lists/tables (e.g., revenue by region, board composition), return a compact JSON-ish string, e.g.:
  "2024: $26,966M; 2023: $13,405M; 2022: $10,306M;"
- If multiple years exist, extract information for all available years.
- Return ONLY valid JSON. No markdown, no comments.
"""

JUDGE_SYSTEM = """You are a strict, detail-oriented fact-checking and grading model.
You will compare a submitted answer against the ground truth for a single field/section.

Scoring policy:
- Output a score in [0, 1]. 1 = fully correct, 0 = incorrect or missing.
- Consider numeric tolerance: relative {rel_tol:.4f}, absolute {abs_tol:.6f} near zero.
- Be strict about sign, order-of-magnitude, currency, and units.
- For text, allow minor paraphrases and synonyms if meaning is identical.
- If both are missing/empty, score=1. If only one is missing, score=0.
- For list-like answers (e.g., region breakdown), require the same key set and near-equal numeric values; partial overlap may earn partial credit.
Return STRICT JSON only.
"""

JUDGE_USER_TMPL = """Section: {section}

Submitted Answer:
{submitted}

Ground Truth:
{ground_truth}

Return EXACT JSON:
{{
  "score": <float 0..1>,
  "verdict": "<Correct | Partially Correct | Incorrect | Missing>",
  "reasoning": "<short, specific comparison reasoning>"
}}
"""


# =============== DATA MODELS ===============

@dataclass
class ExtractedItem:
    id: str
    section: str
    answer: Optional[str]

@dataclass
class Judgment:
    score: float
    verdict: str
    reasoning: str

# =============== CORE LOGIC ===============

def build_fields_list_for_prompt(schema: List[Dict[str, str]]) -> str:
    lines = []
    for item in schema:
        lines.append(f"- id: {item['id']} | section: {item['section']}")
    return "\n".join(lines)

def extract_answers(client: LLMClient, doc_text: str, schema: List[Dict[str,str]]) -> Dict[str, ExtractedItem]:
    """Ask LLM to extract answers for all fields. Returns dict by id -> ExtractedItem."""
    fields_list = build_fields_list_for_prompt(schema)
    user_prompt = EXTRACTION_USER_TMPL.format(doc_text=doc_text, fields_list=fields_list)
    raw = client.complete_json(EXTRACTION_SYSTEM, user_prompt).strip()

    # Best-effort JSON parsing with fallback
    def _safe_json_load(s: str) -> Dict[str, Any]:
        try:
            return json.loads(s)
        except Exception as e:
            # Attempt to salvage common trailing text or code fences
            s2 = s.strip().strip("```json").strip("```").strip()
            return json.loads(s2)

    data = _safe_json_load(raw)
    items = {}
    for rec in data.get("items", []):
        items[rec["id"]] = ExtractedItem(
            id=rec["id"],
            section=rec.get("section",""),
            answer=None if rec.get("answer") in (None, "", "N/A", "null") else str(rec.get("answer"))
        )
    return items

def judge_field(client: LLMClient, section: str, submitted: Optional[str], ground_truth: Optional[str]) -> Judgment:
    sys = JUDGE_SYSTEM.format(
        rel_tol=JUDGE_POLICY["numeric_tolerance_relative"],
        abs_tol=JUDGE_POLICY["numeric_tolerance_absolute"],
    )
    submitted_text = "null" if submitted is None else str(submitted)
    gt_text = "null" if ground_truth is None else str(ground_truth)

    user = JUDGE_USER_TMPL.format(section=section, submitted=submitted_text, ground_truth=gt_text)
    raw = client.complete_json(sys, user).strip()
    try:
        data = json.loads(raw)
    except Exception:
        s2 = raw.strip().strip("```json").strip("```").strip()
        data = json.loads(s2)

    score = float(data.get("score", 0.0))
    verdict = str(data.get("verdict", "Missing"))
    reasoning = str(data.get("reasoning", ""))
    return Judgment(score=score, verdict=verdict, reasoning=reasoning)

def evaluate_reports(
    client: LLMClient, groundtruth_text: str, generated_text: str, schema: List[Dict[str,str]]
) -> Dict[str, Any]:
    gt_items = extract_answers(client, groundtruth_text, schema)
    gen_items = extract_answers(client, generated_text, schema)

    results = []
    scores = []
    for item in schema:
        fid = item["id"]
        q   = item["section"]
        gt  = gt_items.get(fid)
        gen = gen_items.get(fid)

        gt_answer  = gt.answer if gt else None
        gen_answer = gen.answer if gen else None

        judgment = judge_field(client, q, gen_answer, gt_answer)
        scores.append(judgment.score)
        results.append({
            "id": fid,
            "section": q,
            "submitted_answer": gen_answer,
            "ground_truth": gt_answer,
            "score": round(judgment.score, 4),
            "verdict": judgment.verdict,
            "reasoning": judgment.reasoning,
        })

    overall = sum(scores)/len(scores) if scores else 0.0

    # Aggregate section scores (prefix before first underscore)
    section_bucket: Dict[str, List[float]] = {}
    for r in results:
        section_id = r["id"].split("_", 1)[0]  # e.g., "2.1.1" -> "2.1.1" (we want to group by the first two components, but ids are like "2.1.1_revenue")
        # Let's group by the first 3-number pattern (e.g., "2.1", "2.2", "2.3", "1.1", etc.)
        parts = section_id.split(".")
        section_key = ".".join(parts[:2]) if len(parts) >= 2 else section_id
        section_bucket.setdefault(section_key, []).append(r["score"])

    section_scores = {k: round(sum(v)/len(v), 4) for k, v in section_bucket.items()}

    return {
        "overall_score": round(overall, 4),
        "section_scores": section_scores,
        "items": results,
    }

def save_outputs(result: Dict[str, Any], out_json: str, out_md: str) -> None:
    os.makedirs(os.path.dirname(out_json), exist_ok=True)
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    # Pretty Markdown
    lines = []
    lines.append(f"# Evaluation Result")
    lines.append("")
    lines.append(f"- **Overall Score:** {result['overall_score']:.4f}")
    lines.append("")
    lines.append("## Section Scores")
    for k, v in sorted(result["section_scores"].items()):
        lines.append(f"- **{k}**: {v:.4f}")
    lines.append("")
    lines.append("## Itemized Judgments")
    lines.append("")
    lines.append("| ID | Section | Score | Verdict | Submitted | Ground Truth | Reasoning |")
    lines.append("|---|---|---:|---|---|---|---|")
    for r in result["items"]:
        sid = r["id"].replace("|", "\\|")
        q = r["section"].replace("|", "\\|")
        sub = (r["submitted_answer"] or "—").replace("|", "\\|")
        gt = (r["ground_truth"] or "—").replace("|", "\\|")
        reason = r["reasoning"].replace("|", "\\|")
        lines.append(f"| {sid} | {q} | {r['score']:.4f} | {r['verdict']} | {sub} | {gt} | {reason} |")

    os.makedirs(os.path.dirname(out_md), exist_ok=True)
    with open(out_md, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

# =============== CLI ===============

def main():
    parser = argparse.ArgumentParser(description="LLM-based report accuracy evaluator")
    parser.add_argument("--groundtruth", type=str, required=False, default="/mnt/data/NVIDIA_groundtruth.md")
    parser.add_argument("--generated",   type=str, required=False, default="/mnt/data/NVIDIA_generated.md")
    parser.add_argument("--provider",    type=str, default=DEFAULT_PROVIDER, choices=["openai", "ollama"])
    parser.add_argument("--model",       type=str, default=DEFAULT_MODEL)
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--timeout",     type=int, default=120)
    parser.add_argument("--out-json",    type=str, default="/mnt/data/eval_result.json")
    parser.add_argument("--out-md",      type=str, default="/mnt/data/eval_result.md")
    args = parser.parse_args()

    with open(args.groundtruth, "r", encoding="utf-8") as f:
        gt_text = f.read()
    with open(args.generated, "r", encoding="utf-8") as f:
        gen_text = f.read()

    client = LLMClient(provider=args.provider, model=args.model, temperature=args.temperature, timeout=args.timeout)
    result = evaluate_reports(client, gt_text, gen_text, SECTION_SCHEMA)
    save_outputs(result, args.out_json, args.out_md)
    print(json.dumps({"status":"ok","overall_score": result["overall_score"], "out_json": args.out_json, "out_md": args.out_md}, indent=2))

if __name__ == "__main__":
    main()
