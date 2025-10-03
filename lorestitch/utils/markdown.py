import re
HEADING_RX = re.compile(r"^(#{1,6})\s+(.*)$", re.MULTILINE)
def extract_headings(md_text: str):
    return [(m.group(1), m.group(2).strip()) for m in HEADING_RX.finditer(md_text or "")]
