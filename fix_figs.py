import re
import os

filepath = r"d:\DESKTOP\Mini Projrct\output.tex"

with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Fix Figures (with Descriptions)
def fix_figure(m):
    # m.group(1) is the label (e.g., "Figure 3.1: System Architecture...")
    # m.group(2) is the description
    label = m.group(1).replace('\n', ' ')
    label = re.sub(r'\s+', ' ', label).strip()
    
    desc = m.group(2).replace('\n', ' ')
    desc = re.sub(r'\s+', ' ', desc).strip()
    
    # Extract numbering for the label reference
    num_match = re.search(r'Figure\s+([\d.]+)', label)
    ref = "fig:" + num_match.group(1).replace(".", "_") if num_match else "fig:placeholder"
    
    caption = label
    
    return (
        "\\begin{figure}[H]\n"
        "\\centering\n"
        "\\fbox{\\parbox{0.85\\linewidth}{\\centering\\vspace{20pt}\n"
        "{\\small\\textit{[" + label + "]}}\\\\[6pt]\n"
        "{\\footnotesize " + desc + "}\\vspace{20pt}}}\n"
        "\\caption{" + caption + "}\n"
        "\\label{" + ref + "}\n"
        "\\end{figure}"
    )

content = re.sub(
    r"\\textbf\{\{\[\}(Figure[^\]]+)\{\]\}\}\\\\\n\\emph\{Description:\}\s*(.*?)(?=\n\n|\n\\section)",
    fix_figure,
    content,
    flags=re.DOTALL
)

# Also fix figures without description
def fix_figure_nodesc(m):
    label = m.group(1).replace('\n', ' ')
    label = re.sub(r'\s+', ' ', label).strip()
    
    num_match = re.search(r'Figure\s+([\d.]+)', label)
    ref = "fig:" + num_match.group(1).replace(".", "_") if num_match else "fig:placeholder"
    
    return (
        "\\begin{figure}[H]\n"
        "\\centering\n"
        "\\fbox{\\parbox{0.85\\linewidth}{\\centering\\vspace{20pt}\n"
        "{\\small\\textit{[" + label + "]}}\\vspace{20pt}}}\n"
        "\\caption{" + label + "}\n"
        "\\label{" + ref + "}\n"
        "\\end{figure}"
    )

content = re.sub(
    r"\\textbf\{\{\[\}(Figure[^\]]+)\{\]\}\}\\\\\n?(?!\\emph)",
    fix_figure_nodesc,
    content,
    flags=re.DOTALL
)

# 2. Fix Tables
def fix_table(m):
    label = m.group(1).replace('\n', ' ')
    label = re.sub(r'\s+', ' ', label).strip()
    
    num_match = re.search(r'Table\s+([\d.]+)', label)
    ref = "tab:" + num_match.group(1).replace(".", "_") if num_match else "tab:placeholder"
    
    # Remove the "Table X.X:" from caption for the actual caption argument
    caption = re.sub(r'^Table\s+[\d.]+:\s*', '', label)
    
    return (
        "\\begin{table}[H]\n"
        "\\centering\n"
        "\\caption{" + caption + "}\n"
        "\\label{" + ref + "}\n"
        "\\begin{tabular}{ll}\\toprule\n"
        "\\multicolumn{2}{c}{\\textit{[Data not yet available]}} \\\\\n"
        "\\bottomrule\n"
        "\\end{tabular}\n"
        "\\end{table}"
    )

content = re.sub(
    r"\\textbf\{\{\[\}(Table[^\]]+)\{\]\}\}\\\\?",
    fix_table,
    content,
    flags=re.DOTALL
)


with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)

print("Done")
