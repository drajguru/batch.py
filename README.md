batch.py
========

A small side project to satisfy my recreational programming itch :)

Extremely WIP!

## Usage
```python
import batch

# Read batch script
with file(BATCH_FILE, "rb") as f:
    script = f.read()

# Load into lexer
batch.lexer.input(script)

# Iterate over tokens
for token in batch.lexer:
    print token.value
```