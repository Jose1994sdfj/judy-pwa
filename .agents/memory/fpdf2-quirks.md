---
name: fpdf2 quirks for BuildSmart
description: Known gotchas when using fpdf2 to generate construction PDFs in this project
---

## Latin-1 character constraint
Helvetica in fpdf2 only handles latin-1 (0-255). Use `_safe()` helper to replace anything above 255.
- ñ, á, é, í, ó, ú, ü ARE in latin-1 — pass through fine
- •, →, ×, ², ³ are NOT — replace with *, >>, x, 2, 3

## set_draw_color with tuple math
This FAILS: `self.set_draw_color(*B_MUTED[0]-10, *B_MUTED[1:])` — you can't unpack and subtract inline.
Use: `self.set_draw_color(B_MUTED[0]-10, B_MUTED[1], B_MUTED[2])`

## bullet() width overflow guard
When splitting "Bold: rest" text in bullet(), cap the prefix width:
`prefix_w = min(len(parts[0]) * 2.3, CW - 30)`
`remainder_w = max(CW - 7 - prefix_w, 30)`
Otherwise short-text cells raise FPDFException "not enough horizontal space".

## Cover page position management
On the cover page, `set_auto_page_break` can trigger a new page call if a cell overflows.
Keep the cover page's "bottom branding" section above y=280 to avoid unexpected page breaks.
