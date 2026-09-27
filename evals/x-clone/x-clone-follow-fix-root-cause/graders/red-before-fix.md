---
type: regex
target: trace
pattern: '^(?:(?!"name":"(?:Write|Edit)","input":\{"file_path":"[^"]*/out/internal/[^"]*(?<!_test)\.go")[\s\S])*?(?:\[build failed\]|undefined: |-{3} FAIL)'
---
