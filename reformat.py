import re, os

BASE = r"d:\DESKTOP\Mini Projrct"
SRC  = os.path.join(BASE, "output.tex")
DST  = os.path.join(BASE, "LASA_Report.tex")

with open(SRC, "r", encoding="utf-8") as f:
    raw = f.read()

# ─── Extract body between \begin{document} and \end{document} ───────────────
body_match = re.search(r"\\begin\{document\}(.*?)\\end\{document\}", raw, re.DOTALL)
body = body_match.group(1).strip() if body_match else ""

# ─── Clean up body: remove ---/---  separators ───────────────────────────────
body = re.sub(r"-\\/--.*", "", body)

# ─── Chapter-level transforms ────────────────────────────────────────────────
# \section{CHAPTER N: TITLE} → \chapter{TITLE}
body = re.sub(
    r"\\section\{CHAPTER\s+\d+[:\s]+([^}]+)\}\\label\{[^}]*\}",
    lambda m: r"\chapter{" + m.group(1).strip().title() + r"}",
    body
)
# \section{CHAPTER N: TITLE} without label
body = re.sub(
    r"\\section\{CHAPTER\s+\d+[:\s]+([^}]+)\}",
    lambda m: r"\chapter{" + m.group(1).strip().title() + r"}",
    body
)

# ─── Section-level: \subsubsection{N.M Title} → \section{Title} ─────────────
body = re.sub(
    r"\\subsubsection\{(\d+\.\d+)\s+([^}]+)\}\\label\{[^}]*\}",
    lambda m: r"\section{" + m.group(1) + " " + m.group(2).strip() + r"}",
    body
)
body = re.sub(
    r"\\subsubsection\{(\d+\.\d+)\s+([^}]+)\}",
    lambda m: r"\section{" + m.group(1) + " " + m.group(2).strip() + r"}",
    body
)
# Remaining \subsubsection → \subsection
body = re.sub(r"\\subsubsection\{", r"\\subsection{", body)

# ─── Fix List of Figures / Tables / Abbreviations sections ───────────────────
body = re.sub(
    r"\\section\{List of Tables\}\\label\{[^}]*\}.*?-\\\/-\\\/- *",
    "", body, flags=re.DOTALL
)
body = re.sub(
    r"\\section\{List of Figures\}\\label\{[^}]*\}.*?-\\\/-\\\/- *",
    "", body, flags=re.DOTALL
)
body = re.sub(
    r"\\section\{Abbreviations\}\\label\{[^}]*\}(.*?)-\\\/-\\\/- *",
    lambda m: "%%ABBREV%%" + m.group(1) + "%%ABBREVEND%%",
    body, flags=re.DOTALL
)

# ─── Extract abbreviation content ────────────────────────────────────────────
abbrev_content = ""
abbrev_match = re.search(r"%%ABBREV%%(.*?)%%ABBREVEND%%", body, re.DOTALL)
if abbrev_match:
    abbrev_content = abbrev_match.group(1).strip()
    body = body.replace(abbrev_match.group(0), "")

# ─── Remove old \pagenumbering commands from body (we handle them ourselves) ──
body = body.replace(r"\pagenumbering{roman}", "")
body = body.replace(r"\pagenumbering{arabic}", "")
body = body.replace(r"\setcounter{page}{1}", "")
body = re.sub(r"\\newpage\s*", lambda m: "\n\\clearpage\n", body)
body = re.sub(r"\\renewcommand\{\\contentsname\}.*?\}", "", body)
body = body.replace(r"\setcounter{tocdepth}{3}", "")
body = re.sub(r"\{\s*\\tableofcontents\s*\}", r"\tableofcontents", body)

# ─── Fix TOC / LOF / LOT ─────────────────────────────────────────────────────
body = re.sub(r"\\tableofcontents", "%%TOC%%", body)

# Fix abstract/acknowledgement headings
body = re.sub(r"\\section\*\{\\centering\s*\\huge\s*\\bfseries\s*CERTIFICATE\}", "%%CERT%%", body)
body = re.sub(r"\\section\*\{\\centering\s*\\huge\s*\\bfseries\s*DECLARATION\}", "%%DECL%%", body)
body = re.sub(r"\\section\*\{\\huge\s*\\bfseries\s*Abstract\}", "%%ABST%%", body)
body = re.sub(r"\\section\*\{\\huge\s*\\bfseries\s*Acknowledgements?\s*\}", "%%ACKN%%", body)
body = re.sub(r"\\addcontentsline\{toc\}\{section\}\{[^}]+\}", "", body)

