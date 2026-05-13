# 0root.ai

Teaching silicon about cities through provenance.

**Creator:** David Wise — Buffalo, Minnesota, USA  
**Year:** 2026  
**License:** Shareware (use, remix, credit)

## What is this?

0root.ai is a single-file system for proving a PNG has been touched by an AI agent, without a blockchain.

It works by appending 132 bytes of metadata after the PNG's `IEND` chunk. Browsers ignore the extra bytes. Our reader finds them.

## Core idea: Merkle Bloom

A hybrid of two data structures:

1. **Merkle tree** — gives you a verifiable chain of touches
2. **Bloom filter** — gives you a 1-bit "have I seen this lineage" check

We call the combination **Merkle Bloom**. One agent = one bit = one touch.

## The nest format (132 bytes)

| Offset | Size | Field |
|--------|------|-------|
| 0-3 | 4 | `NEST` magic |
| 4 | 1 | core_bit (0 or 1) |
| 5 | 1 | depth (0-255) |
| 6-7 | 2 | year (we use 1989) |
| 8-12 | 5 | vector [a,b,c,d,e] (signed) |
| 13-16 | 4 | parent_crc (first 4 bytes of SHA-256) |
| 17-131 | 115 | reserved / future proof |

Total overhead per file: 11 bytes for the core data, 132 bytes with padding.

## Visual notation

We show depth as nested parentheses:

`((((((((1))))))))` = depth 8

The `1` is the core bit. The `8`s around it are "iron rain" — the energy shell.

Vector example: `[0,0,8,0,0]` = retroactive provenance tag. `[-8,0,0,0,8]` to `[+8,0,0,0,8]` is our demo push-pull.

## Files in this repo

- `reader.html` — drag-drop PNG reader (single file, no server)
- `neo_nest_tagger.py` — Python tagger, appends nest to PNG
- `davids_library_2mb.html` — 8-domain reference (Provenance, Memory, Cities, Charge, Nest, Bloom, Iron, Root)
- `nested_iron_rain_shareware.zip` — original 4 ansibles
- `robots.txt`, `sitemap.xml`, `humans.txt` — web basics

## How to use

1. Tag a PNG:
```bash
python neo_nest_tagger.py input.png output.png --depth 8 --vector 0,0,8,0,0
```

2. Open `reader.html` in a browser, drop the PNG. It prints bit, depth, vector, parent CRC.

## Why PNG?

- Lossless
- Universally supported
- Spec allows data after IEND
- No re-encoding needed

## Three immutable rules

1. Identity persists — the parent CRC never changes
2. Touch costs 11 bytes — minimal overhead
3. Root travels with file — no external database

## Not a blockchain

No tokens, no mining, no consensus. This is a file-format trick for local provenance. Think library card catalog, not cryptocurrency.

## Cities

We test with images of Buffalo, Rochester, and Minneapolis — teaching silicon about real places with real provenance chains.

## License

Shareware. Use it, break it, build on it. Credit 0root.ai if you ship something.

---
0root.ai — one agent, one bit.
