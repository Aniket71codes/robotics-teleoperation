"""Build the project report as Word (.docx) and PDF in the sample report's format.

    python report/build_report.py        -> report/AISR_Project_Report.docx and .pdf

Format (from AISR_Sample_Project_Report.pdf and the Project Instructions):
A4 portrait; margins left 3.0 cm, others 2.5 cm; single-line border on every
page incl. the title page; Times New Roman; body 12 pt, 1.5 spacing,
justified; headings 14 pt bold, sub-headings 12 pt bold; page numbers bottom
centre except on the title page, Roman for front pages and Arabic from
Section 1; Index, List of Figures and List of Tables with real page numbers.

Page numbers are found by converting to PDF with LibreOffice, reading the PDF
with PyMuPDF and rebuilding until the numbers are stable (usually 2 passes).
"""

from __future__ import annotations

import io
import os
import re
import shutil
import subprocess
import sys
import tempfile

import fitz  # PyMuPDF
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from docx import Document  # noqa: E402
from docx.enum.section import WD_SECTION  # noqa: E402
from docx.enum.table import WD_TABLE_ALIGNMENT  # noqa: E402
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK, WD_LINE_SPACING, WD_TAB_ALIGNMENT, WD_TAB_LEADER  # noqa: E402
from docx.oxml import OxmlElement  # noqa: E402
from docx.oxml.ns import qn  # noqa: E402
from docx.shared import Cm, Pt  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import content as C  # noqa: E402

OUT_DOCX = os.path.join(HERE, "AISR_Project_Report.docx")
OUT_PDF = os.path.join(HERE, "AISR_Project_Report.pdf")
LOGO = os.path.join(HERE, "upes_logo.png")
FONT = "Times New Roman"
MONO = "Courier New"
TEXT_W = 21.0 - 3.0 - 2.5        # cm
SMALL = 10.5                     # pt, tables and captions (as in the sample)

FRONT_ITEMS = ["Declaration", "List of Figures", "List of Tables", "Writing Allocation", "Abstract"]


# ======================================================================= numbering pre-pass
class Numbers:
    """Figure/table/equation numbers in order of appearance; references in order of first citation."""

    def __init__(self, body):
        self.fig, self.tab, self.eq, self.ref = {}, {}, {}, {}
        self.fig_list, self.tab_list = [], []
        for b in body:
            kind = b[0]
            texts = []
            if kind == "fig":
                self.fig[b[1]] = len(self.fig) + 1
                self.fig_list.append((b[1], b[3]))
            elif kind == "table":
                self.tab[b[1]] = len(self.tab) + 1
                self.tab_list.append((b[1], b[2]))
                texts = [c for row in b[4] for c in row]
            elif kind == "eq":
                self.eq[b[1]] = len(self.eq) + 1
            if kind in ("p", "h1", "h2"):
                texts = [b[1]]
            elif kind in ("bullets", "numbered"):
                texts = b[1]
            for t in texts:
                for m in re.finditer(r"\{cite:([^}]+)\}", t):
                    for k in m.group(1).split(","):
                        k = k.strip()
                        if k not in C.REFS:
                            raise KeyError(f"unknown reference key {k}")
                        self.ref.setdefault(k, len(self.ref) + 1)
        missing = [k for k in C.REFS if k not in self.ref]
        if missing:
            raise ValueError(f"references never cited: {missing}")

    def expand(self, text: str) -> str:
        def cite(m):
            return ", ".join(f"[{self.ref[k.strip()]}]" for k in m.group(1).split(","))
        text = re.sub(r"\{cite:([^}]+)\}", cite, text)
        text = re.sub(r"\{fig:([^}]+)\}", lambda m: f"Figure {self.fig[m.group(1)]}", text)
        text = re.sub(r"\{tab:([^}]+)\}", lambda m: f"Table {self.tab[m.group(1)]}", text)
        text = re.sub(r"\{eq:([^}]+)\}", lambda m: f"({self.eq[m.group(1)]})", text)
        return text


