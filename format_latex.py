import sys

with open("d:\\DESKTOP\\Mini Projrct\\output.tex", "r", encoding="utf-8") as f:
    lines = f.readlines()

new_lines = []
skip = False

for i, line in enumerate(lines):
    # secnumdepth 5 -> 0
    if line.startswith(r"\setcounter{secnumdepth}{5}"):
        new_lines.append(r"\setcounter{secnumdepth}{0}" + "\n")
        continue

    # Setup roman numbering and remove first table of contents
    if line.startswith(r"\begin{document}"):
        new_lines.append(line)
        new_lines.append(r"\pagenumbering{roman}" + "\n")
        continue

    if i >= 56 and i <= 59:
        # these are the { \setcounter{tocdepth}{3} \tableofcontents } lines
        # skip them
        continue
        
    # Add newpages to sections
    if line.startswith(r"\section{Certificate}"):
        new_lines.append(r"\newpage" + "\n")
        new_lines.append(line)
        continue
    if line.startswith(r"\section{Declaration}"):
        new_lines.append(r"\newpage" + "\n")
        new_lines.append(line)
        continue
    if line.startswith(r"\section{Abstract}"):
        new_lines.append(r"\newpage" + "\n")
        new_lines.append(line)
        continue
    if line.startswith(r"\section{Acknowledgement}"):
        new_lines.append(r"\newpage" + "\n")
        new_lines.append(line)
        continue

    # Replace manual table of contents
    if line.startswith(r"\section{Table of Contents}"):
        # Start skipping until CHAPTER 6: REFERENCES and the dashed line
        skip = True
        new_lines.append(r"\newpage" + "\n")
        new_lines.append(r"\renewcommand{\contentsname}{Table of Contents}" + "\n")
        new_lines.append(r"{" + "\n")
        new_lines.append(r"\setcounter{tocdepth}{3}" + "\n")
        new_lines.append(r"\tableofcontents" + "\n")
        new_lines.append(r"}" + "\n")
        continue

    if skip:
        if line.startswith(r"-\/-\/-") and (i > 250 and i < 270):
            skip = False
        continue

    if line.startswith(r"\section{List of Tables}"):
        new_lines.append(r"\newpage" + "\n")
        new_lines.append(line)
        continue
    if line.startswith(r"\section{List of Figures}"):
        new_lines.append(r"\newpage" + "\n")
        new_lines.append(line)
        continue
    if line.startswith(r"\section{Abbreviations}"):
        new_lines.append(r"\newpage" + "\n")
        new_lines.append(line)
        continue

    # Chapter 1 arabic numbering
    if line.startswith(r"\section{CHAPTER 1: INTRODUCTION}"):
        new_lines.append(r"\newpage" + "\n")
        new_lines.append(r"\pagenumbering{arabic}" + "\n")
        new_lines.append(r"\setcounter{page}{1}" + "\n")
        new_lines.append(line)
        continue

    new_lines.append(line)

with open("d:\\DESKTOP\\Mini Projrct\\output.tex", "w", encoding="utf-8") as f:
    f.writelines(new_lines)

print("Modification complete.")
