"""Build resume/resume.pdf and resume/resume.md from data/profile.json + data/projects.json."""
import json
from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import HRFlowable, Paragraph, SimpleDocTemplate, Spacer

profile = json.loads(Path("data/profile.json").read_text(encoding="utf-8"))
projects = json.loads(Path("data/projects.json").read_text(encoding="utf-8"))
Path("resume").mkdir(exist_ok=True)

# ---------- Markdown ----------
md = [f"# {profile['name']}", f"**{profile['title']}**", ""]
md.append(" | ".join([profile["location"], profile["email"]] + [f"[{k}]({v})" for k, v in profile["links"].items()]))
md += ["", "## Summary", profile["summary"], "", "## Projects"]
for p in projects:
    links = f"[Code]({p['url']})" + (f" | [Demo]({p['demo']})" if p["demo"] else "")
    tech = ", ".join(filter(None, [p["language"]] + p["topics"]))
    md.append(f"- **{p['title']}** - {p['description']} ({tech}) {links}")
md += ["", "## Skills"] + [f"- **{k}:** {', '.join(v)}" for k, v in profile["skills"].items()]
md += ["", "## Education"] + [f"- **{e['school']}** - {e['degree']} ({e['period']})" for e in profile["education"]]
if profile.get("certifications"):
    md += ["", "## Certifications"] + [f"- {c}" for c in profile["certifications"]]
Path("resume/resume.md").write_text("\n".join(md) + "\n", encoding="utf-8")

# ---------- PDF ----------
ss = getSampleStyleSheet()
name_s = ParagraphStyle("name", parent=ss["Title"], fontSize=20, leading=24, alignment=0, spaceAfter=2)
sub_s = ParagraphStyle("sub", parent=ss["Normal"], fontSize=11, textColor=colors.HexColor("#333333"))
small = ParagraphStyle("small", parent=ss["Normal"], fontSize=9, textColor=colors.HexColor("#555555"))
h_s = ParagraphStyle("h", parent=ss["Heading2"], fontSize=12, spaceBefore=10, spaceAfter=2,
                     textColor=colors.HexColor("#1a3a5c"))
body = ParagraphStyle("body", parent=ss["Normal"], fontSize=9.5, leading=13)
bullet = ParagraphStyle("bullet", parent=body, leftIndent=10, bulletIndent=0, spaceAfter=3)

e = escape
story = [Paragraph(e(profile["name"]), name_s), Paragraph(e(profile["title"]), sub_s)]
contact = " | ".join([e(profile["location"]), e(profile["email"])] +
                     [f'<a href="{e(v)}" color="#1a3a5c">{e(k)}</a>' for k, v in profile["links"].items()])
story += [Spacer(1, 3), Paragraph(contact, small)]


def section(title):
    story.extend([Paragraph(title, h_s), HRFlowable(width="100%", thickness=0.6, color=colors.HexColor("#1a3a5c")),
                  Spacer(1, 3)])


section("Summary")
story.append(Paragraph(e(profile["summary"]), body))

section("Projects")
for p in projects:
    tech = ", ".join(filter(None, [p["language"]] + p["topics"]))
    links = f'<a href="{e(p["url"])}" color="#1a3a5c">GitHub</a>'
    if p["demo"]:
        links += f' | <a href="{e(p["demo"])}" color="#1a3a5c">Live demo</a>'
    text = f"<b>{e(p['title'])}</b> - {e(p['description'])}"
    if tech:
        text += f" <i>({e(tech)})</i>"
    story.append(Paragraph(f"{text} [{links}]", bullet, bulletText="\u2022"))

section("Skills")
for k, v in profile["skills"].items():
    story.append(Paragraph(f"<b>{e(k)}:</b> {e(', '.join(v))}", bullet, bulletText="\u2022"))

section("Education")
for ed in profile["education"]:
    story.append(Paragraph(f"<b>{e(ed['school'])}</b><br/>{e(ed['degree'])} ({e(ed['period'])})", body))

if profile.get("certifications"):
    section("Certifications")
    for c in profile["certifications"]:
        story.append(Paragraph(e(c), bullet, bulletText="\u2022"))

SimpleDocTemplate("resume/resume.pdf", pagesize=A4, leftMargin=18 * mm, rightMargin=18 * mm,
                  topMargin=15 * mm, bottomMargin=15 * mm, title=f"{profile['name']} - Resume",
                  author=profile["name"]).build(story)
print("resume built with", len(projects), "projects")