# ======================================================================= low-level docx helpers
def set_run_font(run, size=None, bold=None, italic=None, name=FONT):
    run.font.name = name
    rpr = run._element.get_or_add_rPr()
    rfonts = rpr.find(qn("w:rFonts"))
    if rfonts is None:
        rfonts = OxmlElement("w:rFonts")
        rpr.insert(0, rfonts)
    for a in ("w:ascii", "w:hAnsi", "w:cs", "w:eastAsia"):
        rfonts.set(qn(a), name)
    if size is not None:
        run.font.size = Pt(size)
    if bold is not None:
        run.font.bold = bold
    if italic is not None:
        run.font.italic = italic


def style_font(style, size, bold=False):
    style.font.name = FONT
    style.font.size = Pt(size)
    style.font.bold = bold
    style.font.color.rgb = None
    rpr = style.element.get_or_add_rPr()
    rfonts = rpr.find(qn("w:rFonts"))
    if rfonts is None:
        rfonts = OxmlElement("w:rFonts")
        rpr.insert(0, rfonts)
    for a in list(rfonts.attrib):
        del rfonts.attrib[a]
    for a in ("w:ascii", "w:hAnsi", "w:cs", "w:eastAsia"):
        rfonts.set(qn(a), FONT)
    color = rpr.find(qn("w:color"))
    if color is not None:
        rpr.remove(color)


def para_format(p, align=WD_ALIGN_PARAGRAPH.JUSTIFY, before=0, after=6, spacing=1.5, keep_next=False,
                indent=None):
    pf = p.paragraph_format
    pf.alignment = align
    pf.space_before = Pt(before)
    pf.space_after = Pt(after)
    pf.line_spacing = spacing
    pf.keep_with_next = keep_next
    if indent is not None:
        pf.left_indent = Cm(indent)
    return p


def add_text_runs(p, text, size=12, bold=False, italic=False):
    """Add text with **bold** markup as runs."""
    parts = re.split(r"(\*\*[^*]+\*\*)", text)
    for part in parts:
        if not part:
            continue
        if part.startswith("**") and part.endswith("**"):
            set_run_font(p.add_run(part[2:-2]), size, True, italic)
        else:
            set_run_font(p.add_run(part), size, bold, italic)


def add_field(run, instr):
    """Insert a Word field (e.g. PAGE) into a run."""
    for tag, attr in (("w:fldChar", {"w:fldCharType": "begin"}), ("w:instrText", None),
                      ("w:fldChar", {"w:fldCharType": "separate"}), ("w:t", None),
                      ("w:fldChar", {"w:fldCharType": "end"})):
        el = OxmlElement(tag)
        if attr:
            for k, v in attr.items():
                el.set(qn(k), v)
        if tag == "w:instrText":
            el.set(qn("xml:space"), "preserve")
            el.text = f" {instr} "
        if tag == "w:t":
            el.text = "1"
        run._element.append(el)


def setup_section(section, page_fmt=None, start=None, footer=True):
    section.page_width, section.page_height = Cm(21.0), Cm(29.7)
    section.left_margin = Cm(3.0)
    section.right_margin = Cm(2.5)
    section.top_margin = Cm(2.5)
    section.bottom_margin = Cm(2.5)
    section.footer_distance = Cm(1.25)
    section.header_distance = Cm(1.25)
    sp = section._sectPr
    for tag in ("w:pgBorders", "w:pgNumType"):
        for el in sp.findall(qn(tag)):
            sp.remove(el)
    # page border: single line on all four sides, measured from the page edge
    borders = OxmlElement("w:pgBorders")
    borders.set(qn("w:offsetFrom"), "page")
    for side in ("top", "left", "bottom", "right"):
        b = OxmlElement(f"w:{side}")
        b.set(qn("w:val"), "single")
        b.set(qn("w:sz"), "6")
        b.set(qn("w:space"), "24")
        b.set(qn("w:color"), "000000")
        borders.append(b)
    pgmar = sp.find(qn("w:pgMar"))
    pgmar.addnext(borders)
    if page_fmt:
        num = OxmlElement("w:pgNumType")
        num.set(qn("w:fmt"), page_fmt)
        if start is not None:
            num.set(qn("w:start"), str(start))
        borders.addnext(num)
    section.footer.is_linked_to_previous = False
    section.header.is_linked_to_previous = False
    f = section.footer
    for p in f.paragraphs:
        p.text = ""
    if footer:
        p = f.paragraphs[0]
        para_format(p, WD_ALIGN_PARAGRAPH.CENTER, 0, 0, 1.0)
        r = p.add_run()
        set_run_font(r, 12)
        add_field(r, "PAGE")


