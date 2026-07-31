#!/usr/bin/env python3
"""Build and locally serve a self-contained Boxing Me decision page."""

from __future__ import annotations

import argparse
import html
import json
import os
import re
import tempfile
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

MAX_BODY = 1_000_000

UI_TEXT = {
    "en": {
        "decision_brief": "Decision brief", "apply": "Apply recommendations", "clear": "Clear answers",
        "review": "Review", "direction": "Your direction", "overall_label": "Anything the agent should change, avoid, or know?",
        "overall_placeholder": "Optional overall feedback", "save": "Save decisions", "copy": "Copy agent brief",
        "download": "Download JSON", "privacy": "Answers stay in this browser until you save, copy, or download them.",
        "recommended": "Recommended", "why_this": "Why this:", "decision": "DECISION", "required": "Required",
        "write_answer": "Write your answer", "other": "Other or a variation", "other_placeholder": "Describe what you want instead",
        "notes": "Notes for this decision", "notes_placeholder": "Optional detail", "choose_answer": "Choose or write an answer.",
        "choose_min": "Choose at least %n%.", "choose_max": "Choose no more than %n%.", "brief_title": "Decision brief:",
        "unanswered": "Unanswered", "other_brief": "Other:", "notes_brief": "Notes:", "overall_brief": "Overall notes:",
        "count": "%done% of %total% answered", "not_answered": "Not answered", "clear_confirm": "Clear every answer and note on this page?",
        "cleared": "Answers cleared.", "copied": "Agent brief copied.", "copy_blocked": "Copy was blocked. Use Download JSON instead.",
        "downloaded": "Response downloaded.", "complete_required": "Complete the highlighted required decisions.",
        "saved": "Saved. Tell the agent you are done.", "save_fallback": "No local save server found. Your JSON was downloaded instead.",
        "add_question": "Add question", "edit": "Edit", "delete": "Delete", "custom": "YOUR QUESTION",
        "builder_title": "Build a decision", "prompt_label": "Question", "why_label": "Why it matters",
        "type_label": "Answer type", "single_type": "Choose one", "multi_type": "Choose several", "text_type": "Written answer",
        "required_label": "Required", "allow_other_label": "Allow another answer", "minimum_label": "Minimum choices",
        "maximum_label": "Maximum choices", "options_label": "Choices", "add_option": "Add choice",
        "option_label": "Choice label", "details_label": "Tradeoffs and details", "recommend_label": "Recommend", "no_recommendation": "No recommendation",
        "reason_label": "Why recommend it?", "create_question": "Add to page", "update_question": "Update question",
        "cancel": "Cancel", "builder_invalid": "Complete the highlighted question fields.",
        "delete_confirm": "Delete this question and its answer?", "question_added": "Question added.",
        "question_updated": "Question updated.", "question_deleted": "Question deleted."
    },
    "th": {
        "decision_brief": "แบบสรุปการตัดสินใจ", "apply": "ใช้ตัวเลือกที่แนะนำ", "clear": "ล้างคำตอบ",
        "review": "ตรวจทาน", "direction": "ทิศทางที่คุณเลือก", "overall_label": "มีอะไรที่ Agent ควรแก้ หลีกเลี่ยง หรือควรรู้เพิ่มเติมไหม?",
        "overall_placeholder": "ความคิดเห็นเพิ่มเติม (ไม่บังคับ)", "save": "บันทึกคำตอบ", "copy": "คัดลอกสรุปให้ Agent",
        "download": "ดาวน์โหลด JSON", "privacy": "คำตอบจะอยู่ในเบราว์เซอร์นี้จนกว่าคุณจะบันทึก คัดลอก หรือดาวน์โหลด",
        "recommended": "แนะนำ", "why_this": "เหตุผลที่แนะนำ:", "decision": "คำถาม", "required": "จำเป็น",
        "write_answer": "พิมพ์คำตอบของคุณ", "other": "ตัวเลือกอื่นหรือปรับรายละเอียด", "other_placeholder": "อธิบายสิ่งที่คุณต้องการแทน",
        "notes": "หมายเหตุสำหรับข้อนี้", "notes_placeholder": "รายละเอียดเพิ่มเติม (ไม่บังคับ)", "choose_answer": "กรุณาเลือกหรือพิมพ์คำตอบ",
        "choose_min": "กรุณาเลือกอย่างน้อย %n% ตัวเลือก", "choose_max": "กรุณาเลือกไม่เกิน %n% ตัวเลือก", "brief_title": "สรุปการตัดสินใจ:",
        "unanswered": "ยังไม่ตอบ", "other_brief": "อื่น ๆ:", "notes_brief": "หมายเหตุ:", "overall_brief": "หมายเหตุรวม:",
        "count": "ตอบแล้ว %done% จาก %total% ข้อ", "not_answered": "ยังไม่ตอบ", "clear_confirm": "ล้างคำตอบและหมายเหตุทั้งหมดในหน้านี้หรือไม่?",
        "cleared": "ล้างคำตอบแล้ว", "copied": "คัดลอกสรุปสำหรับ Agent แล้ว", "copy_blocked": "เบราว์เซอร์ไม่อนุญาตให้คัดลอก กรุณาใช้ดาวน์โหลด JSON แทน",
        "downloaded": "ดาวน์โหลดคำตอบแล้ว", "complete_required": "กรุณาตอบคำถามที่จำเป็นให้ครบ",
        "saved": "บันทึกแล้ว กรุณาบอก Agent ว่าคุณทำเสร็จแล้ว", "save_fallback": "ไม่พบเซิร์ฟเวอร์สำหรับบันทึก จึงดาวน์โหลด JSON ให้แทน",
        "add_question": "เพิ่มคำถาม", "edit": "แก้ไข", "delete": "ลบ", "custom": "คำถามของคุณ",
        "builder_title": "สร้างคำถามตัดสินใจ", "prompt_label": "คำถาม", "why_label": "เหตุผลที่สำคัญ",
        "type_label": "รูปแบบคำตอบ", "single_type": "เลือกหนึ่งข้อ", "multi_type": "เลือกหลายข้อ", "text_type": "เขียนคำตอบ",
        "required_label": "จำเป็น", "allow_other_label": "อนุญาตคำตอบอื่น", "minimum_label": "จำนวนขั้นต่ำ",
        "maximum_label": "จำนวนสูงสุด", "options_label": "ตัวเลือก", "add_option": "เพิ่มตัวเลือก",
        "option_label": "ชื่อตัวเลือก", "details_label": "รายละเอียดและข้อแลกเปลี่ยน", "recommend_label": "แนะนำ", "no_recommendation": "ไม่แนะนำตัวเลือกใด",
        "reason_label": "เหตุผลที่แนะนำ", "create_question": "เพิ่มลงในหน้า", "update_question": "อัปเดตคำถาม",
        "cancel": "ยกเลิก", "builder_invalid": "กรุณากรอกช่องคำถามที่ไฮไลต์ให้ครบ",
        "delete_confirm": "ลบคำถามนี้พร้อมคำตอบหรือไม่?", "question_added": "เพิ่มคำถามแล้ว",
        "question_updated": "อัปเดตคำถามแล้ว", "question_deleted": "ลบคำถามแล้ว"
    },
}


