"""Check the built report against the format rules of the course.

    python report/check_report.py [report/AISR_Project_Report.pdf]

Checks: page count (25-35), A4 size, a border on every page, page numbers
(none on the title page, Roman on front pages, Arabic from Section 1),
margins and fonts from the .docx, mandatory sections, abstract length
(150-200 words), every figure and table numbered, captioned and mentioned in
the text, at least 8 references all cited and first cited in order, Index
page numbers equal to the real ones, and leftover placeholders / instruction
text.  Exit code 1 if any check FAILS (WARN does not fail).
"""

from __future__ import annotations

import os
import re
import sys
import zipfile

import fitz

HERE = os.path.dirname(os.path.abspath(__file__))
PDF = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "AISR_Project_Report.pdf")
DOCX = os.path.splitext(PDF)[0] + ".docx"
results = []


def check(name, ok, detail="", warn=False):
    status = "PASS" if ok else ("WARN" if warn else "FAIL")
    results.append(status)
    print(f"[{status}] {name}" + (f": {detail}" if detail else ""))


def roman(n):
    out = ""
    for v, s in [(10, "x"), (9, "ix"), (5, "v"), (4, "iv"), (1, "i")]:
        while n >= v:
            out += s
            n -= v
    return out


doc = fitz.open(PDF)
pages = [p.get_text() for p in doc]
n = len(doc)


def heading_pages(text):
    """PDF page indices where `text` appears as a 14 pt heading line."""
    out = []
    for i, p in enumerate(doc):
        for b in p.get_text("dict")["blocks"]:
            for ln in b.get("lines", []):
                t = " ".join("".join(s["text"] for s in ln["spans"]).split())
                if t == text and max(s["size"] for s in ln["spans"]) > 13:
                    out.append(i)
    return out

# ---------------------------------------------------------------- pages and paper
check("Page count 25-35 (incl. front pages)", 25 <= n <= 35, f"{n} pages")
a4 = all(abs(p.rect.width - 595.3) < 2 and abs(p.rect.height - 841.9) < 2 for p in doc)
check("A4 portrait on every page", a4)

# ---------------------------------------------------------------- border on every page
no_border = []
for i, p in enumerate(doc):
    W, H = p.rect.width, p.rect.height
    edges = {"top": False, "bottom": False, "left": False, "right": False}
    for d in p.get_drawings():
        for it in d["items"]:
            pts = []
            if it[0] == "l":
                pts = [(it[1], it[2])]
            elif it[0] == "re":
                r = it[1]
                pts = [((r.x0, r.y0), (r.x1, r.y0)), ((r.x0, r.y1), (r.x1, r.y1)),
                       ((r.x0, r.y0), (r.x0, r.y1)), ((r.x1, r.y0), (r.x1, r.y1))]
            for a, b in pts:
                (x0, y0), (x1, y1) = (a.x, a.y) if hasattr(a, "x") else a, (b.x, b.y) if hasattr(b, "x") else b
                if abs(y0 - y1) < 1 and abs(x1 - x0) > W * 0.8:
                    if y0 < 60:
                        edges["top"] = True
                    if y0 > H - 60:
                        edges["bottom"] = True
                if abs(x0 - x1) < 1 and abs(y1 - y0) > H * 0.8:
                    if x0 < 60:
                        edges["left"] = True
                    if x0 > W - 60:
                        edges["right"] = True
    if not all(edges.values()):
        no_border.append(i + 1)
check("Single-line page border on every page (incl. title page)", not no_border,
      "missing on PDF pages " + ", ".join(map(str, no_border)) if no_border else f"{n}/{n} pages")


# ---------------------------------------------------------------- page numbers
def footer_text(i):
    p = doc[i]
    clip = fitz.Rect(0, p.rect.height - 52, p.rect.width, p.rect.height - 20)
    return " ".join(p.get_text(clip=clip).split())


body_start = heading_pages("1. Introduction")[0]
bad = []
if footer_text(0):
    bad.append(f"title page shows '{footer_text(0)}'")