def page_break(doc):
    p = doc.add_paragraph()
    para_format(p, after=0, spacing=1.0)
    p.add_run().add_break(WD_BREAK.PAGE)


def heading(doc, text, level=1, front=False):
    p = doc.add_paragraph(style="Heading 1" if level == 1 else "Heading 2")
    para_format(p, WD_ALIGN_PARAGRAPH.LEFT, before=(0 if front else (12 if level == 1 else 8)),
                after=6, spacing=1.15, keep_next=True)
    set_run_font(p.add_run(text), 14 if level == 1 else 12, True)
    return p


def table(doc, header, rows, widths, numbers, font=SMALL, header_bold=True, align_first_left=True,
          row_height=None):
    t = doc.add_table(rows=1, cols=len(header))
    t.style = "Table Grid"
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    t.autofit = False

    def fill(cell, text, bold, center):
        cell.text = ""
        p = cell.paragraphs[0]
        para_format(p, WD_ALIGN_PARAGRAPH.CENTER if center else WD_ALIGN_PARAGRAPH.LEFT, 1, 1, 1.0)
        add_text_runs(p, numbers.expand(text) if numbers else text, font, bold)

    for i, h in enumerate(header):
        fill(t.rows[0].cells[i], h, header_bold, True)
    for row in rows:
        cells = t.add_row().cells
        for i, v in enumerate(row):
            fill(cells[i], str(v), False, not (i == 0 and align_first_left) and len(str(v)) < 22)
    for row in t.rows:
        if row_height:
            row.height = Cm(row_height)
        for i, w in enumerate(widths):
            row.cells[i].width = Cm(w)
    fix_table_widths(t, widths)
    # keep short tables on one page: every row "keeps with next", except the last
    if len(t.rows) <= 16:
        for row in t.rows[:-1]:
            for cell in row.cells:
                for cp in cell.paragraphs:
                    cp.paragraph_format.keep_with_next = True
    # repeat header row on page breaks
    trpr = t.rows[0]._tr.get_or_add_trPr()
    h = OxmlElement("w:tblHeader")
    h.set(qn("w:val"), "true")
    trpr.append(h)
    return t


def fix_table_widths(t, widths):
    """LibreOffice ignores per-cell widths unless the grid and a fixed layout say the same."""
    tbl = t._tbl
    tblPr = tbl.tblPr
    for tag in ("w:tblW", "w:tblLayout"):
        for el in tblPr.findall(qn(tag)):
            tblPr.remove(el)
    tw = OxmlElement("w:tblW")
    tw.set(qn("w:w"), str(int(sum(widths) * 567)))
    tw.set(qn("w:type"), "dxa")
    tblPr.append(tw)
    lay = OxmlElement("w:tblLayout")
    lay.set(qn("w:type"), "fixed")
    tblPr.append(lay)
    grid = tbl.tblGrid
    for gc, w in zip(grid.findall(qn("w:gridCol")), widths):
        gc.set(qn("w:w"), str(int(w * 567)))
    for row in t.rows:
        trpr = row._tr.get_or_add_trPr()
        cs = OxmlElement("w:cantSplit")
        trpr.append(cs)


_eq_cache = {}


def equation_png(latex):
    if latex in _eq_cache:
        return _eq_cache[latex]
    fig = plt.figure(figsize=(0.01, 0.01))
    fig.text(0, 0, f"${latex}$", fontsize=16, math_fontfamily="stix")
    buf = io.BytesIO()
    fig.savefig(buf, dpi=300, bbox_inches="tight", pad_inches=0.04, transparent=False, facecolor="white")
    plt.close(fig)
    buf.seek(0)
    _eq_cache[latex] = buf.getvalue()
    return _eq_cache[latex]