def load_spec(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"Cannot read specification: {exc}") from exc
    spec = normalize_spec(value)
    validate_spec(spec)
    return spec


TYPE_ALIASES = {"s": "single", "m": "multi", "x": "text"}


def normalize_spec(value: Any) -> Any:
    """Expand the compact authoring shape while leaving legacy specs intact."""
    if not isinstance(value, dict) or "questions" in value or "q" not in value:
        return value

    def expand_option(option: Any) -> Any:
        if isinstance(option, dict):
            return option
        if not isinstance(option, list) or len(option) not in {3, 4}:
            return option
        expanded = {"id": option[0], "label": option[1], "details": option[2]}
        if len(option) == 4:
            expanded.update(recommended=True, recommendation_reason=option[3])
        return expanded

    def expand_question(question: Any) -> Any:
        if not isinstance(question, dict):
            return question
        expanded = {
            "id": question.get("i"),
            "prompt": question.get("p"),
            "why": question.get("w"),
            "type": TYPE_ALIASES.get(question.get("t"), question.get("t")),
        }
        aliases = {
            "r": "required", "a": "allow_other", "n": "min",
            "m": "max", "if": "when",
        }
        for short, long in aliases.items():
            if short in question:
                expanded[long] = question[short]
        if "o" in question:
            options = question["o"]
            expanded["options"] = [expand_option(option) for option in options] if isinstance(options, list) else options
        return expanded

    return {
        "id": value.get("i"),
        "locale": value.get("l", "en"),
        "title": value.get("t"),
        "context": value.get("c"),
        "questions": [expand_question(question) for question in value.get("q", [])]
        if isinstance(value.get("q"), list) else value.get("q"),
    }


def _validate_condition(condition: Any, earlier: dict[str, set[str]], prefix: str, errors: list[str]) -> None:
    if not isinstance(condition, list) or not condition:
        errors.append(f"{prefix} must be a condition array")
        return
    if len(condition) == 2 and all(isinstance(value, str) and value.strip() for value in condition):
        question_id, option_id = condition
        if question_id not in earlier:
            errors.append(f"{prefix} must reference an earlier choice question")
        elif option_id not in earlier[question_id]:
            errors.append(f"{prefix} references an unknown option")
        return
    operator = condition[0]
    if operator in {"all", "any"}:
        if len(condition) < 3:
            errors.append(f"{prefix} {operator} requires at least two conditions")
            return
        for index, child in enumerate(condition[1:]):
            _validate_condition(child, earlier, f"{prefix}[{index + 1}]", errors)
        return
    if operator == "not":
        if len(condition) != 2:
            errors.append(f"{prefix} not requires exactly one condition")
            return
        _validate_condition(condition[1], earlier, f"{prefix}[1]", errors)
        return
    errors.append(f"{prefix} leaf must be [question-id, option-id]")


