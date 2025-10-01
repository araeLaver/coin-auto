"""Decimal을 Numeric으로 변경"""
import re

with open('database/models.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Decimal( -> Numeric(으로 변경
content = re.sub(r'Decimal\(', 'Numeric(', content)

with open('database/models.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Decimal -> Numeric 변환 완료")