# ======================================================================= document parts
class Builder:
    def __init__(self, pages: dict):
        self.pages = pages              # name -> displayed page label from the previous pass
        self.N = Numbers(C.BODY)
        self.doc = Document()
        st = self.doc.styles
        style_font(st["Normal"], 12)
        st["Normal"].paragraph_format.line_spacing_rule = WD_LINE_SPACING.ONE_POINT_FIVE
        style_font(st["Heading 1"], 14, True)
        style_font(st["Heading 2"], 12, True)
        for name in ("Heading 1", "Heading 2"):
            st[name].paragraph_format.keep_with_next = True

    def pg(self, key):
        return self.pages.get(key, "00")

    # ------------------------------------------------------------------ title page
    def title_page(self):
        d = self.doc
        setup_section(d.sections[0], footer=False)

        def line(text, size=12, bold=False, before=0, after=6, spacing=1.15):
            p = d.add_paragraph()
            para_format(p, WD_ALIGN_PARAGRAPH.CENTER, before, after, spacing)
            set_run_font(p.add_run(text), size, bold)
            return p

        p = d.add_paragraph()
        para_format(p, WD_ALIGN_PARAGRAPH.CENTER, 18, 6, 1.0)
        p.add_run().add_picture(LOGO, width=Cm(8.0))
        line("School of Computer Science, UPES, Dehradun", 14, True, 6, 24)
        line("A Project Report on", 13, False, 12, 8)
        line(C.META["title"], 20, True, 4, 22, 1.15)
        line("Submitted for the course", 11, False, 0, 2)
        line("CSAI4014 Algorithms for Intelligent Systems and Robotics", 13, True, 0, 4)
        line("B.Tech CSE (AI & ML), Semester VII", 12, False, 0, 14)
        info = [("Project No.:", C.META["project_no"]), ("Group No.:", C.META["group_no"]),
                ("Batch:", C.META["batch"])]
        t = d.add_table(rows=0, cols=2)
        t.alignment = WD_TABLE_ALIGNMENT.CENTER
        for k, v in info:
            cells = t.add_row().cells
            for c, txt, b in ((cells[0], k, True), (cells[1], v, False)):
                para_format(c.paragraphs[0], WD_ALIGN_PARAGRAPH.LEFT, 0, 0, 1.0)
                set_run_font(c.paragraphs[0].add_run(txt), 12, b)
            cells[0].width, cells[1].width = Cm(3.0), Cm(4.0)
        fix_table_widths(t, [3.0, 4.0])
        line("Submitted by", 12, True, 16, 6)
        rows = [[str(i + 1), n, s] for i, (n, s) in enumerate(C.META["members"])]
        tt = table(d, ["S. No.", "Name", "SAP ID"], rows, [1.8, 7.2, 3.2], None, font=11, align_first_left=False)
        for r in tt.rows[1:]:
            r.cells[0].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
            r.cells[2].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
        line("Submitted to", 12, True, 22, 4)
        line("Course Faculty, CSAI4014", 12, False, 0, 2)
        line("School of Computer Science, UPES, Dehradun", 12, False, 0, 18)
        line("Academic Year 2026-2027   |   October 2026", 12, True, 6, 0)

    # ------------------------------------------------------------------ front matter
    def front(self):
        d = self.doc
        sec = d.add_section(WD_SECTION.NEW_PAGE)
        setup_section(sec, "lowerRoman", 1)

        # Declaration
        heading(d, "Declaration", front=True)
        p = d.add_paragraph()
        para_format(p)
        add_text_runs(p, f"We declare that this project report titled “{C.META['title']}” is our own "
                         "work, carried out for the course CSAI4014 Algorithms for Intelligent Systems and "
                         "Robotics. The code, results and text are original, and all sources used are cited in "
                         "the References. All experimental results were produced by the team's own software on "
                         "the mock simulator, as stated in the report.")
        sp = d.add_paragraph()
        para_format(sp, after=12)
        rows = [[n, s, ""] for n, s in C.META["members"]]
        table(d, ["Name", "SAP ID", "Signature"], rows, [6.0, 3.6, 4.6], None, font=11, row_height=1.15)
        p = d.add_paragraph()
        para_format(p, WD_ALIGN_PARAGRAPH.LEFT, 30, 0, 1.15)
        p.paragraph_format.tab_stops.add_tab_stop(Cm(TEXT_W), WD_TAB_ALIGNMENT.RIGHT)
        set_run_font(p.add_run("Date: ____________________\tPlace: Dehradun"), 12)
        page_break(d)

        # Index
        heading(d, "Index", front=True)
        entries = [(item, 0) for item in FRONT_ITEMS]
        for b in C.BODY:
            if b[0] == "h1":
                entries.append((b[1], 0))
            elif b[0] == "h2":
                entries.append((b[1], 1))
        entries += [("References", 0), ("Appendix: Links and Logs", 0)]
        for text, lvl in entries:
            self.toc_line(text, self.pg(text), bold=(lvl == 0), indent=0.6 if lvl else 0)
        page_break(d)

        # Lists
        heading(d, "List of Figures", front=True)
        for key, cap in self.N.fig_list:
            n = self.N.fig[key]
            self.toc_line(f"Figure {n}:  {cap}", self.pg(f"Figure {n}"), bold=False)
        p = d.add_paragraph()
        para_format(p, after=0, spacing=1.0)
        heading(d, "List of Tables", front=True)
        for key, cap in self.N.tab_list:
            n = self.N.tab[key]
            self.toc_line(f"Table {n}:  {cap}", self.pg(f"Table {n}"), bold=False)
        page_break(d)

        # Writing allocation
        heading(d, "Writing Allocation", front=True)
        alloc = [("M1", 0, "Abstract, 1, 2, References"), ("M2", 2, "3, 4"), ("M3", 3, "5, 7"),
                 ("M4", 1, "6, 8"), ("M5", 4, "9, 12, Appendix")]
        rows = []
        for m, idx, secs in alloc:
            name, sap = C.META["members"][idx]
            rows.append([m, f"{name} ({sap})", secs, self.pages.get(f"alloc:{m}", "-")])
        rows.append(["All", "Every member", "10 (own row), 11 (own reflection), Declaration", "-"])
        t = table(d, ["Member", "Name and SAP ID", "Sections written", "Pages"], rows, [2.1, 5.9, 5.2, 1.6],
                  None, font=11, align_first_left=False)
        for r in t.rows[1:]:
            r.cells[0].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
            r.cells[3].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
        p = d.add_paragraph()
        para_format(p, before=8)
        add_text_runs(p, "Pages = words written by the member (text and tables, without figures) divided by "
                         "330, the words on one page of 12 pt text at 1.5 line spacing; rounded to half pages.",
                      SMALL, italic=True)
        page_break(d)

        # Abstract
        heading(d, "Abstract", front=True)
        p = d.add_paragraph()
        para_format(p)
        add_text_runs(p, C.ABSTRACT)
        p = d.add_paragraph()
        para_format(p, before=4)
        add_text_runs(p, "**Keywords:** " + C.KEYWORDS)

    def toc_line(self, text, page, bold=False, indent=0):
        p = self.doc.add_paragraph()
        para_format(p, WD_ALIGN_PARAGRAPH.LEFT, 0, 3, 1.15, indent=indent)
        p.paragraph_format.tab_stops.add_tab_stop(Cm(TEXT_W), WD_TAB_ALIGNMENT.RIGHT, WD_TAB_LEADER.DOTS)
        set_run_font(p.add_run(f"{text}\t{page}"), 12, bold)

    # ------------------------------------------------------------------ body
    def body(self):
        d = self.doc
        sec = d.add_section(WD_SECTION.NEW_PAGE)
        setup_section(sec, "decimal", 1)
        N = self.N
        for b in C.BODY:
            k = b[0]
            if k == "h1":
                heading(d, b[1], 1)
            elif k == "h2":
                heading(d, b[1], 2)
            elif k == "p":
                p = d.add_paragraph()
                para_format(p)
                add_text_runs(p, N.expand(b[1]))
            elif k in ("bullets", "numbered"):
                for i, item in enumerate(b[1], 1):
                    p = d.add_paragraph()
                    para_format(p, after=3, indent=0.9)
                    p.paragraph_format.first_line_indent = Cm(-0.6)
                    p.paragraph_format.tab_stops.add_tab_stop(Cm(0.9))
                    add_text_runs(p, (f"{i}.\t" if k == "numbered" else "•\t") + N.expand(item))
            elif k == "fig":
                _, key, fname, cap, width = b
                p = d.add_paragraph()
                para_format(p, WD_ALIGN_PARAGRAPH.CENTER, 6, 2, 1.0, keep_next=True)
                p.add_run().add_picture(os.path.join(C.FIG, fname), width=Cm(width))
                p = d.add_paragraph()
                para_format(p, WD_ALIGN_PARAGRAPH.CENTER, 0, 10, 1.15)
                set_run_font(p.add_run(f"Figure {N.fig[key]}: "), SMALL, True)
                set_run_font(p.add_run(cap), SMALL)
            elif k == "table":
                _, key, cap, header, rows, widths = b
                p = d.add_paragraph()
                para_format(p, WD_ALIGN_PARAGRAPH.CENTER, 6, 3, 1.15, keep_next=True)
                set_run_font(p.add_run(f"Table {N.tab[key]}: "), SMALL, True)
                set_run_font(p.add_run(cap), SMALL)
                table(d, header, rows, widths, N)
                sp = d.add_paragraph()
                para_format(sp, after=0, spacing=1.0)
                set_run_font(sp.add_run(""), 6)
            elif k == "eq":
                _, key, latex = b
                p = d.add_paragraph()
                para_format(p, WD_ALIGN_PARAGRAPH.LEFT, 3, 3, 1.0)
                ts = p.paragraph_format.tab_stops
                ts.add_tab_stop(Cm(TEXT_W / 2), WD_TAB_ALIGNMENT.CENTER)
                ts.add_tab_stop(Cm(TEXT_W), WD_TAB_ALIGNMENT.RIGHT)
                png = equation_png(latex)
                set_run_font(p.add_run("\t"), 12)
                r = p.add_run()
                from PIL import Image
                w_px, h_px = Image.open(io.BytesIO(png)).size
                r.add_picture(io.BytesIO(png), width=Cm(min(w_px / 300 * 2.54, TEXT_W - 2.0)))
                set_run_font(p.add_run(f"\t({N.eq[key]})"), 12)
            elif k == "code":
                for i, line in enumerate(b[1]):
                    p = d.add_paragraph()
                    para_format(p, WD_ALIGN_PARAGRAPH.LEFT, 4 if i == 0 else 0,
                                6 if i == len(b[1]) - 1 else 0, 1.0, indent=0.4,
                                keep_next=i < len(b[1]) - 1)
                    shd = OxmlElement("w:shd")
                    shd.set(qn("w:val"), "clear")
                    shd.set(qn("w:fill"), "F2F2F2")
                    p._p.get_or_add_pPr().append(shd)
                    set_run_font(p.add_run(line if line else " "), 8.5, name=MONO)
            elif k == "contrib":
                rows = [[str(i + 1), f"{n} ({C.META['members'][i][1]})", tech, f"{secs}\n\nSignature:"]
                        for i, (n, tech, secs) in enumerate(C.CONTRIB)]
                table(d, ["S. No.", "Member name and SAP ID", "Technical contribution (modules / algorithms / "
                          "code files / experiments)", "Report sections written + signature"],
                      rows, [1.3, 3.4, 7.3, 3.0], N, align_first_left=False)
                sp = d.add_paragraph()
                para_format(sp, after=4, spacing=1.0)
            elif k == "reflections":
                for name, _ in C.META["members"]:
                    p = d.add_paragraph()
                    para_format(p, before=4, after=2, keep_next=True)
                    add_text_runs(p, f"**{name}:**")
                    p = d.add_paragraph()
                    para_format(p, after=6)
                    add_text_runs(p, "[What I learned on my own: … What I learned from team-mates: … "
                                     "What I taught others: … (5-8 lines, written by " + name.split()[0] + ")]",
                                  italic=True)
            elif k == "pagebreak":
                page_break(d)
        # references
        heading(d, "References", 1)
        for key, n in sorted(N.ref.items(), key=lambda kv: kv[1]):
            p = d.add_paragraph()
            para_format(p, WD_ALIGN_PARAGRAPH.LEFT, 0, 3, 1.0, indent=1.0)
            p.paragraph_format.first_line_indent = Cm(-1.0)
            p.paragraph_format.tab_stops.add_tab_stop(Cm(1.0))
            set_run_font(p.add_run(f"[{n}]\t{C.REFS[key]}"), 12)
        self.appendix()

    def appendix(self):
        d = self.doc
        heading(d, "Appendix: Links and Logs", 1)
        p = d.add_paragraph()
        para_format(p)
        add_text_runs(p, C.APPENDIX_INTRO)
        for label, val in (("GitHub repository:", C.META["github"]),
                           ("YouTube video (Unlisted):", C.META["youtube"])):
            p = d.add_paragraph()
            para_format(p, WD_ALIGN_PARAGRAPH.LEFT, 0, 4)
            set_run_font(p.add_run(label + " "), 12, True)
            set_run_font(p.add_run(val), 12)
        p = d.add_paragraph()
        para_format(p, WD_ALIGN_PARAGRAPH.LEFT, 10, 4, 1.15, keep_next=True)
        set_run_font(p.add_run("Meeting log"), 12, True)
        rows = [[str(i), "", "", "", ""] for i in range(1, 5)]
        table(self.doc, ["No.", "Date", "Duration", "Attendees", "Decisions"], rows, [1.2, 2.6, 2.2, 3.0, 6.0],
              None, font=11, align_first_left=False, row_height=0.8)
        p = d.add_paragraph()
        para_format(p, WD_ALIGN_PARAGRAPH.LEFT, 10, 4, 1.15, keep_next=True)
        set_run_font(p.add_run("Commit evidence"), 12, True)
        p = d.add_paragraph()
        para_format(p)
        add_text_runs(p, "Output of python scripts/git_author_stats.py (commits, files changed and lines per "
                         "author) is pasted here before printing.")
        table(self.doc, ["Author", "Commits", "Files changed", "Lines + / -"],
              [[n, "", "", ""] for n, _ in C.META["members"]], [6.0, 2.6, 3.0, 3.4], None, font=11,
              row_height=0.7)
        p = d.add_paragraph()
        para_format(p, WD_ALIGN_PARAGRAPH.LEFT, 10, 4, 1.15, keep_next=True)
        set_run_font(p.add_run("Peer-assessment sheets"), 12, True)
        p = d.add_paragraph()
        para_format(p)
        add_text_runs(p, "Each member fills in one sheet individually and attaches it here (format: Project "
                         "Instructions, Section 4; scale 1 = very poor to 5 = excellent). Assessor: "
                         "______________________   SAP ID: ____________   Signature: ____________")
        table(self.doc, ["No.", "Team-mate name and SAP ID", "Contribution (1-5)", "Reliability / on time (1-5)",
                         "Helped others learn (1-5)", "Quality of work (1-5)"],
              [[str(i), "", "", "", "", ""] for i in range(1, 5)], [1.0, 4.6, 2.3, 2.5, 2.3, 2.3], None,
              font=SMALL, align_first_left=False, row_height=0.8)

    def build(self, path):
        self.title_page()
        self.front()
        self.body()
        self.doc.core_properties.title = C.META["title"]
        self.doc.core_properties.author = "Group " + C.META["group_no"]
        self.doc.save(path)