def validate_spec(spec: Any) -> None:
    errors: list[str] = []
    if not isinstance(spec, dict):
        raise ValueError("Specification must be a JSON object")
    for field in ("id", "title", "context"):
        if not isinstance(spec.get(field), str) or not spec[field].strip():
            errors.append(f"{field} must be a non-empty string")
    if spec.get("locale", "en") not in UI_TEXT:
        errors.append("locale must be en or th")
    questions = spec.get("questions")
    if not isinstance(questions, list) or not questions:
        errors.append("questions must be a non-empty array")
        questions = []
    seen_questions: set[str] = set()
    earlier_choice_options: dict[str, set[str]] = {}
    for index, question in enumerate(questions):
        prefix = f"questions[{index}]"
        if not isinstance(question, dict):
            errors.append(f"{prefix} must be an object")
            continue
        qid = question.get("id")
        if not isinstance(qid, str) or not qid.strip():
            errors.append(f"{prefix}.id must be a non-empty string")
        elif qid in seen_questions:
            errors.append(f"{prefix}.id is duplicated")
        else:
            seen_questions.add(qid)
        if not isinstance(question.get("prompt"), str) or not question["prompt"].strip():
            errors.append(f"{prefix}.prompt must be a non-empty string")
        if not isinstance(question.get("why"), str) or not question["why"].strip():
            errors.append(f"{prefix}.why must be a non-empty string")
        for field in ("required", "allow_other"):
            if field in question and not isinstance(question[field], bool):
                errors.append(f"{prefix}.{field} must be a boolean")
        qtype = question.get("type")
        if qtype not in {"single", "multi", "text"}:
            errors.append(f"{prefix}.type must be single, multi, or text")
        options = question.get("options", [])
        if qtype in {"single", "multi"}:
            if not isinstance(options, list) or len(options) < 2:
                errors.append(f"{prefix}.options must contain at least two options")
                options = []
            seen_options: set[str] = set()
            recommended = 0
            for option_index, option in enumerate(options):
                oprefix = f"{prefix}.options[{option_index}]"
                if not isinstance(option, dict):
                    errors.append(f"{oprefix} must be an object")
                    continue
                oid = option.get("id")
                if not isinstance(oid, str) or not oid.strip():
                    errors.append(f"{oprefix}.id must be a non-empty string")
                elif oid in seen_options:
                    errors.append(f"{oprefix}.id is duplicated")
                else:
                    seen_options.add(oid)
                for field in ("label", "details"):
                    if not isinstance(option.get(field), str) or not option[field].strip():
                        errors.append(f"{oprefix}.{field} must be a non-empty string")
                if option.get("recommended") is True:
                    recommended += 1
                    if not isinstance(option.get("recommendation_reason"), str) or not option["recommendation_reason"].strip():
                        errors.append(f"{oprefix}.recommendation_reason is required")
            if recommended > 1:
                errors.append(f"{prefix} has more than one recommended option")
        if qtype == "multi":
            minimum = question.get("min", 1 if question.get("required") else 0)
            maximum = question.get("max", len(options) if isinstance(options, list) else 0)
            if (
                not isinstance(minimum, int)
                or isinstance(minimum, bool)
                or not isinstance(maximum, int)
                or isinstance(maximum, bool)
                or minimum < 0
                or maximum < minimum
            ):
                errors.append(f"{prefix}.min/max are invalid")
            elif isinstance(options, list) and maximum > len(options):
                errors.append(f"{prefix}.max exceeds the number of options")
        if "when" in question:
            _validate_condition(question["when"], earlier_choice_options, f"{prefix}.when", errors)
        if qtype in {"single", "multi"} and isinstance(qid, str) and qid.strip():
            earlier_choice_options[qid] = {
                option.get("id") for option in options
                if isinstance(option, dict) and isinstance(option.get("id"), str)
            }
    if errors:
        raise ValueError("Invalid specification:\n- " + "\n- ".join(errors))


