#!/usr/bin/env python3
"""
Build the enhanced Voron Log Analyzer HTML file.
This script reads the backup and applies all enhancements.
"""

import re

# Read the backup file
with open('voron_log_analyzer_backup_20260506_195506.html', 'r', encoding='utf-8') as f:
    content = f.read()

print("Building enhanced version...")
print(f"Original size: {len(content)} bytes")

# 1. Fix cooldown padding
content = content.replace(
    'const pad = 2 * 60000;',
    'const startPad = 2 * 60000;  // 2 minutes before\n  const endPad = 15 * 60000;   // 15 minutes after to capture full cooldown'
)
content = content.replace(
    'return S.records.filter(r => r.wallTime >= new Date(start - pad) && r.wallTime <= new Date(end + pad));',
    'return S.records.filter(r => r.wallTime >= new Date(start.getTime() - startPad) && r.wallTime <= new Date(end.getTime() + endPad));'
)

# Apply same fix to sessionEchoes
content = re.sub(
    r'function sessionEchoes\(\) \{[^}]+const pad = 2 \* 60000;[^}]+\}',
    '''function sessionEchoes() {
  if (!S.echoes.length) return [];
  if (!S.activeSession) return S.echoes;
  const { start, end } = S.activeSession;
  const startPad = 2 * 60000;
  const endPad = 15 * 60000;
  return S.echoes.filter(e => e.time >= new Date(start.getTime() - startPad) && e.time <= new Date(end.getTime() + endPad));
}''',
    content,
    flags=re.DOTALL
)

print("✓ Fixed cooldown padding")

# Write the enhanced version
with open('voron_log_analyzer.html', 'w', encoding='utf-8') as f:
    f.write(content)

print(f"✓ Enhanced version created: {len(content)} bytes")
print("✓ Done! Open voron_log_analyzer.html in your browser")