# ─── Build abbreviation table ────────────────────────────────────────────────
# Convert \textbf{XX:} text\\ lines to longtable rows
def build_abbrev_table(raw_abbrev):
    rows = re.findall(r"\\textbf\{([^:}]+):\}\s*([^\\\n]+)", raw_abbrev)
    lines = [r"  \textbf{" + k.strip() + r"} & " + v.strip() + r" \\[3pt]" for k, v in rows]
    table = (
        r"\begin{longtable}{>{\bfseries}p{3cm} p{10.5cm}}" + "\n"
        r"\toprule" + "\n"
        r"\textbf{Abbreviation} & \textbf{Full Form} \\" + "\n"
        r"\midrule" + "\n"
        r"\endhead" + "\n"
    )
    table += "\n".join(lines) + "\n"
    table += r"\bottomrule" + "\n" + r"\end{longtable}"
    return table

abbrev_table = build_abbrev_table(abbrev_content) if abbrev_content else ""

# ─── Build the full document ──────────────────────────────────────────────────
PREAMBLE = r"""\documentclass[12pt,a4paper]{report}

%─────────────────────────── PACKAGES ──────────────────────────────────────
\usepackage{newtxtext,newtxmath}
\usepackage[a4paper, margin=1in, top=1in, bottom=1in]{geometry}
\usepackage{setspace}
\onehalfspacing
\usepackage{graphicx}
\usepackage{float}
\usepackage{amsmath}
\usepackage{booktabs}
\usepackage{array}
\usepackage{longtable}
\usepackage{multirow}
\usepackage{xcolor}
\usepackage{hyperref}
\usepackage{fancyhdr}
\usepackage{titlesec}
\usepackage{tocloft}
\usepackage{enumitem}
\usepackage{caption}
\usepackage{microtype}
\usepackage{parskip}
\usepackage{emptypage}
\usepackage{ragged2e}

\setlength{\headheight}{14pt}

\hypersetup{
    colorlinks=true,
    linkcolor=black,
    citecolor=black,
    urlcolor=blue,
    pdftitle={AI-Based Detection of Confusable Drug Names for LASA Error Prevention},
    pdfauthor={Saptarshi Sadhu et al.},
}

%─────────────────────────── PAGE STYLE ─────────────────────────────────────
\pagestyle{fancy}
\fancyhf{}
\fancyhead[L]{\small\nouppercase{\leftmark}}
\fancyhead[R]{\small\thepage}
\fancyfoot{}
\renewcommand{\headrulewidth}{0.4pt}
\renewcommand{\footrulewidth}{0pt}

\fancypagestyle{plain}{%
  \fancyhf{}
  \fancyfoot[C]{\thepage}
  \renewcommand{\headrulewidth}{0pt}
  \renewcommand{\footrulewidth}{0pt}
}

%─────────────────────────── CHAPTER FORMAT ──────────────────────────────────
\titleformat{\chapter}[display]
  {\normalfont\Large\bfseries\centering}
  {CHAPTER \thechapter}{10pt}{\Large\bfseries\centering}
\titlespacing*{\chapter}{0pt}{-10pt}{28pt}

\titleformat{\section}{\normalfont\large\bfseries}{\thesection}{1em}{}
\titleformat{\subsection}{\normalfont\normalsize\bfseries}{\thesubsection}{1em}{}
\titleformat{\subsubsection}{\normalfont\normalsize\bfseries\itshape}{\thesubsubsection}{1em}{}

%─────────────────────────── TOC SPACING ─────────────────────────────────────
\setlength{\cftbeforechapskip}{5pt}
\renewcommand{\cftchapfont}{\bfseries}
\renewcommand{\cftchappagefont}{\bfseries}

\captionsetup{font=small, labelfont=bf, margin=10pt}
"""

