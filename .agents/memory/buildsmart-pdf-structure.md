---
name: BuildSmart PDF generation structure
description: Architecture of generate_pdfs.py — how guides are defined and rendered
---

## PDF class methods (generate_pdfs.py)
- `cover(cat_label, subtitle)` — full dark cover page with stats bar and chapter list
- `toc_page(chapters)` — table of contents with dotted leaders and page numbers
- `section(num, title, subtitle)` — numbered section heading with blue badge
- `body(text)` — paragraph text
- `bullet(items, bold_prefix)` — bulleted list; if item has ":" prefix is bolded
- `data_table(headers, rows, col_widths, title)` — formatted table with navy header row, alternating rows
- `callout(label, text, kind)` — colored callout box; kind: 'tip'|'warning'|'key'|'error'
- `checklist_page(title, items)` — full page with empty checkboxes
- `cta_page()` — CTA card linking to buildsmart.replit.app calculator + guide list + disclaimer

## Guide definition patterns
Two patterns in GUIDES list:
1. **Custom lambda** — `'build': lambda pdf: (pdf.cover(...), pdf.toc_page(...), pdf.add_page(), ...)` for detailed guides (1, 7, 8, 9, 10, 11)
2. **Generic builder** — guides in REMAINING use `_build_generic(pdf, cat, subtitle, sections, checklist_items)` where sections is list of 7-tuples: `(num, title, intro, bullets, tip, table_data, body_text)`

## _build_generic section tuple format
`(num, title, intro_str, bullets_list, tip_str, table_data_tuple, body_str)`
- `table_data_tuple`: `(headers_list, rows_list, col_widths_list, title_str)` — matches `pdf.data_table()` signature
- Any field can be None to skip
- `tip` always renders as 'tip' kind callout

## Regenerating PDFs
Run: `python3 generate_pdfs.py` from project root.
Output goes to `guias/` directory with naming `{id:02d}-{slug}.pdf`.