def render_html(spec: dict[str, Any]) -> str:
    safe_json = json.dumps(spec, ensure_ascii=False).replace("<", "\\u003c").replace("&", "\\u0026")
    locale = spec.get("locale", "en")
    ui = UI_TEXT[locale]
    safe_ui = json.dumps(ui, ensure_ascii=False).replace("<", "\\u003c").replace("&", "\\u0026")
    title = html.escape(spec["title"])
    page = '''<!doctype html>
<html lang="__LANG__">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>__TITLE__ · Boxing Me</title>
<style>
:root{--ink:#172033;--muted:#667085;--line:#d9dfeb;--paper:#fff;--wash:#f4f6fa;--accent:#4f46e5;--accent2:#eef2ff;--good:#087a55;--warn:#a44811;--shadow:0 18px 60px rgba(24,31,51,.11)}
*{box-sizing:border-box} body{margin:0;background:linear-gradient(145deg,#eef2ff 0,#f8fafc 42%,#fef7ed 100%);color:var(--ink);font:200 16px/1.55 "Noto Sans","Noto Sans Thai",ui-sans-serif,system-ui,-apple-system,"Segoe UI",sans-serif;min-height:100vh}
button,input,textarea,select{font:inherit;font-weight:200} button{cursor:pointer} [hidden]{display:none!important}.shell{width:min(960px,calc(100% - 28px));margin:36px auto 80px}.hero,.panel{background:rgba(255,255,255,.94);border:1px solid rgba(217,223,235,.9);box-shadow:var(--shadow);border-radius:22px}
.hero{padding:clamp(24px,5vw,48px);position:relative;overflow:hidden}.hero:after{content:"";position:absolute;width:220px;height:220px;border-radius:50%;background:#e0e7ff;right:-80px;top:-100px;opacity:.75}.hero>*{position:relative;z-index:1}.eyebrow{text-transform:uppercase;letter-spacing:.14em;font-weight:800;font-size:.75rem;color:var(--accent)}h1{font-size:clamp(2rem,5vw,3.5rem);font-weight:800;line-height:1.06;margin:.3rem 0 1rem;max-width:720px}.context{color:var(--muted);max-width:700px;font-size:1.08rem}.progress{margin-top:24px;display:flex;gap:12px;align-items:center}.track{height:9px;flex:1;background:#e8ecf3;border-radius:99px;overflow:hidden}.bar{height:100%;width:0;background:linear-gradient(90deg,var(--accent),#8b5cf6);transition:width .25s}.count{font-size:.85rem;color:var(--muted);white-space:nowrap}
.toolbar{display:flex;gap:10px;flex-wrap:wrap;margin:18px 0}.btn{border:1px solid var(--line);background:#fff;color:var(--ink);border-radius:11px;padding:10px 15px;font-weight:750}.btn:hover{border-color:#aab4c6}.btn.primary{background:var(--accent);color:#fff;border-color:var(--accent)}.btn.ghost{background:transparent}.btn.danger{color:#b42318}
.question{padding:clamp(20px,4vw,34px);margin-top:18px}.qtop{display:flex;justify-content:space-between;gap:16px;align-items:flex-start}.qnum{color:var(--accent);font-weight:850;font-size:.8rem;letter-spacing:.08em}h2{margin:.25rem 0 .4rem;font-size:clamp(1.25rem,3vw,1.7rem);font-weight:750;line-height:1.25}.why{margin:0;color:var(--muted)}.required{border:1px solid #fdba74;color:var(--warn);background:#fff7ed;border-radius:99px;padding:4px 9px;font-size:.75rem;font-weight:800;white-space:nowrap}.custom-tools{display:flex;gap:7px;margin-top:10px}.custom-tools .btn{padding:6px 10px;font-size:.78rem}
.options{display:grid;gap:11px;margin-top:22px}.option{display:block;border:1.5px solid var(--line);border-radius:15px;padding:16px;transition:.15s;background:var(--paper)}.option:hover{border-color:#a5b4fc;transform:translateY(-1px)}.option.selected{border-color:var(--accent);box-shadow:0 0 0 3px var(--accent2)}.option-head{display:flex;gap:11px;align-items:flex-start}.option input{accent-color:var(--accent);width:18px;height:18px;margin-top:3px}.label{font-weight:800}.pill{font-size:.7rem;font-weight:850;letter-spacing:.04em;text-transform:uppercase;background:#dcfce7;color:#087a55;border-radius:99px;padding:3px 8px;margin-left:8px}.details{display:block;color:var(--muted);margin:6px 0 0 29px}.recommend{display:block;background:#f0fdf4;color:#116044;border-left:3px solid #34d399;margin:10px 0 0 29px;padding:8px 11px;border-radius:6px;font-size:.9rem}
.textinput,.notes,select{width:100%;border:1.5px solid var(--line);border-radius:12px;padding:12px;background:#fff;min-height:48px}textarea{resize:vertical}.textinput:focus,.notes:focus,select:focus{outline:3px solid var(--accent2);border-color:var(--accent)}.other{margin-top:12px}.subtle,.field-label{display:block;font-size:.82rem;color:var(--muted);font-weight:700;margin:16px 0 6px}.error{color:#b42318;font-size:.85rem;font-weight:750;min-height:1.3em;margin-top:8px}.invalid{border-color:#b42318!important;background:#fff8f7!important}
.builder{padding:clamp(22px,4vw,36px);margin:18px 0}.field-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:0 14px}.check-row{display:flex;gap:18px;flex-wrap:wrap;margin:14px 0}.check-row label{font-weight:650}.option-editor{display:grid;grid-template-columns:1fr 1.5fr;gap:10px;padding:12px;margin-top:10px;background:var(--wash);border-radius:12px}.option-editor .reason{grid-column:2}.option-editor .recommend-check{display:flex;gap:8px;align-items:center;font-weight:650}.builder-actions{display:flex;gap:10px;flex-wrap:wrap;margin-top:18px}
.review{padding:clamp(22px,4vw,36px);margin-top:22px}.summary{display:grid;gap:9px;margin:16px 0 22px}.summary-row{padding:12px 14px;background:var(--wash);border-radius:10px}.summary-row strong{display:block;font-size:.82rem;font-weight:750}.summary-row span{color:var(--muted)}.actions{display:flex;gap:10px;flex-wrap:wrap;margin-top:18px}.status{min-height:1.5em;margin-top:12px;color:var(--good);font-weight:750}footer{text-align:center;color:var(--muted);font-size:.8rem;margin-top:24px}
@media(max-width:600px){.shell{margin-top:14px}.qtop{display:block}.required{display:inline-block;margin-top:8px}.btn{flex:1}.field-grid,.option-editor{grid-template-columns:1fr}.option-editor .reason{grid-column:1}}
@media print{body{background:#fff}.shell{width:100%;margin:0}.hero,.panel{box-shadow:none}.toolbar,.actions,.custom-tools,.builder{display:none}}
</style>
</head>
<body><main class="shell"><section class="hero"><div class="eyebrow" id="decisionBrief"></div><h1 id="title"></h1><p class="context" id="context"></p><div class="progress"><div class="track"><div class="bar" id="bar"></div></div><span class="count" id="count"></span></div></section>
<div class="toolbar"><button class="btn" id="recommend" type="button"></button><button class="btn" id="addQuestion" type="button"></button><button class="btn ghost" id="clear" type="button"></button></div>
<section class="panel builder" id="builder" hidden><div class="eyebrow" id="builderEyebrow"></div><h2 id="builderTitle"></h2><div class="field-grid"><label><span class="field-label" id="promptLabel"></span><input class="textinput" id="builderPrompt"></label><label><span class="field-label" id="whyLabel"></span><input class="textinput" id="builderWhy"></label><label><span class="field-label" id="typeLabel"></span><select id="builderType"><option value="single" id="singleType"></option><option value="multi" id="multiType"></option><option value="text" id="textType"></option></select></label><div id="limits"><div class="field-grid"><label><span class="field-label" id="minimumLabel"></span><input class="textinput" id="builderMin" type="number" min="0"></label><label><span class="field-label" id="maximumLabel"></span><input class="textinput" id="builderMax" type="number" min="0"></label></div></div></div><div class="check-row"><label><input type="checkbox" id="builderRequired"> <span id="requiredLabel"></span></label><label id="allowOtherWrap"><input type="checkbox" id="builderOther"> <span id="allowOtherLabel"></span></label></div><div id="builderChoiceFields"><span class="field-label" id="optionsLabel"></span><label class="recommend-check"><input type="radio" name="builder-recommended" id="noRecommendation"> <span id="noRecommendationLabel"></span></label><div id="builderOptions"></div><button class="btn" id="addOption" type="button"></button></div><div class="builder-actions"><button class="btn primary" id="submitBuilder" type="button"></button><button class="btn" id="cancelBuilder" type="button"></button></div><div class="error" id="builderError" role="alert"></div></section>
<form id="form" novalidate></form><section class="panel review"><div class="eyebrow" id="reviewLabel"></div><h2 id="directionLabel"></h2><div class="summary" id="summary"></div><label for="overall" class="subtle" id="overallLabel"></label><textarea id="overall" class="notes" rows="4"></textarea><div class="actions"><button class="btn primary" id="save" type="button"></button><button class="btn" id="copy" type="button"></button><button class="btn" id="download" type="button"></button></div><div class="status" id="status" role="status" aria-live="polite"></div></section><footer id="privacy"></footer></main>
<script>
const spec=__SPEC__,ui=__UI__,key=`boxing-me:${spec.id}`;
const state={answers:{},notes:{},overall:"",custom:[]};
try{Object.assign(state,JSON.parse(localStorage.getItem(key)||"{}"))}catch{}
if(!state.answers||typeof state.answers!=="object")state.answers={};if(!state.notes||typeof state.notes!=="object")state.notes={};if(!Array.isArray(state.custom))state.custom=[];
const validStoredQuestion=q=>q&&typeof q.id==="string"&&typeof q.prompt==="string"&&typeof q.why==="string"&&["single","multi","text"].includes(q.type)&&(q.type==="text"||Array.isArray(q.options)&&q.options.length>=2&&q.options.every(o=>o&&typeof o.id==="string"&&typeof o.label==="string"&&typeof o.details==="string"));
state.custom=state.custom.filter(validStoredQuestion);
let editingId=null;
const $=selector=>document.querySelector(selector),esc=value=>String(value??"").replace(/[&<>"']/g,char=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[char]));
const questions=()=>[...spec.questions.map(q=>({...q,source:"agent"})),...state.custom.map(q=>({...q,source:"user"}))];
for(const q of questions()){const answer=state.answers[q.id];if(q.type==="multi"&&!Array.isArray(answer))delete state.answers[q.id];if(q.type!=="multi"&&answer!=null&&typeof answer!=="string")delete state.answers[q.id];if(state.notes[q.id]!=null&&typeof state.notes[q.id]!=="string")delete state.notes[q.id]}
function conditionReady(condition,active){if(condition.length===2&&typeof condition[1]==="string")return active.has(condition[0]);const op=condition[0];if(op==="all"||op==="any")return condition.slice(1).every(item=>conditionReady(item,active));return conditionReady(condition[1],active)}
function conditionMatches(condition){if(condition.length===2&&typeof condition[1]==="string"){const answer=state.answers[condition[0]];return Array.isArray(answer)?answer.includes(condition[1]):answer===condition[1]}const op=condition[0];if(op==="all")return condition.slice(1).every(conditionMatches);if(op==="any")return condition.slice(1).some(conditionMatches);return !conditionMatches(condition[1])}
function activeQuestions(){const active=new Set(),result=[];for(const q of questions()){if(!q.when||(conditionReady(q.when,active)&&conditionMatches(q.when))){active.add(q.id);result.push(q)}}return result}
function persist(){localStorage.setItem(key,JSON.stringify(state))}
function optionMarkup(q,o){const type=q.type==="multi"?"checkbox":"radio";return `<label class="option" data-q="${esc(q.id)}" data-o="${esc(o.id)}"><span class="option-head"><input type="${type}" name="${esc(q.id)}" value="${esc(o.id)}"><span><span class="label">${esc(o.label)}</span>${o.recommended?`<span class="pill">${esc(ui.recommended)}</span>`:""}</span></span><span class="details">${esc(o.details)}</span>${o.recommended?`<span class="recommend"><strong>${esc(ui.why_this)}</strong> ${esc(o.recommendation_reason)}</span>`:""}</label>`}
function questionMarkup(q){const tools=q.source==="user"?`<div class="custom-tools"><button class="btn" type="button" data-edit="${esc(q.id)}">${esc(ui.edit)}</button><button class="btn danger" type="button" data-delete="${esc(q.id)}">${esc(ui.delete)}</button></div>`:"";return `<section class="panel question" data-question="${esc(q.id)}"><div class="qtop"><div><div class="qnum"></div><h2>${esc(q.prompt)}</h2><p class="why">${esc(q.why)}</p>${tools}</div>${q.required?`<span class="required">${esc(ui.required)}</span>`:""}</div>${q.type==="text"?`<textarea class="textinput" data-text="${esc(q.id)}" rows="4" placeholder="${esc(ui.write_answer)}"></textarea>`:`<div class="options">${q.options.map(o=>optionMarkup(q,o)).join("")}</div>${q.allow_other?`<div class="other"><label class="subtle" for="other-${esc(q.id)}">${esc(ui.other)}</label><input id="other-${esc(q.id)}" class="textinput" data-other="${esc(q.id)}" placeholder="${esc(ui.other_placeholder)}"></div>`:""}`}<label class="subtle" for="note-${esc(q.id)}">${esc(ui.notes)}</label><textarea id="note-${esc(q.id)}" class="notes" data-note="${esc(q.id)}" rows="2" placeholder="${esc(ui.notes_placeholder)}"></textarea><div class="error" data-error="${esc(q.id)}"></div></section>`}
function restoreInputs(){for(const q of questions()){const answer=state.answers[q.id];if(q.type==="text"){const el=$(`[data-text="${CSS.escape(q.id)}"]`);if(el)el.value=answer||""}else{const values=Array.isArray(answer)?answer:[answer];document.querySelectorAll(`input[name="${CSS.escape(q.id)}"]`).forEach(el=>el.checked=values.includes(el.value));const other=$(`[data-other="${CSS.escape(q.id)}"]`);if(other)other.value=state.answers[`${q.id}__other`]||""}const note=$(`[data-note="${CSS.escape(q.id)}"]`);if(note)note.value=state.notes[q.id]||""}$("#overall").value=state.overall||""}
function bindQuestions(){document.querySelectorAll('#form input[type=radio],#form input[type=checkbox]').forEach(el=>el.addEventListener("change",()=>{const q=questions().find(item=>item.id===el.name);state.answers[q.id]=q.type==="multi"?[...document.querySelectorAll(`input[name="${CSS.escape(q.id)}"]:checked`)].map(item=>item.value):el.value;persist();update()}));document.querySelectorAll("[data-text]").forEach(el=>el.addEventListener("input",()=>{state.answers[el.dataset.text]=el.value;persist();update()}));document.querySelectorAll("[data-other]").forEach(el=>el.addEventListener("input",()=>{state.answers[`${el.dataset.other}__other`]=el.value;persist();update()}));document.querySelectorAll("[data-note]").forEach(el=>el.addEventListener("input",()=>{state.notes[el.dataset.note]=el.value;persist()}));document.querySelectorAll("[data-edit]").forEach(el=>el.addEventListener("click",()=>openBuilder(state.custom.find(q=>q.id===el.dataset.edit))));document.querySelectorAll("[data-delete]").forEach(el=>el.addEventListener("click",()=>deleteQuestion(el.dataset.delete)))}
function renderQuestions(){$("#form").innerHTML=questions().map(questionMarkup).join("");bindQuestions();restoreInputs();update()}
function answered(q){const answer=state.answers[q.id],other=(state.answers[`${q.id}__other`]||"").trim();return q.type==="multi"?(answer||[]).length>0||!!other:!!(String(answer||"").trim()||other)}
function validate(show=false){let valid=true;const activeIds=new Set(activeQuestions().map(q=>q.id));for(const q of questions()){let message="";if(activeIds.has(q.id)){const answer=state.answers[q.id];if(q.required&&!answered(q))message=ui.choose_answer;if(q.type==="multi"){const count=(answer||[]).length+(state.answers[`${q.id}__other`]?.trim()?1:0),min=q.min??(q.required?1:0),max=q.max??q.options.length;if(count<min)message=ui.choose_min.replace("%n%",min);if(count>max)message=ui.choose_max.replace("%n%",max)}}if(message)valid=false;const el=$(`[data-error="${CSS.escape(q.id)}"]`);if(el)el.textContent=show?message:""}return valid}
function answerPayload(q){const ids=q.type==="multi"?(state.answers[q.id]||[]):state.answers[q.id]?[state.answers[q.id]]:[];return{question_id:q.id,prompt:q.prompt,selected:ids.map(id=>{const option=(q.options||[]).find(item=>item.id===id);return{id,label:option?.label||id}}),text:q.type==="text"?(state.answers[q.id]||""):undefined,other:state.answers[`${q.id}__other`]||"",notes:state.notes[q.id]||"",source:q.source}}
function payload(){return{format:"boxing-me-response-v1",spec_id:spec.id,spec_title:spec.title,saved_at:new Date().toISOString(),answers:activeQuestions().map(answerPayload),overall_notes:state.overall||"",custom_questions:state.custom}}
function brief(){const response=payload();return[`${ui.brief_title} ${response.spec_title}`,...response.answers.map(answer=>{const value=answer.text||answer.selected.map(item=>item.label).join(", ")||answer.other||ui.unanswered;return`- ${answer.prompt}: ${value}${answer.other&&value!==answer.other?`; ${ui.other_brief} ${answer.other}`:""}${answer.notes?`; ${ui.notes_brief} ${answer.notes}`:""}`}),response.overall_notes?`- ${ui.overall_brief} ${response.overall_notes}`:null].filter(Boolean).join(String.fromCharCode(10))}
function update(){const active=activeQuestions(),activeIds=new Set(active.map(q=>q.id));let number=0;document.querySelectorAll("[data-question]").forEach(section=>{const visible=activeIds.has(section.dataset.question);section.hidden=!visible;if(visible)section.querySelector(".qnum").textContent=`${questions().find(q=>q.id===section.dataset.question)?.source==="user"?ui.custom:ui.decision} ${++number}`});document.querySelectorAll(".option").forEach(el=>el.classList.toggle("selected",el.querySelector("input").checked));const done=active.filter(answered).length;$("#bar").style.width=`${active.length?done/active.length*100:0}%`;$("#count").textContent=ui.count.replace("%done%",done).replace("%total%",active.length);const response=payload();$("#summary").innerHTML=response.answers.map(answer=>{const value=answer.text||answer.selected.map(item=>item.label).join(", ")||answer.other||ui.not_answered;return`<div class="summary-row"><strong>${esc(answer.prompt)}</strong><span>${esc(value)}</span></div>`}).join("");validate(false)}
function slug(value){return value.toLowerCase().normalize("NFKD").replace(/[^a-z0-9]+/g,"-").replace(/^-|-$/g,"").slice(0,40)||"custom"}
function uniqueId(value,used){const base=slug(value);let id=base,index=2;while(used.has(id))id=`${base}-${index++}`;return id}
function readOptionEditors(){return[...document.querySelectorAll(".option-editor")].map((row,index)=>({label:row.querySelector("[data-option-label]").value.trim(),details:row.querySelector("[data-option-details]").value.trim(),reason:row.querySelector("[data-option-reason]").value.trim(),recommended:row.querySelector("[data-option-recommended]").checked,index}))}
function optionEditorMarkup(option={},index=0){return`<div class="option-editor"><input class="textinput" data-option-label placeholder="${esc(ui.option_label)}" value="${esc(option.label||"")}"><input class="textinput" data-option-details placeholder="${esc(ui.details_label)}" value="${esc(option.details||"")}"><label class="recommend-check"><input type="radio" name="builder-recommended" data-option-recommended ${option.recommended?"checked":""}> ${esc(ui.recommend_label)}</label><input class="textinput reason" data-option-reason placeholder="${esc(ui.reason_label)}" value="${esc(option.recommendation_reason??option.reason??"")}"><button class="btn danger" type="button" data-remove-option="${index}">${esc(ui.delete)}</button></div>`}
function renderOptionEditors(options){$("#builderOptions").innerHTML=options.map(optionEditorMarkup).join("");if(!options.some(option=>option.recommended))$("#noRecommendation").checked=true;document.querySelectorAll("[data-remove-option]").forEach(button=>button.addEventListener("click",()=>{const current=readOptionEditors();current.splice(Number(button.dataset.removeOption),1);renderOptionEditors(current)}))}
function syncBuilderType(){const choice=$("#builderType").value!=="text";$("#builderChoiceFields").hidden=!choice;$("#allowOtherWrap").hidden=!choice;$("#limits").hidden=$("#builderType").value!=="multi"}
function openBuilder(question=null){editingId=question?.id||null;$("#builder").hidden=false;$("#builderTitle").textContent=question?ui.update_question:ui.builder_title;$("#submitBuilder").textContent=question?ui.update_question:ui.create_question;$("#builderPrompt").value=question?.prompt||"";$("#builderWhy").value=question?.why||"";$("#builderType").value=question?.type||"single";$("#builderRequired").checked=!!question?.required;$("#builderOther").checked=!!question?.allow_other;$("#builderMin").value=question?.min??"";$("#builderMax").value=question?.max??"";$("#noRecommendation").checked=!(question?.options||[]).some(option=>option.recommended);$("#builderError").textContent="";renderOptionEditors(question?.options||[{},{ }]);syncBuilderType();$("#builder").scrollIntoView({behavior:"smooth",block:"start"})}
function closeBuilder(){$("#builder").hidden=true;editingId=null;$("#builderError").textContent=""}
function saveBuilder(){const wasEditing=!!editingId,prompt=$("#builderPrompt").value.trim(),why=$("#builderWhy").value.trim(),type=$("#builderType").value,required=$("#builderRequired").checked,allowOther=$("#builderOther").checked,rawOptions=readOptionEditors();document.querySelectorAll("#builder .invalid").forEach(el=>el.classList.remove("invalid"));let invalid=!prompt||!why;if(!prompt)$("#builderPrompt").classList.add("invalid");if(!why)$("#builderWhy").classList.add("invalid");let options=[];if(type!=="text"){if(rawOptions.length<2)invalid=true;const labels=new Set();options=rawOptions.map(item=>{const labelKey=item.label.toLowerCase();if(!item.label||!item.details||labels.has(labelKey)||(item.recommended&&!item.reason))invalid=true;labels.add(labelKey);const option={id:"",label:item.label,details:item.details};if(item.recommended){option.recommended=true;option.recommendation_reason=item.reason}return option});const used=new Set();for(const option of options){option.id=uniqueId(option.label,used);used.add(option.id)}}let minimum,maximum;if(type==="multi"){minimum=$("#builderMin").value===""?(required?1:0):Number($("#builderMin").value);maximum=$("#builderMax").value===""?options.length:Number($("#builderMax").value);if(!Number.isInteger(minimum)||!Number.isInteger(maximum)||minimum<0||maximum<minimum||maximum>options.length)invalid=true}if(invalid){$("#builderError").textContent=ui.builder_invalid;return}const usedQuestions=new Set(questions().filter(q=>q.id!==editingId).map(q=>q.id)),id=editingId||uniqueId(prompt,usedQuestions),question={id,prompt,why,type,required,source:"user"};if(type!=="text"){question.options=options;question.allow_other=allowOther}if(type==="multi"){question.min=minimum;question.max=maximum}if(editingId){const index=state.custom.findIndex(q=>q.id===editingId);state.custom[index]=question;delete state.answers[id];delete state.answers[`${id}__other`];delete state.notes[id]}else state.custom.push(question);persist();renderQuestions();closeBuilder();$("#status").textContent=wasEditing?ui.question_updated:ui.question_added}
function deleteQuestion(id){if(!confirm(ui.delete_confirm))return;state.custom=state.custom.filter(q=>q.id!==id);delete state.answers[id];delete state.answers[`${id}__other`];delete state.notes[id];persist();renderQuestions();$("#status").textContent=ui.question_deleted}
function staticText(){document.title=`${spec.title} · Boxing Me`;$("#title").textContent=spec.title;$("#context").textContent=spec.context;const values={decisionBrief:"decision_brief",recommend:"apply",addQuestion:"add_question",clear:"clear",builderEyebrow:"custom",builderTitle:"builder_title",promptLabel:"prompt_label",whyLabel:"why_label",typeLabel:"type_label",singleType:"single_type",multiType:"multi_type",textType:"text_type",minimumLabel:"minimum_label",maximumLabel:"maximum_label",requiredLabel:"required_label",allowOtherLabel:"allow_other_label",optionsLabel:"options_label",noRecommendationLabel:"no_recommendation",addOption:"add_option",submitBuilder:"create_question",cancelBuilder:"cancel",reviewLabel:"review",directionLabel:"direction",overallLabel:"overall_label",save:"save",copy:"copy",download:"download",privacy:"privacy"};for(const [id,keyName] of Object.entries(values))$(`#${id}`).textContent=ui[keyName];$("#overall").placeholder=ui.overall_placeholder}
$("#overall").addEventListener("input",event=>{state.overall=event.target.value;persist()});$("#addQuestion").addEventListener("click",()=>openBuilder());$("#cancelBuilder").addEventListener("click",closeBuilder);$("#builderType").addEventListener("change",syncBuilderType);$("#addOption").addEventListener("click",()=>renderOptionEditors([...readOptionEditors(),{}]));$("#submitBuilder").addEventListener("click",saveBuilder);
$("#recommend").addEventListener("click",()=>{for(let pass=0;pass<questions().length;pass++){let changed=false;for(const q of activeQuestions()){const option=(q.options||[]).find(item=>item.recommended);if(!option)continue;if(q.type==="multi"){const current=state.answers[q.id]||[],other=state.answers[`${q.id}__other`]?.trim()?1:0,max=q.max??q.options.length;if(!current.includes(option.id)&&current.length+other<max){state.answers[q.id]=[...current,option.id];changed=true}}else if(state.answers[q.id]!==option.id){state.answers[q.id]=option.id;changed=true}}if(!changed)break}persist();restoreInputs();update()});
$("#clear").addEventListener("click",()=>{if(!confirm(ui.clear_confirm))return;state.answers={};state.notes={};state.overall="";persist();restoreInputs();update();$("#status").textContent=ui.cleared});
$("#copy").addEventListener("click",async()=>{try{await navigator.clipboard.writeText(brief());$("#status").textContent=ui.copied}catch{$("#status").textContent=ui.copy_blocked}});$("#download").addEventListener("click",()=>{const blob=new Blob([JSON.stringify(payload(),null,2)],{type:"application/json"}),anchor=document.createElement("a");anchor.href=URL.createObjectURL(blob);anchor.download=`${spec.id}-response.json`;anchor.click();URL.revokeObjectURL(anchor.href);$("#status").textContent=ui.downloaded});
$("#save").addEventListener("click",async()=>{if(!validate(true)){$("#status").textContent=ui.complete_required;document.querySelector(".error:not(:empty)")?.scrollIntoView({behavior:"smooth",block:"center"});return}const button=$("#save");button.disabled=true;try{const response=await fetch("/api/save",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(payload())});if(!response.ok)throw new Error();const result=await response.json();$("#status").textContent=`${ui.saved} (${result.filename})`}catch{$("#status").textContent=ui.save_fallback;$("#download").click()}finally{button.disabled=false}});
staticText();renderQuestions();
</script></body></html>'''
    replacements = {"LANG": locale, "TITLE": title, "SPEC": safe_json, "UI": safe_ui}
    return re.sub(r"__(LANG|TITLE|SPEC|UI)__", lambda match: replacements[match.group(1)], page)