for i in range(1, body_start):
    if footer_text(i) != roman(i):
        bad.append(f"PDF p{i + 1}: '{footer_text(i)}' != {roman(i)}")
for i in range(body_start, n):
    if footer_text(i) != str(i - body_start + 1):
        bad.append(f"PDF p{i + 1}: '{footer_text(i)}' != {i - body_start + 1}")
check("Page numbers: none on title, i, ii, ... on front pages, 1, 2, ... from Section 1", not bad,
      "; ".join(bad[:4]) if bad else f"front i-{roman(body_start - 1)}, body 1-{n - body_start}")

# ---------------------------------------------------------------- docx: margins, fonts, spacing
with zipfile.ZipFile(DOCX) as z:
    xml = z.read("word/document.xml").decode("utf8")
    styles = z.read("word/styles.xml").decode("utf8")
margins = re.findall(r'<w:pgMar ([^>]*)/>', xml)
ok_m = True
for m in margins:
    vals = dict(re.findall(r'w:(\w+)="(\d+)"', m))
    ok_m &= abs(int(vals["left"]) - 1701) < 5 and all(abs(int(vals[k]) - 1417) < 5 for k in ("right", "top", "bottom"))
check("Margins left 3.0 cm, right/top/bottom 2.5 cm (all sections)", ok_m and margins, f"{len(margins)} sections")
borders = len(re.findall(r"<w:pgBorders", xml))
check("Page border defined in every docx section", borders == len(margins), f"{borders}/{len(margins)}")
fonts_pdf = set()
for p in doc:
    for f in p.get_fonts():
        fonts_pdf.add(re.sub(r"^[A-Z]{6}\+", "", f[3]))
non_tnr = sorted(f for f in fonts_pdf if not f.startswith("TimesNewRoman") and "Courier" not in f
                 and "STIX" not in f.upper() and not f.startswith("Image"))
check("Text font is Times New Roman (code in Courier New)", not non_tnr,
      ", ".join(sorted(fonts_pdf)) if not non_tnr else "other fonts: " + ", ".join(non_tnr))
normal = re.search(r'w:styleId="Normal".*?</w:style>', styles, re.S).group(0)
check("Body text style: 12 pt", 'w:sz w:val="24"' in normal)
just = xml.count('<w:jc w:val="both"/>')
spacing = len(re.findall(r'w:line="360"', xml))
check("Body paragraphs justified with 1.5 line spacing", just > 50 and spacing > 50,
      f"{just} justified, {spacing} at 1.5 spacing")
h1 = re.search(r'w:styleId="Heading1".*?</w:style>', styles, re.S).group(0)
h2 = re.search(r'w:styleId="Heading2".*?</w:style>', styles, re.S).group(0)
check("Headings 14 pt bold, sub-headings 12 pt bold", 'w:sz w:val="28"' in h1 and 'w:sz w:val="24"' in h2
      and "<w:b/>" in h1 and "<w:b/>" in h2)

# ---------------------------------------------------------------- structure
full = "\n".join(pages)
required = ["Declaration", "Index", "List of Figures", "List of Tables", "Writing Allocation", "Abstract",
            "1. Introduction", "2. Problem Statement and Objectives", "3. Literature and Industry Review",
            "4. Novelty", "5. Syllabus Mapping and Theory", "6. System Design", "7. Methodology and Algorithms",
            "8. Simulation Setup", "9. Results and Analysis", "10. Contribution", "11. Co-learning Reflection",
            "12. Conclusion and Future Scope", "References", "Appendix: Links and Logs"]
heads = []
for r in required:
    m = heading_pages(r)
    heads.append(m[0] if m else -1)
missing = [r for r, h in zip(required, heads) if h < 0]
order_ok = all(a <= b for a, b in zip(heads, heads[1:])) and not missing
check("All sections present, in the required order (Novelty and Contribution mandatory)", order_ok,
      "missing: " + ", ".join(missing) if missing else "")

