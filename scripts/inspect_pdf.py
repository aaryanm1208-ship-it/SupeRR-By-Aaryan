import zlib
import re

pdf_path = r'6af458274c1e8_data_pack\Data Pack\Round 1 Problem Statement _ SupeRR Selector Season 2.docx.pdf'
with open(pdf_path, 'rb') as f:
    content = f.read()

# Look for stream objects
streams = re.finditer(rb'stream[\r\n]+(.*?)[\r\n]+endstream', content, re.DOTALL)
for i, match in enumerate(streams):
    data = match.group(1)
    try:
        dec = zlib.decompress(data)
        print(f"=== Stream {i} (len {len(dec)}) ===")
        # Look for text operators like Tj, TJ, or readable strings
        lines = dec.splitlines()
        for line in lines:
            if b'Tj' in line or b'TJ' in line:
                print(line.decode('latin1', errors='replace'))
    except Exception as e:
        print(f"Stream {i} failed decompress: {e}")
