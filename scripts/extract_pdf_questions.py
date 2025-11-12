#!/usr/bin/env python3
import re
import json
from pathlib import Path
from PyPDF2 import PdfReader

PDF_PATH = Path(__file__).parents[1] / 'CIVIL-DEFENCE-NSCDC-RECRUITMENT-EXAM-PAST-QUESTIONS-AND-ANSWERS.pdf'
OUT_PATH = Path(__file__).parents[1] / 'questions.json'

def extract_text_from_pdf(path):
    reader = PdfReader(str(path))
    texts = []
    for p in reader.pages:
        try:
            texts.append(p.extract_text() or "")
        except Exception:
            # fallback: try to read /contents
            texts.append("")
    return "\n".join(texts)

# heuristic parser: split by numbered question starts like "1.", "2)", "3 -" at start of a line
QUESTION_SPLIT_RE = re.compile(r'(?m)^(\s*\d{1,3})\s*[\)\.\-:]\s*', re.MULTILINE)

OPT_RE = re.compile(r'(?m)^\s*([A-D])\s*[\)\.]\s*(.+)$')


def parse_questions(fulltext):
    # Normalize line endings
    # Ensure question markers are at line starts - if not, try to insert
    # Use split with capture to get numbers
    parts = QUESTION_SPLIT_RE.split(fulltext)
    # split yields: [prefix, '1', rest, '2', rest, ...] if text starts with something before first match
    items = []
    if len(parts) < 3:
        # fallback: try to find inline occurrences like "1. " anywhere
        parts = re.split(r'(\d{1,3}\.\s+)', fulltext)
    # Build pairs
    i = 0
    # If parts[0] is prefix text before first question, skip if empty
    if parts and not parts[0].strip():
        i = 1
    while i + 1 < len(parts):
        num = parts[i].strip()
        body = parts[i+1].strip()
        # trim anything after next number (sometimes split left trailing parts)
        # body may contain next question number at start; but our split should have handled that
        items.append((num, body))
        i += 2
    questions = []
    qid = 1
    for num, body in items:
        # try to extract options A-D
        lines = [ln.rstrip() for ln in body.splitlines() if ln.strip()]
        opts = []
        other_lines = []
        current_opt = None
        for ln in lines:
            m = OPT_RE.match(ln)
            if m:
                # new option
                opts.append({'label': m.group(1), 'text': m.group(2).strip()})
                current_opt = opts[-1]
            else:
                # continuation of previous option or question text
                if current_opt is not None:
                    # append to last option text
                    current_opt['text'] += ' ' + ln.strip()
                else:
                    other_lines.append(ln)
        question_text = ' '.join(other_lines).strip()
        # normalize options to simple list
        options_list = [o['text'] for o in opts]
        questions.append({
            'id': qid,
            'num': num,
            'text': question_text,
            'options': options_list,
            'answer': None
        })
        qid += 1
    return questions


def main():
    if not PDF_PATH.exists():
        print(f"PDF not found at {PDF_PATH}")
        return
    print(f"Reading PDF: {PDF_PATH}")
    text = extract_text_from_pdf(PDF_PATH)
    print("Extracted text length:", len(text))
    questions = parse_questions(text)
    print(f"Parsed {len(questions)} candidate questions")
    # Save only questions with some text
    filtered = [q for q in questions if q['text'] or q['options']]
    with open(OUT_PATH, 'w', encoding='utf-8') as f:
        json.dump(filtered, f, ensure_ascii=False, indent=2)
    print(f"Wrote {len(filtered)} questions to {OUT_PATH}")

if __name__ == '__main__':
    main()