# ---------------------------------------------------------------- abstract
abs_page = next(t for t in pages[1:body_start] if re.search(r"^Abstract\s*$", t, re.M))
abs_text = abs_page.split("Abstract", 1)[1].split("Keywords:")[0]
abs_text = re.sub(r"^\s*[ivx]+\s*$", "", abs_text, flags=re.M)
words = len(abs_text.split())
check("Abstract 150-200 words", 150 <= words <= 200, f"{words} words")

# ---------------------------------------------------------------- figures, tables, mentions
body = "\n".join(pages[body_start:])
refs_idx = body.find("\nReferences\n")
body_text = body[:refs_idx]
caption_re = re.compile(r"^(Figure|Table) (\d+): ", re.M)
captions = caption_re.findall(body_text)
figs = sorted({int(k) for t, k in captions if t == "Figure"})
tabs = sorted({int(k) for t, k in captions if t == "Table"})
text_wo_captions = caption_re.sub("", body_text)
unref = [f"Figure {k}" for k in figs if not re.search(rf"Figure {k}\b", text_wo_captions)]
unref += [f"Table {k}" for k in tabs if not re.search(rf"Table {k}\b", text_wo_captions)]
check("Figures numbered 1..n with captions", figs == list(range(1, len(figs) + 1)), f"{len(figs)} figures")
check("Tables numbered 1..n with captions", tabs == list(range(1, len(tabs) + 1)), f"{len(tabs)} tables")
check("Every figure and table is mentioned in the text", not unref, ", ".join(unref))

# ---------------------------------------------------------------- references
ref_section = body[refs_idx:].split("Appendix: Links and Logs")[0]
ref_nums = [int(x) for x in re.findall(r"^\[(\d+)\]", ref_section, re.M)]
check("At least 8 references, numbered [1]..[n]", len(ref_nums) >= 8 and ref_nums == list(range(1, len(ref_nums) + 1)),
      f"{len(ref_nums)} references")
cited_seq = []
for m in re.finditer(r"\[(\d+)\](?:, \[(\d+)\])*", body_text):
    for x in re.findall(r"\[(\d+)\]", m.group(0)):
        cited_seq.append(int(x))
first = []
for c in cited_seq:
    if c not in first:
        first.append(c)
uncited = [k for k in ref_nums if k not in first]
check("Every reference is cited in the text", not uncited, "uncited: " + str(uncited) if uncited else "")
check("References numbered in order of first citation", first == sorted(first), str(first[:12]) + "...")

# ---------------------------------------------------------------- index page numbers
index_text = "\n".join(pages[2:body_start])
problems = []
for name in required[6:]:
    m = re.search(re.escape(name) + r"\s*\.{3,}\s*([0-9ivx]+)", index_text)
    actual = next(iter(heading_pages(name)), None)
    if not m or actual is None:
        problems.append(f"{name}: not found")
    elif m.group(1) != str(actual - body_start + 1):
        problems.append(f"{name}: index {m.group(1)} vs actual {actual - body_start + 1}")
check("Index page numbers match the real pages", not problems, "; ".join(problems[:4]))

# ---------------------------------------------------------------- leftovers
leftover = re.findall(r"\[Sample[^\]]*\]|Student Name \d|Lorem ipsum|TODO|\[Mandatory[^\]]*\]|\[Write[^\]]*\]", full)
check("No leftover sample / instruction text", not leftover, "; ".join(sorted(set(leftover))[:5]))
ph = re.findall(r"<[^<>\n]{2,40}>", full)
counts = {}
for x in ph:
    counts[x] = counts.get(x, 0) + 1
check("Placeholders to fill before submission", not ph,
      ", ".join(f"{k} x{v}" for k, v in sorted(counts.items())), warn=True)
refl = len(re.findall(r"\[What I learned on my own", full))
check("Co-learning reflections written by members", refl == 0,
      f"{refl} template paragraphs still to be replaced", warn=True)
check("Signatures (Declaration, Contribution) are blank for hand-signing", True, "sign the printed copy")

print()
fails = results.count("FAIL")
print(f"Summary: {results.count('PASS')} PASS, {results.count('WARN')} WARN, {fails} FAIL")
sys.exit(1 if fails else 0)