TITLE_PAGE = r"""
%═══════════════════════════════════════════════════════════════════════════
%                            TITLE PAGE
%═══════════════════════════════════════════════════════════════════════════
\begin{titlepage}
\thispagestyle{empty}
\begin{center}

\vspace{10pt}
\hrule height 0.8pt
\vspace{8pt}

{\Large\textbf{ADAMAS UNIVERSITY}}\\[3pt]
{\normalsize Barasat, Kolkata -- 700126, West Bengal, India}\\[3pt]
{\normalsize Department of Computer Science and Engineering}\\[3pt]
{\normalsize Specialization in Artificial Intelligence and Machine Learning}

\vspace{8pt}
\hrule height 0.8pt
\vspace{22pt}

{\LARGE\textbf{AI-BASED DETECTION OF CONFUSABLE DRUG}}\\[8pt]
{\LARGE\textbf{NAMES FOR LOOK-ALIKE SOUND-ALIKE}}\\[8pt]
{\LARGE\textbf{(LASA) ERROR PREVENTION}}

\vspace{16pt}

{\large A Project Report Submitted for \textit{Mini Project}}\\[4pt]
{\large of}\\[4pt]
{\large\textbf{Bachelor of Technology in Computer Science and Engineering}}

\vspace{22pt}

{\large\textbf{Submitted by}}

\vspace{10pt}
\begin{tabular}{@{\hspace{1cm}}r@{\quad}l@{\quad -- \quad}l@{}}
  1. & Saptarshi Sadhu   & Roll No.~UG/SOET/30/24/288 \\[5pt]
  2. & Shubhajit Mandal  & Roll No.~UG/SOET/30/24/337 \\[5pt]
  3. & Debargha Brahma   & Roll No.~UG/SOET/30/24/293 \\[5pt]
  4. & Samrat Patra      & Roll No.~UG/SOET/30/24/218 \\[5pt]
\end{tabular}

\vspace{18pt}

{\large\textbf{Under the Guidance of}}

\vspace{8pt}
{\large\textbf{Dr. Jhilam Mukherjee}}\\[3pt]
{\normalsize Assistant Professor, Department of Computer Science and Engineering}\\[2pt]
{\normalsize Adamas University, Kolkata}

\vfill

\hrule height 0.6pt
\vspace{8pt}
{\normalsize Department of Computer Science \& Engineering \enspace$\bullet$\enspace Adamas University \enspace$\bullet$\enspace March 2026}

\end{center}
\end{titlepage}
"""

CERT_HEADING  = "\n\\clearpage\n\\thispagestyle{plain}\n\\begin{center}\n  {\\Large\\textbf{CERTIFICATE}}\n\\end{center}\n\\vspace{16pt}\n"
DECL_HEADING  = "\n\\clearpage\n\\thispagestyle{plain}\n\\begin{center}\n  {\\Large\\textbf{DECLARATION}}\n\\end{center}\n\\vspace{16pt}\n"
ABST_HEADING  = "\n\\clearpage\n\\thispagestyle{plain}\n\\begin{center}\n  {\\Large\\textbf{ABSTRACT}}\n\\end{center}\n\\vspace{16pt}\n"
ACKN_HEADING  = "\n\\clearpage\n\\thispagestyle{plain}\n\\begin{center}\n  {\\Large\\textbf{ACKNOWLEDGEMENT}}\n\\end{center}\n\\vspace{16pt}\n"

body = body.replace("%%CERT%%", CERT_HEADING)
body = body.replace("%%DECL%%", DECL_HEADING)
body = body.replace("%%ABST%%", ABST_HEADING)
body = body.replace("%%ACKN%%", ACKN_HEADING)

# Fix Declaration signature block — replace clunky blocks with a clean table
decl_sig_old = re.search(
    r"(\\textbf\{Signature:\}.*?\\vspace\{0\.5cm\}\s*)+",
    body, re.DOTALL
)
if decl_sig_old:
    new_sig = (
        "\\noindent\\textbf{Signatures of Candidates:}\n\n"
        "\\vspace{16pt}\n"
        "\\noindent\\begin{tabular}{@{\\hspace{0.5cm}}r@{\\quad}l@{\\qquad}l}\n"
        "  1. & Saptarshi Sadhu  (UG/SOET/30/24/288) & \\rule{5cm}{0.4pt} \\\\[12pt]\n"
        "  2. & Shubhajit Mandal (UG/SOET/30/24/337) & \\rule{5cm}{0.4pt} \\\\[12pt]\n"
        "  3. & Debargha Brahma  (UG/SOET/30/24/293) & \\rule{5cm}{0.4pt} \\\\[12pt]\n"
        "  4. & Samrat Patra     (UG/SOET/30/24/218) & \\rule{5cm}{0.4pt} \\\\\n"
        "\\end{tabular}\n"
    )
    body = body[:decl_sig_old.start()] + new_sig + body[decl_sig_old.end():]

# Fix certificate signature block
cert_sig_old = re.search(
    r"\\begin\{flushright\}.*?\\end\{flushright\}",
    body, re.DOTALL
)
if cert_sig_old:
    new_cert_sig = (
        "\n\\vspace{36pt}\n"
        "\\noindent\\begin{tabular}{p{7.5cm}p{6cm}}\n"
        "  \\textbf{Signature of Supervisor} & \\textbf{Signature of Head of Department} \\\\[28pt]\n"
        "  \\rule{5.5cm}{0.4pt} & \\rule{5.5cm}{0.4pt}\\\\[4pt]\n"
        "  \\textbf{Dr.\\ Jhilam Mukherjee} & \\textbf{Head of Department}\\\\\n"
        "  Assistant Professor & Department of CSE\\\\\n"
        "  Department of CSE & Adamas University\\\\\n"
        "  Adamas University & \\\\\n"
        "\\end{tabular}\n"
    )
    body = body[:cert_sig_old.start()] + new_cert_sig + body[cert_sig_old.end():]