def atomic_write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=path.parent, delete=False) as handle:
        handle.write(content)
        temporary = Path(handle.name)
    os.replace(temporary, path)


def build(spec_path: Path, output_path: Path) -> dict[str, Any]:
    spec = load_spec(spec_path)
    atomic_write(output_path, render_html(spec))
    return spec


def make_handler(page: bytes, response_path: Path, spec_id: str):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, message: str, *args: Any) -> None:
            print(f"BOXING_ME_HTTP={self.address_string()} {message % args}", flush=True)

        def send_bytes(self, status: int, content_type: str, body: bytes) -> None:
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self) -> None:
            if self.path in {"/", "/index.html"}:
                self.send_bytes(200, "text/html; charset=utf-8", page)
            elif self.path == "/api/status":
                body = json.dumps({"ready": True, "saved": response_path.exists()}).encode()
                self.send_bytes(200, "application/json", body)
            else:
                self.send_bytes(404, "text/plain; charset=utf-8", b"Not found")

        def do_POST(self) -> None:
            if self.path != "/api/save":
                self.send_bytes(404, "text/plain; charset=utf-8", b"Not found")
                return
            try:
                length = int(self.headers.get("Content-Length", "0"))
            except ValueError:
                length = 0
            if length <= 0 or length > MAX_BODY:
                self.send_bytes(413, "application/json", b'{"error":"invalid payload size"}')
                return
            try:
                payload = json.loads(self.rfile.read(length))
                if (
                    not isinstance(payload, dict)
                    or payload.get("format") != "boxing-me-response-v1"
                    or payload.get("spec_id") != spec_id
                    or not isinstance(payload.get("spec_title"), str)
                    or not payload["spec_title"].strip()
                    or not isinstance(payload.get("saved_at"), str)
                    or not payload["saved_at"].strip()
                    or not isinstance(payload.get("answers"), list)
                    or not all(isinstance(answer, dict) for answer in payload["answers"])
                    or not isinstance(payload.get("overall_notes"), str)
                    or not isinstance(payload.get("custom_questions"), list)
                    or not all(isinstance(question, dict) for question in payload["custom_questions"])
                ):
                    raise ValueError("response does not match this page")
                payload["received_at"] = datetime.now(timezone.utc).isoformat()
                atomic_write(response_path, json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
            except (json.JSONDecodeError, ValueError, OSError) as exc:
                body = json.dumps({"error": str(exc)}).encode()
                self.send_bytes(400, "application/json", body)
                return
            body = json.dumps({"saved": True, "filename": response_path.name}).encode()
            self.send_bytes(200, "application/json", body)

    return Handler


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    for command in ("validate", "build", "serve"):
        sub = subparsers.add_parser(command)
        sub.add_argument("spec", type=Path)
        if command in {"build", "serve"}:
            sub.add_argument("--output", type=Path, required=True)
        if command == "serve":
            sub.add_argument("--response", type=Path, required=True)
            sub.add_argument("--host", default="127.0.0.1")
            sub.add_argument("--port", type=int, default=0)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        if args.command == "validate":
            spec = load_spec(args.spec)
            print(f"VALID spec={spec['id']} questions={len(spec['questions'])}")
            return 0
        spec = build(args.spec, args.output)
        print(f"BUILT={args.output.resolve()}", flush=True)
        if args.command == "build":
            return 0
        server = ThreadingHTTPServer((args.host, args.port), make_handler(args.output.read_bytes(), args.response.resolve(), spec["id"]))
        host, port = server.server_address[:2]
        print(f"BOXING_ME_URL=http://{host}:{port}/", flush=True)
        print(f"BOXING_ME_RESPONSE={args.response.resolve()}", flush=True)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass
        finally:
            server.server_close()
        return 0
    except ValueError as exc:
        print(exc, file=__import__("sys").stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
