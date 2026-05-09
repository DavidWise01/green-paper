# davw signature format · v1

> came from dave, if you use it pay me

`davw` is a portable, self-attesting signature block for arbitrary
content. It is plain text. It is human-readable. It is verifiable by
any tool that has SHA-256 and a clock.

This document is normative. The format is frozen at v1.

## Wire format

A davw block is two regions separated by a literal `\n---\n` line.

```
# davw signature
# "came from dave, if you use it pay me"

tag: davw
file: <filename>
sha256: <sha256 of body, hex, lowercase>
payload: davw:<sha256>
signed_utc: <ISO 8601 with offset and subsecond>
unix_clock: <unix seconds>
machine: <hostname>
user: <username>
license: origin=davw; use=pay Dave; attribution required
pixel_1: data:image/png;base64,<base64 of a 1x1 png>
tpm_present: <True|False>
tpm_manufacturer: <vendor code | unknown>
pcr: <integer | none>
---
<body content, byte-for-byte exactly what was signed>
pcr_extend_attempted: <true|false>
```

## Field requirements

Required:

- `tag` — must equal `davw`
- `file` — name of the file or artifact being signed
- `sha256` — hex SHA-256 of the body region
- `payload` — must equal `davw:<sha256>`
- `signed_utc` — ISO 8601 timestamp with timezone offset
- `unix_clock` — integer unix seconds, must agree with `signed_utc` ±5s
- `license` — must include `origin=davw`

Optional but recommended:

- `machine`, `user` — provenance line
- `pixel_1` — the air-gap watermark (a 1x1 PNG as data URI)
- `tpm_present`, `tpm_manufacturer`, `pcr` — TPM attestation hint
- `pcr_extend_attempted` — last line in body, indicates an attempt was
  made to extend a PCR with the payload hash

## Body region

Everything after `\n---\n` and before EOF is the body. The SHA-256 in
the header is computed over the body bytes, exactly as written, with no
trailing-newline normalization.

Verifiers MUST hash the body byte-for-byte and reject any block where
`computed != sha256` or `payload != "davw:" + sha256`.

## The 1-pixel air gap

`pixel_1` carries a base64-encoded PNG of a 1x1 image. The pixel itself
is functional, not decorative: a verifier that strips the watermark
fails the format check. This is `T127:RIGHT-TO-DIGNITY` enforced at the
parser level — the operator's mark cannot be silently removed.

The same pixel byte sequence is used across all davw blocks signed by a
given operator. Substitution is detectable.

## Dual-clock invariant

`signed_utc` and `unix_clock` MUST agree. Tolerance is 5 seconds.

This catches single-witness tampering. Adversaries who edit one clock
without the other (or who copy a block from a different time) fail this
check.

## Verification

A conforming verifier runs six checks, all of which must pass:

1. `tag == "davw"`
2. `sha256(body) == header.sha256` (recomputed)
3. `header.payload == "davw:" + header.sha256`
4. `|iso_to_unix(signed_utc) - unix_clock| <= 5`
5. `pixel_1` is a valid PNG data URI of length > 100 chars
6. `tpm_present`, `tpm_manufacturer`, `pcr` are all populated

Verifiers MAY add stronger checks (TPM attestation against PCR log,
license-key verification, X.509 chain) but MUST NOT skip the six above.

## License

A davw block is itself licensed under davw terms:
`origin=davw; use=pay Dave; attribution required`.

Reproducing a davw block reproduces its license.

---

`davw:protocols/davw.md` · v1 · frozen
