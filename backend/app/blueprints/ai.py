"""
AI Blueprint — Gemini AI-powered Doubt Solver & Solution Explainer for Question Papers.
Uses Google Gemini API to explain past-year questions, provide step-by-step solutions,
explain official marking scheme criteria, and link back to curriculum textbooks.
"""
import os
import json
import urllib.request
import urllib.error
from flask import Blueprint, jsonify, request, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..db import get_db

ai_bp = Blueprint("ai", __name__)

DEFAULT_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")
FALLBACK_MODELS = ["gemini-3.5-flash-lite", "gemini-3.1-flash-lite", "gemini-flash-lite-latest"]


def _call_gemini(system_prompt: str, user_message: str, api_key: str) -> dict:
    """Invoke Gemini REST API with fallback models."""
    models_to_try = [DEFAULT_MODEL] + [m for m in FALLBACK_MODELS if m != DEFAULT_MODEL]
    last_error = None

    for model in models_to_try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
        payload = {
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": f"{system_prompt}\n\nStudent Doubt / Question:\n{user_message}"}]
                }
            ],
            "generationConfig": {
                "temperature": 0.3,
                "topP": 0.95,
                "maxOutputTokens": 2048,
            }
        }
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        try:
            with urllib.request.urlopen(req, timeout=20) as resp:
                result = json.loads(resp.read().decode("utf-8"))
                candidates = result.get("candidates", [])
                if candidates and "content" in candidates[0]:
                    parts = candidates[0]["content"].get("parts", [])
                    if parts and "text" in parts[0]:
                        return {
                            "text": parts[0]["text"],
                            "model": model,
                            "finish_reason": candidates[0].get("finishReason")
                        }
        except urllib.error.HTTPError as e:
            err_body = e.read().decode("utf-8", errors="ignore")
            last_error = f"HTTP {e.code}: {err_body[:180]}"
        except Exception as e:
            last_error = str(e)

    raise RuntimeError(f"All Gemini models failed. Last error: {last_error}")


@ai_bp.route("/explain", methods=["POST"])
def explain_question():
    """
    POST /ai/explain
    Body:
    {
        "paper_id": 126,
        "question_text": "...",
        "user_query": "Explain step-by-step with formulas and common pitfalls",
        "mode": "step_by_step" | "hint" | "marking_scheme" | "textbook_ref"
    }
    """
    data = request.get_json(silent=True) or {}
    paper_id = data.get("paper_id")
    question_text = (data.get("question_text") or "").strip()
    user_query = (data.get("user_query") or "").strip()
    mode = data.get("mode", "step_by_step")

    if not user_query and not question_text:
        return jsonify({"error": "Either question_text or user_query is required"}), 400

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return jsonify({"error": "GEMINI_API_KEY is not configured in backend .env"}), 500

    paper_meta = {}
    textbooks = []
    if paper_id:
        conn = get_db()
        with conn.cursor() as cur:
            cur.execute("""
                SELECT p.id, p.title, p.year, p.paper_type, p.has_answer_key,
                       e.name AS exam_name, e.slug AS exam_slug,
                       ec.name AS category_name
                FROM papers p
                JOIN exam_categories ec ON p.exam_category_id = ec.id
                JOIN exams e ON ec.exam_id = e.id
                WHERE p.id = %s
            """, (paper_id,))
            paper_meta = cur.fetchone() or {}

            # Fetch linked textbooks
            cur.execute("""
                SELECT tb.title, tb.board, tb.standard_level
                FROM textbooks tb
                JOIN paper_subjects ps ON tb.subject_id = ps.subject_id
                WHERE ps.paper_id = %s
                LIMIT 3
            """, (paper_id,))
            textbooks = cur.fetchall()

    exam_context = ""
    if paper_meta:
        exam_context = f"""
Current Document Context:
- Paper Title: {paper_meta.get('title')}
- Examination: {paper_meta.get('exam_name')} ({paper_meta.get('category_name')})
- Year: {paper_meta.get('year')}
- Paper Classification: {'Official Genuine Exam Paper' if paper_meta.get('paper_type') == 'original' else 'Official Sample Question Paper (SQP)'}
- Official Answer Key Attached: {'Yes' if paper_meta.get('has_answer_key') else 'No'}
"""
    if textbooks:
        tb_names = ", ".join([f"{tb['title']} ({tb['board']})" for tb in textbooks])
        exam_context += f"- Prescribed Curriculum Textbooks: {tb_names}\n"

    mode_instructions = {
        "step_by_step": (
            "Provide a comprehensive, pedagogical, step-by-step solution. "
            "Include: (1) Core concepts & underlying laws/theorems, (2) Step-by-step derivation or calculation with clean LaTeX math equations, "
            "(3) Common student misconceptions & traps to avoid, (4) Direct reference to relevant NCERT / board textbook chapter."
        ),
        "hint": (
            "Do NOT give away the final answer or full derivation! Provide an intuitive Socratic hint that guides the student "
            "to deduce the next step themselves, noting the governing equation or concept to recall."
        ),
        "marking_scheme": (
            "Break down how examiners evaluate this question according to official CBSE / NTA / UPSC marking schemes. "
            "Show point-by-point step mark allocation (e.g., formula 1/2 mark, substitution 1/2 mark, diagram 1 mark, final answer with units 1 mark)."
        ),
        "textbook_ref": (
            "Identify the exact NCERT / State Board textbook chapter, section, and standard learning outcomes tested by this question."
        )
    }

    selected_mode_instruction = mode_instructions.get(mode, mode_instructions["step_by_step"])

    system_prompt = f"""You are the ExamVault AI Master Tutor & Doubt Solver, an apex academic expert specializing in Indian national and state examinations (CBSE 10th & 12th, ICSE/ISC, JEE Main & Advanced, NEET UG, UPSC Civil Services, and TNPSC).

Your goals:
1. Deliver rigorously accurate, crystal-clear, pedagogically sound answers.
2. Format all mathematical and chemical equations using KaTeX / LaTeX ($...$ for inline, $$...$$ for display).
3. Structure your response with bold headers, bullet points, and numbered steps.
4. {selected_mode_instruction}
{exam_context}
"""

    combined_user_message = ""
    if question_text:
        combined_user_message += f"Question to Solve:\n\"\"\"\n{question_text}\n\"\"\"\n\n"
    if user_query:
        combined_user_message += f"Student Instruction / Question:\n{user_query}"
    else:
        combined_user_message += "Please provide the official step-by-step solution and explanation for this question."

    try:
        gemini_result = _call_gemini(system_prompt, combined_user_message, api_key)
        return jsonify({
            "solution": gemini_result["text"],
            "model_used": gemini_result["model"],
            "mode": mode,
            "paper_id": paper_id
        }), 200
    except Exception as e:
        return jsonify({"error": f"AI explanation failed: {str(e)}"}), 502
