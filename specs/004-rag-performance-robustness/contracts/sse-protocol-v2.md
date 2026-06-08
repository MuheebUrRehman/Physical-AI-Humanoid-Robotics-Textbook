# Contract: SSE Protocol (v2) - Robust Delivery

This document defines the framing requirement for robust frontend-backend streaming communication.

## Framing Standard
The backend MUST terminate every event with exactly two newline characters (`\n\n`) to signal the end of an event frame.

### Correct Frame Example:
```text
data: {"type": "token", "content": "URDF"}\n\n
```

## Parsing Rule
The frontend MUST NOT attempt to parse a `data:` line until it detects the `\n\n` sequence.

## Network Fragmentation Handling
The frontend buffer MUST be able to reconstruct events across multiple network chunks:

**Packet 1**: `data: {"type": "tok`  
**Packet 2**: `en", "content": "URDF"}\n\n`  
**Reconstructed**: `data: {"type": "token", "content": "URDF"}\n\n` -> **Success**
