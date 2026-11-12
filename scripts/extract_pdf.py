import zlib
import re

pdf_path = r'6af458274c1e8_data_pack\Data Pack\Round 1 Problem Statement _ SupeRR Selector Season 2.docx.pdf'
with open(pdf_path, 'rb') as f:
    content = f.read()

# Let's find ToUnicode CMaps in the PDF
cmaps = {}
for match in re.finditer(rb'<<.*?/ToUnicode\s+(\d+)\s+(\d+)\s+R.*?>>', content, re.DOTALL):
    obj_num = int(match.group(1))
    # find the object
    obj_pattern = re.compile(rf'{obj_num}\s+0\s+obj(.*?)endobj', re.DOTALL)
    m = obj_pattern.search(content.decode('latin1', errors='ignore'))
    if m:
        obj_text = m.group(1).encode('latin1')
        stream_m = re.search(rb'stream[\r\n]+(.*?)[\r\n]+endstream', obj_text, re.DOTALL)
        if stream_m:
            try:
                cmap_data = zlib.decompress(stream_m.group(1)).decode('latin1', errors='ignore')
                # Parse cmap mappings: beginbfchar / endbfchar and beginbfrange / endbfrange
                for bfchar in re.finditer(r'beginbfchar(.*?)endbfchar', cmap_data, re.DOTALL):
                    for line in bfchar.group(1).strip().splitlines():
                        parts = line.split()
                        if len(parts) >= 2:
                            src = parts[0].strip('<>')
                            dst = parts[1].strip('<>')
                            # dst can be utf16 hex
                            try:
                                dst_char = bytes.fromhex(dst).decode('utf-16-be')
                                cmaps[src.upper()] = dst_char
                            except Exception:
                                pass
                for bfrange in re.finditer(r'beginbfrange(.*?)endbfrange', cmap_data, re.DOTALL):
                    for line in bfrange.group(1).strip().splitlines():
                        parts = line.split()
                        if len(parts) >= 3:
                            start = int(parts[0].strip('<>'), 16)
                            end = int(parts[1].strip('<>'), 16)
                            dst = int(parts[2].strip('<>'), 16)
                            for code in range(start, end + 1):
                                src_hex = f"{code:04X}"
                                dst_code = dst + (code - start)
                                try:
                                    dst_char = chr(dst_code)
                                    cmaps[src_hex] = dst_char
                                except Exception:
                                    pass
            except Exception as e:
                print("Error decompressing cmap:", e)

print(f"Loaded {len(cmaps)} character mappings.")

# Now extract text from all stream objects
def decode_tj(hex_str):
    # hex_str like 010A
    res = []
    # could be 4 hex chars per glyph
    for i in range(0, len(hex_str), 4):
        code = hex_str[i:i+4].upper()
        if code in cmaps:
            res.append(cmaps[code])
        else:
            res.append(f"[{code}]")
    return ''.join(res)

full_extracted = []
streams = re.finditer(rb'stream[\r\n]+(.*?)[\r\n]+endstream', content, re.DOTALL)
for i, match in enumerate(streams):
    data = match.group(1)
    try:
        dec = zlib.decompress(data)
        text_lines = []
        for line in dec.splitlines():
            line_str = line.decode('latin1', errors='replace')
            # Look for <hex> Tj
            for m in re.finditer(r'<([0-9a-fA-F]+)>\s*Tj', line_str):
                text_lines.append(decode_tj(m.group(1)))
            # Look for [(...) <...> (...)] TJ
            for m in re.finditer(r'\[(.*?)\]\s*TJ', line_str):
                tj_inner = m.group(1)
                for h in re.finditer(r'<([0-9a-fA-F]+)>', tj_inner):
                    text_lines.append(decode_tj(h.group(1)))
            if 'ET' in line_str or 'T*' in line_str:
                text_lines.append('\n')
        if text_lines:
            txt = ''.join(text_lines)
            if any(c.isalnum() for c in txt):
                full_extracted.append(f"--- Stream {i} ---\n" + txt)
    except Exception:
        pass

out_text = '\n\n'.join(full_extracted)
with open('scripts/extracted_problem_statement.txt', 'w', encoding='utf-8') as f:
    f.write(out_text)

print("Extracted problem statement length:", len(out_text))
print("First 2000 chars:\n")
print(out_text[:2000])
