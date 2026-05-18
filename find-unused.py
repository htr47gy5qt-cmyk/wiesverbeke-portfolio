#!/usr/bin/env python3
import os, urllib.parse, pathlib

extensions = {'.html', '.css', '.js', '.json'}
blob = []
for p in pathlib.Path('.').rglob('*'):
    if p.is_file() and p.suffix.lower() in extensions and 'photos-unused' not in p.parts:
        try:
            blob.append(p.read_text(errors='ignore'))
        except Exception:
            pass
text = '\n'.join(blob)

photos = sorted(os.listdir('photos'))
unused = []
for f in photos:
    stem, _ = os.path.splitext(f)
    candidates = [f] + [stem + ext for ext in ('.jpg', '.jpeg', '.png', '.webp')]
    if any(c in text or urllib.parse.quote(c) in text for c in candidates):
        continue
    unused.append(f)

print(f"Unused: {len(unused)} / Total: {len(photos)}")
pathlib.Path('/tmp/unused.txt').write_text('\n'.join(unused) + '\n')
print("---")
print('\n'.join(unused[:30]))