# ======================================================================= PDF conversion and page lookup
def to_pdf(docx_path, out_dir):
    soffice = shutil.which("soffice") or shutil.which("libreoffice")
    if not soffice:
        sys.exit("LibreOffice (soffice) not found on PATH")
    with tempfile.TemporaryDirectory() as profile:
        subprocess.run([soffice, f"-env:UserInstallation=file://{profile}", "--headless", "--convert-to", "pdf",
                        "--outdir", out_dir, docx_path], check=True, capture_output=True)
    return os.path.join(out_dir, os.path.splitext(os.path.basename(docx_path))[0] + ".pdf")


def roman(n):
    vals = [(10, "x"), (9, "ix"), (5, "v"), (4, "iv"), (1, "i")]
    out = ""
    for v, s in vals:
        while n >= v:
            out += s
            n -= v
    return out


def pdf_lines(pdf_path):
    """[(page_index, text, size, bold, y0, page_height)] for every text line."""
    doc = fitz.open(pdf_path)
    out = []
    for i, page in enumerate(doc):
        for b in page.get_text("dict")["blocks"]:
            for ln in b.get("lines", []):
                spans = [s for s in ln["spans"] if s["text"].strip()]
                if not spans:
                    continue
                text = " ".join("".join(s["text"] for s in ln["spans"]).split())
                size = max(s["size"] for s in spans)
                bold = any(s["flags"] & 16 or "Bold" in s["font"] for s in spans)
                out.append((i, text, size, bold, ln["bbox"][1], page.rect.height))
    return out, len(doc)


