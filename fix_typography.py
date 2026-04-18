import re

filepath = r"d:\DESKTOP\Mini Projrct\output.tex"

with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

# Remove stray \\\\ or \\ at the end of paragraphs
# Only target \\ at the end of lines that are followed by a blank line,
# or multiple backslashes. Be careful not to break table rows (\\ inside tabular)
# We can just look for `\\` that is outside of tabular/longtable environments.
# A simpler approach: remove `\\\\` completely, as it's bad LaTeX.
content = re.sub(r'\\\\(?!\n\s*\\)', '', content) # Removes \\\\ unless followed by another LaTeX command

# Remove \tightlist since we configured enumitem or parskip globally
content = content.replace(r"\tightlist", "")

# Remove excessive bolding in paragraphs (not headers or items)
# This is tricky because we want to keep \textbf{} for keywords or labels.
# The user's prompt says "Remove excessive bold". I'll search for \textbf{...} where the content is longer than 50 characters, as that's likely a whole sentence/paragraph bolded unnecessarily.

def unbold_long_text(match):
    text = match.group(1)
    if len(text) > 100 and "Figure" not in text and "Table" not in text:
        return text # remove \textbf
    return match.group(0) # keep \textbf

content = re.sub(r'\\textbf\{([^}]+)\}', unbold_long_text, content)

# Also fix the weird \begin{table}...\end{table}\begin{itemize} issue I saw in line 839
content = content.replace(r"\end{table}\begin{itemize}", "\\end{table}\n\n\\begin{itemize}")

# Remove multiple blank lines
content = re.sub(r'\n{3,}', '\n\n', content)

with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)
print("Done")