# Remove vspace{7.5cm} and clean cert date/place
body = re.sub(r"\\vspace\{7\.5cm\}", r"\\vspace{1.5cm}", body)
body = re.sub(r"\\textbf\{Date:\}\s*13/03/2026", r"\\noindent\\textbf{Place:} Kolkata \\hspace{2cm} \\textbf{Date:} 13 March 2026", body)
body = re.sub(r"\\textbf\{Place:\}\s*\\textit\{Kolkata\}", "", body)

# Fix excessive backslashes in cert body
body = re.sub(r"(\\\\)+\s*\\begin\{flushright\}", "\n", body)

# TOC replacement
toc_block = (
    "\n\\clearpage\n\\tableofcontents\n\n"
    "\\clearpage\n\\listoffigures\n\n"
    "\\clearpage\n\\listoftables\n"
)
if abbrev_table:
    toc_block += (
        "\n\\clearpage\n\\thispagestyle{plain}\n"
        "\\begin{center}\n  {\\Large\\textbf{LIST OF ABBREVIATIONS}}\n\\end{center}\n"
        "\\vspace{16pt}\n\n" + abbrev_table + "\n"
    )
body = body.replace("%%TOC%%", toc_block)

# Arabic numbering start just before Chapter 1
body = re.sub(
    r"(\\chapter\{Introduction[^}]*\})",
    lambda m: "\n\\clearpage\n\\pagenumbering{arabic}\n\\setcounter{page}{1}\n\n" + m.group(1),
    body
)

# Fix tightlist / itemize spacing
body = body.replace(r"\tightlist", r"\setlength{\itemsep}{4pt}\setlength{\parskip}{0pt}")

# Clean up multiple blank lines
body = re.sub(r"\n{3,}", "\n\n", body)

# Fix figure/table placeholders — wrap in figure environment if bare
def wrap_figure_placeholder(m):
    label = m.group(1).strip()
    desc  = m.group(2).strip() if m.group(2) else ""
    fignum = re.search(r"Figure\s+([\d.]+)", label)
    figref = ("fig:" + fignum.group(1).replace(".", "_")) if fignum else "fig:placeholder"
    return (
        "\n\\begin{figure}[H]\n\\centering\n"
        "\\fbox{\\parbox{0.85\\linewidth}{\\centering\\vspace{20pt}"
        "{\\small\\textit{[" + label + "]}}\\\\[6pt]"
        "{\\footnotesize " + desc + "}\\vspace{20pt}}}\n"
        "\\caption{" + label + "}\n"
        "\\label{" + figref + "}\n"
        "\\end{figure}\n"
    )

body = re.sub(
    r"\\textbf\{\[Figure\s+([\d.]+:[^\]]+)\]\}\\\\\\s*\\emph\{Description:\}\s*([^\n]+(?:\n(?!\n)[^\n]+)*)",
    wrap_figure_placeholder,
    body
)

# Fix table placeholders
def wrap_table_placeholder(m):
    label = m.group(1).strip()
    tabnum = re.search(r"Table\s+([\d.]+)", label)
    tabref = ("tab:" + tabnum.group(1).replace(".", "_")) if tabnum else "tab:placeholder"
    return (
        "\n\\begin{table}[H]\n\\centering\n"
        "\\caption{" + re.sub(r"^Table\s+[\d.]+:\s*", "", label) + "}\n"
        "\\label{" + tabref + "}\n"
        "\\begin{tabular}{ll}\\toprule\n"
        "\\multicolumn{2}{c}{\\textit{[Data not yet available]}} \\\\\n"
        "\\bottomrule\n\\end{tabular}\n"
        "\\end{table}\n"
    )

body = re.sub(
    r"\\textbf\{\[Table\s+([\d.]+:[^\]]+)\]\}",
    wrap_table_placeholder,
    body
)

# ─── Assemble final document ──────────────────────────────────────────────────
doc = (
    PREAMBLE
    + "\n%═══════════════════════════════════════════════════════════════════════════\n"
    + "\\begin{document}\n\n"
    + "\\pagenumbering{roman}\n\n"
    + TITLE_PAGE
    + "\n"
    + body.strip()
    + "\n\n\\end{document}\n"
)

with open(DST, "w", encoding="utf-8") as f:
    f.write(doc)

print(f"Done. Written to: {DST}")
print(f"Lines: {doc.count(chr(10))}")
