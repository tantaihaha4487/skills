#!/usr/bin/env python3
"""Build and locally serve a self-contained Boxing Me decision page."""

from __future__ import annotations

import argparse
import html
import json
import os
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
        "saved": "Saved. Tell the agent you are done.", "save_fallback": "No local save server found. Your JSON was downloaded instead."
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
        "saved": "บันทึกแล้ว กรุณาบอก Agent ว่าคุณทำเสร็จแล้ว", "save_fallback": "ไม่พบเซิร์ฟเวอร์สำหรับบันทึก จึงดาวน์โหลด JSON ให้แทน"
    },
}


def load_spec(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"Cannot read specification: {exc}") from exc
    validate_spec(value)
    return value


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
            if not isinstance(minimum, int) or not isinstance(maximum, int) or minimum < 0 or maximum < minimum:
                errors.append(f"{prefix}.min/max are invalid")
            elif isinstance(options, list) and maximum > len(options):
                errors.append(f"{prefix}.max exceeds the number of options")
    if errors:
        raise ValueError("Invalid specification:\n- " + "\n- ".join(errors))


def render_html(spec: dict[str, Any]) -> str:
    safe_json = json.dumps(spec, ensure_ascii=False).replace("<", "\\u003c").replace("&", "\\u0026")
    locale = spec.get("locale", "en")
    ui = UI_TEXT[locale]
    safe_ui = json.dumps(ui, ensure_ascii=False).replace("<", "\\u003c").replace("&", "\\u0026")
    title = html.escape(spec["title"])
    page = f'''<!doctype html>
<html lang="{locale}">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title} · Boxing Me</title>
<style>
:root{{--ink:#172033;--muted:#667085;--line:#d9dfeb;--paper:#fff;--wash:#f4f6fa;--accent:#4f46e5;--accent2:#eef2ff;--good:#087a55;--warn:#a44811;--shadow:0 18px 60px rgba(24,31,51,.11)}}
*{{box-sizing:border-box}} body{{margin:0;background:linear-gradient(145deg,#eef2ff 0,#f8fafc 42%,#fef7ed 100%);color:var(--ink);font:16px/1.55 ui-sans-serif,system-ui,-apple-system,"Segoe UI",sans-serif;min-height:100vh}}
button,input,textarea{{font:inherit}} button{{cursor:pointer}} .shell{{width:min(960px,calc(100% - 28px));margin:36px auto 80px}} .hero,.panel{{background:rgba(255,255,255,.94);border:1px solid rgba(217,223,235,.9);box-shadow:var(--shadow);border-radius:22px}}
.hero{{padding:clamp(24px,5vw,48px);position:relative;overflow:hidden}} .hero:after{{content:"";position:absolute;width:220px;height:220px;border-radius:50%;background:#e0e7ff;right:-80px;top:-100px;opacity:.75}} .eyebrow{{text-transform:uppercase;letter-spacing:.14em;font-weight:800;font-size:.75rem;color:var(--accent)}} h1{{font-size:clamp(2rem,5vw,3.5rem);line-height:1.06;margin:.3rem 0 1rem;max-width:720px}} .context{{color:var(--muted);max-width:700px;font-size:1.08rem}} .progress{{margin-top:24px;display:flex;gap:12px;align-items:center}} .track{{height:9px;flex:1;background:#e8ecf3;border-radius:99px;overflow:hidden}} .bar{{height:100%;width:0;background:linear-gradient(90deg,var(--accent),#8b5cf6);transition:width .25s}} .count{{font-size:.85rem;color:var(--muted);white-space:nowrap}}
.toolbar{{display:flex;gap:10px;flex-wrap:wrap;margin:18px 0}} .btn{{border:1px solid var(--line);background:#fff;color:var(--ink);border-radius:11px;padding:10px 15px;font-weight:750}} .btn:hover{{border-color:#aab4c6}} .btn.primary{{background:var(--accent);color:white;border-color:var(--accent)}} .btn.ghost{{background:transparent}}
.question{{padding:clamp(20px,4vw,34px);margin-top:18px}} .qtop{{display:flex;justify-content:space-between;gap:16px;align-items:flex-start}} .qnum{{color:var(--accent);font-weight:850;font-size:.8rem;letter-spacing:.08em}} h2{{margin:.25rem 0 .4rem;font-size:clamp(1.25rem,3vw,1.7rem);line-height:1.25}} .why{{margin:0;color:var(--muted)}} .required{{border:1px solid #fdba74;color:var(--warn);background:#fff7ed;border-radius:99px;padding:4px 9px;font-size:.75rem;font-weight:800;white-space:nowrap}}
.options{{display:grid;gap:11px;margin-top:22px}} .option{{display:block;border:1.5px solid var(--line);border-radius:15px;padding:16px;transition:.15s;background:var(--paper)}} .option:hover{{border-color:#a5b4fc;transform:translateY(-1px)}} .option.selected{{border-color:var(--accent);box-shadow:0 0 0 3px var(--accent2)}} .option-head{{display:flex;gap:11px;align-items:flex-start}} .option input{{accent-color:var(--accent);width:18px;height:18px;margin-top:3px}} .label{{font-weight:800}} .pill{{font-size:.7rem;font-weight:850;letter-spacing:.04em;text-transform:uppercase;background:#dcfce7;color:#087a55;border-radius:99px;padding:3px 8px;margin-left:8px}} .details{{display:block;color:var(--muted);margin:6px 0 0 29px}} .recommend{{display:block;background:#f0fdf4;color:#116044;border-left:3px solid #34d399;margin:10px 0 0 29px;padding:8px 11px;border-radius:6px;font-size:.9rem}}
.textinput,.notes{{width:100%;border:1.5px solid var(--line);border-radius:12px;padding:12px;background:#fff;min-height:48px}} textarea{{resize:vertical}} .textinput:focus,.notes:focus{{outline:3px solid var(--accent2);border-color:var(--accent)}} .other{{margin-top:12px}} .subtle{{font-size:.82rem;color:var(--muted);font-weight:700;margin:16px 0 6px}} .error{{color:#b42318;font-size:.85rem;font-weight:750;min-height:1.3em;margin-top:8px}}
.review{{padding:clamp(22px,4vw,36px);margin-top:22px}} .summary{{display:grid;gap:9px;margin:16px 0 22px}} .summary-row{{padding:12px 14px;background:var(--wash);border-radius:10px}} .summary-row strong{{display:block;font-size:.82rem}} .summary-row span{{color:var(--muted)}} .actions{{display:flex;gap:10px;flex-wrap:wrap;margin-top:18px}} .status{{min-height:1.5em;margin-top:12px;color:var(--good);font-weight:750}} footer{{text-align:center;color:var(--muted);font-size:.8rem;margin-top:24px}} @media(max-width:600px){{.shell{{margin-top:14px}}.qtop{{display:block}}.required{{display:inline-block;margin-top:8px}}.btn{{flex:1}}}}
@media print{{body{{background:#fff}}.shell{{width:100%;margin:0}}.hero,.panel{{box-shadow:none}}.toolbar,.actions{{display:none}}}}
</style>
</head>
<body><main class="shell"><section class="hero"><div class="eyebrow">{html.escape(ui['decision_brief'])}</div><h1 id="title"></h1><p class="context" id="context"></p><div class="progress"><div class="track"><div class="bar" id="bar"></div></div><span class="count" id="count"></span></div></section><div class="toolbar"><button class="btn" id="recommend">{html.escape(ui['apply'])}</button><button class="btn ghost" id="clear">{html.escape(ui['clear'])}</button></div><form id="form" novalidate></form><section class="panel review"><div class="eyebrow">{html.escape(ui['review'])}</div><h2>{html.escape(ui['direction'])}</h2><div class="summary" id="summary"></div><label for="overall" class="subtle">{html.escape(ui['overall_label'])}</label><textarea id="overall" class="notes" rows="4" placeholder="{html.escape(ui['overall_placeholder'])}"></textarea><div class="actions"><button class="btn primary" id="save" type="button">{html.escape(ui['save'])}</button><button class="btn" id="copy" type="button">{html.escape(ui['copy'])}</button><button class="btn" id="download" type="button">{html.escape(ui['download'])}</button></div><div class="status" id="status" role="status" aria-live="polite"></div></section><footer>{html.escape(ui['privacy'])}</footer></main>
<script>
const spec={safe_json}; const ui={safe_ui}; const key=`boxing-me:${{spec.id}}`; const state={{answers:{{}},notes:{{}},overall:""}};
const esc=s=>String(s??"").replace(/[&<>"']/g,c=>({{"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}}[c]));
function optionMarkup(q,o){{const type=q.type==="multi"?"checkbox":"radio";return `<label class="option" data-q="${{esc(q.id)}}" data-o="${{esc(o.id)}}"><span class="option-head"><input type="${{type}}" name="${{esc(q.id)}}" value="${{esc(o.id)}}"><span><span class="label">${{esc(o.label)}}</span>${{o.recommended?`<span class="pill">${{esc(ui.recommended)}}</span>`:''}}</span></span><span class="details">${{esc(o.details)}}</span>${{o.recommended?`<span class="recommend"><strong>${{esc(ui.why_this)}}</strong> ${{esc(o.recommendation_reason)}}</span>`:''}}</label>`}}
function render(){{document.title=`${{spec.title}} · Boxing Me`;document.querySelector('#title').textContent=spec.title;document.querySelector('#context').textContent=spec.context;document.querySelector('#form').innerHTML=spec.questions.map((q,i)=>`<section class="panel question" data-question="${{esc(q.id)}}"><div class="qtop"><div><div class="qnum">${{esc(ui.decision)}} ${{i+1}}</div><h2>${{esc(q.prompt)}}</h2><p class="why">${{esc(q.why)}}</p></div>${{q.required?`<span class="required">${{esc(ui.required)}}</span>`:''}}</div>${{q.type==='text'?`<textarea class="textinput" data-text="${{esc(q.id)}}" rows="4" placeholder="${{esc(ui.write_answer)}}"></textarea>`:`<div class="options">${{q.options.map(o=>optionMarkup(q,o)).join('')}}</div>${{q.allow_other?`<div class="other"><label class="subtle" for="other-${{esc(q.id)}}">${{esc(ui.other)}}</label><input id="other-${{esc(q.id)}}" class="textinput" data-other="${{esc(q.id)}}" placeholder="${{esc(ui.other_placeholder)}}"></div>`:''}}`}}<label class="subtle" for="note-${{esc(q.id)}}">${{esc(ui.notes)}}</label><textarea id="note-${{esc(q.id)}}" class="notes" data-note="${{esc(q.id)}}" rows="2" placeholder="${{esc(ui.notes_placeholder)}}"></textarea><div class="error" data-error="${{esc(q.id)}}"></div></section>`).join('');bind();restore();update();}}
function bind(){{document.querySelectorAll('input[type=radio],input[type=checkbox]').forEach(el=>el.addEventListener('change',()=>{{const q=spec.questions.find(x=>x.id===el.name);if(q.type==='multi') state.answers[q.id]=[...document.querySelectorAll(`input[name="${{CSS.escape(q.id)}}"]:checked`)].map(x=>x.value);else state.answers[q.id]=el.value;persist();update();}}));document.querySelectorAll('[data-text]').forEach(el=>el.addEventListener('input',()=>{{state.answers[el.dataset.text]=el.value;persist();update();}}));document.querySelectorAll('[data-other]').forEach(el=>el.addEventListener('input',()=>{{state.answers[`${{el.dataset.other}}__other`]=el.value;persist();update();}}));document.querySelectorAll('[data-note]').forEach(el=>el.addEventListener('input',()=>{{state.notes[el.dataset.note]=el.value;persist();}}));document.querySelector('#overall').addEventListener('input',e=>{{state.overall=e.target.value;persist();}});}}
function persist(){{localStorage.setItem(key,JSON.stringify(state));}}
function restore(){{try{{Object.assign(state,JSON.parse(localStorage.getItem(key)||'{{}}'));}}catch{{}} spec.questions.forEach(q=>{{const a=state.answers[q.id];if(q.type==='text'){{const el=document.querySelector(`[data-text="${{CSS.escape(q.id)}}"]`);if(el)el.value=a||'';}}else{{const vals=Array.isArray(a)?a:[a];document.querySelectorAll(`input[name="${{CSS.escape(q.id)}}"]`).forEach(el=>el.checked=vals.includes(el.value));const other=document.querySelector(`[data-other="${{CSS.escape(q.id)}}"]`);if(other)other.value=state.answers[`${{q.id}}__other`]||'';}}const note=document.querySelector(`[data-note="${{CSS.escape(q.id)}}"]`);if(note)note.value=state.notes[q.id]||'';}});document.querySelector('#overall').value=state.overall||'';}}
function answered(q){{const a=state.answers[q.id],other=(state.answers[`${{q.id}}__other`]||'').trim();if(q.type==='multi')return (a||[]).length>0||!!other;return !!(String(a||'').trim()||other);}}
function validate(show=false){{let ok=true;spec.questions.forEach(q=>{{let msg='';const a=state.answers[q.id];if(q.required&&!answered(q))msg=ui.choose_answer;if(q.type==='multi'){{const n=(a||[]).length+(state.answers[`${{q.id}}__other`]?.trim()?1:0),min=q.min??(q.required?1:0),max=q.max??q.options.length;if(n<min)msg=ui.choose_min.replace('%n%',min);if(n>max)msg=ui.choose_max.replace('%n%',max);}}if(msg)ok=false;const el=document.querySelector(`[data-error="${{CSS.escape(q.id)}}"]`);if(el)el.textContent=show?msg:'';}});return ok;}}
function payload(){{return {{format:"boxing-me-response-v1",spec_id:spec.id,spec_title:spec.title,saved_at:new Date().toISOString(),answers:spec.questions.map(q=>{{const ids=q.type==='multi'?(state.answers[q.id]||[]):state.answers[q.id]?[state.answers[q.id]]:[];return {{question_id:q.id,prompt:q.prompt,selected:ids.map(id=>{{const o=(q.options||[]).find(x=>x.id===id);return {{id,label:o?.label||id}}}}),text:q.type==='text'?(state.answers[q.id]||''):undefined,other:state.answers[`${{q.id}}__other`]||'',notes:state.notes[q.id]||''}}}}),overall_notes:state.overall||''}};}}
function brief(){{const p=payload();return [`${{ui.brief_title}} ${{p.spec_title}}`,...p.answers.map(a=>{{const value=a.text||a.selected.map(x=>x.label).join(', ')||a.other||ui.unanswered;return `- ${{a.prompt}}: ${{value}}${{a.other&&value!==a.other?`; ${{ui.other_brief}} ${{a.other}}`:''}}${{a.notes?`; ${{ui.notes_brief}} ${{a.notes}}`:''}}`;}}),p.overall_notes?`- ${{ui.overall_brief}} ${{p.overall_notes}}`:null].filter(Boolean).join('\n');}}
function update(){{document.querySelectorAll('.option').forEach(el=>el.classList.toggle('selected',el.querySelector('input').checked));const done=spec.questions.filter(answered).length;document.querySelector('#bar').style.width=`${{done/spec.questions.length*100}}%`;document.querySelector('#count').textContent=ui.count.replace('%done%',done).replace('%total%',spec.questions.length);document.querySelector('#summary').innerHTML=spec.questions.map(q=>{{const a=payload().answers.find(x=>x.question_id===q.id),v=a.text||a.selected.map(x=>x.label).join(', ')||a.other||ui.not_answered;return `<div class="summary-row"><strong>${{esc(q.prompt)}}</strong><span>${{esc(v)}}</span></div>`}}).join('');validate(false);}}
document.querySelector('#recommend').addEventListener('click',()=>{{spec.questions.forEach(q=>{{const o=(q.options||[]).find(x=>x.recommended);if(!o)return;if(q.type==='multi')state.answers[q.id]=[...new Set([...(state.answers[q.id]||[]),o.id])];else state.answers[q.id]=o.id;}});persist();restore();update();}});
document.querySelector('#clear').addEventListener('click',()=>{{if(!confirm(ui.clear_confirm))return;state.answers={{}};state.notes={{}};state.overall='';localStorage.removeItem(key);restore();update();document.querySelector('#status').textContent=ui.cleared;}});
document.querySelector('#copy').addEventListener('click',async()=>{{try{{await navigator.clipboard.writeText(brief());document.querySelector('#status').textContent=ui.copied;}}catch{{document.querySelector('#status').textContent=ui.copy_blocked;}}}});
document.querySelector('#download').addEventListener('click',()=>{{const blob=new Blob([JSON.stringify(payload(),null,2)],{{type:'application/json'}}),a=document.createElement('a');a.href=URL.createObjectURL(blob);a.download=`${{spec.id}}-response.json`;a.click();URL.revokeObjectURL(a.href);document.querySelector('#status').textContent=ui.downloaded;}});
document.querySelector('#save').addEventListener('click',async()=>{{if(!validate(true)){{document.querySelector('#status').textContent=ui.complete_required;document.querySelector('.error:not(:empty)')?.scrollIntoView({{behavior:'smooth',block:'center'}});return;}}const button=document.querySelector('#save');button.disabled=true;try{{const response=await fetch('/api/save',{{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify(payload())}});if(!response.ok)throw new Error();const result=await response.json();document.querySelector('#status').textContent=`${{ui.saved}} (${{result.filename}})`;}}catch{{document.querySelector('#status').textContent=ui.save_fallback;document.querySelector('#download').click();}}finally{{button.disabled=false;}}}});
render();
</script></body></html>'''
    return page.replace(
        ".filter(Boolean).join('" + chr(10) + "');",
        ".filter(Boolean).join(String.fromCharCode(10));",
    )


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
                if not isinstance(payload, dict) or payload.get("spec_id") != spec_id or not isinstance(payload.get("answers"), list):
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