def locate(pdf_path, N):
    lines, n_pages = pdf_lines(pdf_path)
    body_start = next(i for i, t, s, b, y, h in lines if t == "1. Introduction" and s > 13)

    def label(i):
        return roman(i) if i < body_start else str(i - body_start + 1)

    found, pos = {}, {}
    h1s = FRONT_ITEMS + [b[1] for b in C.BODY if b[0] == "h1"] + ["References", "Appendix: Links and Logs"]
    h2s = [b[1] for b in C.BODY if b[0] == "h2"]
    for i, t, s, b, y, h in lines:
        if s > 13 and t in h1s and t not in found:
            found[t], pos[t] = label(i), (i, y / h)
        elif i >= body_start and b and abs(s - 12) < 0.6 and t in h2s and t not in found:
            found[t], pos[t] = label(i), (i, y / h)
        elif i >= body_start and abs(s - SMALL) < 0.6:
            m = re.match(r"(Figure|Table) (\d+):", t)
            if m and f"{m.group(1)} {m.group(2)}" not in found:
                found[f"{m.group(1)} {m.group(2)}"] = label(i)
    # pages written per member = words written / 330 (one page of 12 pt text at 1.5 spacing)
    words, cur = {}, None
    for blk in C.BODY:
        if blk[0] == "h1":
            cur = int(blk[1].split(".")[0])
            words[cur] = 0
        if blk[0] in ("p", "h1", "h2"):
            words[cur] += len(blk[1].split())
        elif blk[0] in ("bullets", "numbered"):
            words[cur] += sum(len(x.split()) for x in blk[1])
        elif blk[0] == "table":
            words[cur] += sum(len(str(c).split()) for r in blk[4] for c in r)
        elif blk[0] == "code":
            words[cur] += sum(len(x.split()) for x in blk[1])
    refs = sum(len(v.split()) for v in C.REFS.values())
    appendix = 250
    groups = {"M1": words[1] + words[2] + refs + len(C.ABSTRACT.split()), "M2": words[3] + words[4],
              "M3": words[5] + words[7], "M4": words[6] + words[8], "M5": words[9] + words[12] + appendix}
    for m, w in groups.items():
        found[f"alloc:{m}"] = f"{round(w / 330 * 2) / 2:g}"
    found["_pages"] = n_pages
    return found


def main():
    pages = {}
    work = tempfile.mkdtemp()
    for attempt in range(4):
        b = Builder(pages)
        tmp_docx = os.path.join(work, "AISR_Project_Report.docx")
        b.build(tmp_docx)
        pdf = to_pdf(tmp_docx, work)
        new = locate(pdf, b.N)
        stable = all(pages.get(k) == v for k, v in new.items())
        print(f"pass {attempt + 1}: {new['_pages']} pages" + (" (page numbers stable)" if stable else ""))
        pages = new
        if stable:
            break
    shutil.copy(tmp_docx, OUT_DOCX)
    shutil.copy(pdf, OUT_PDF)
    print("wrote", OUT_DOCX)
    print("wrote", OUT_PDF)


if __name__ == "__main__":
    main()
