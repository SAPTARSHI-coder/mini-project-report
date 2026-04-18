import re

filepath = r"d:\DESKTOP\Mini Projrct\output.tex"

with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

# Restore \\[Xpt] that was incorrectly stripped to [Xpt]
# We'll target [\d+pt] but we should be careful not to double backslash if it already has it.
# Actually, let's just do a blanket replace of ` [Xpt]` to `\\[Xpt]` for the lines we know are affected
content = re.sub(r'(?<!\\\\) (\[\d+pt\])', r'\\\\\1', content)

# But wait! For some lines like `[3pt]` the regex above might miss if there's no space before it?
# Let's use `(?<!\\\\)\s*(\[\d+pt\])`
content = re.sub(r'(?<!\\\\)\s*(\[\d+pt\])', r'\\\\\1', content)

with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)

print("Restored")
