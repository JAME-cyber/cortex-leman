# PDF Dossier Template (fpdf2)

Proven template for generating structured Go/No-Go or analysis dossiers as PDF.
Uses DejaVu Sans TTF fonts for full Unicode support.

## Requirements

```bash
pip install fpdf2
# DejaVu fonts should be pre-installed on most Linux systems:
# /usr/share/fonts/truetype/dejavu/DejaVuSans.ttf
# /usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf
# /usr/share/fonts/truetype/dejavu/DejaVuSans-Oblique.ttf
```

## Working Pattern

```python
from fpdf import FPDF
from fpdf.enums import XPos, YPos

font_r = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
font_b = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
font_i = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Oblique.ttf'

class DossierPDF(FPDF):
    def header(self):
        if self.page_no() == 1:
            return  # No header on title page
        self.set_fill_color(232, 149, 96)  # Warm accent bar
        self.rect(0, 0, 210, 10, 'F')
        self.set_font('DejaVu', '', 7)
        self.set_text_color(255, 255, 255)
        self.cell(0, 6, 'PROJECT NAME - DOSSIER', align='R')
        self.set_text_color(0, 0, 0)
        self.ln(4)

    def footer(self):
        self.set_y(-15)
        self.set_font('DejaVu', 'I', 7)
        self.set_text_color(128)
        self.cell(0, 10, f'Page {self.page_no()}/{{nb}} - {date}', align='C')
        self.set_text_color(0)

pdf = DossierPDF()
pdf.alias_nb_pages()
pdf.set_auto_page_break(auto=True, margin=22)
pdf.add_font('DejaVu', '', font_r)
pdf.add_font('DejaVu', 'B', font_b)
pdf.add_font('DejaVu', 'I', font_i)

# ... build pages with pdf.cell() / pdf.multi_cell() ...
# Use new_x=XPos.LMARGIN, new_y=YPos.NEXT instead of ln=1

pdf.output('output.pdf')
```

## Key gotchas

1. **Always use `set_font('DejaVu', ...)` — never Helvetica.** Helvetica = latin-1 crash on any Unicode.
2. **fpdf2 v2.5.2+ deprecated `ln` param.** Use `new_x=XPos.LMARGIN, new_y=YPos.NEXT` for newline behavior, or just chain with `pdf.ln(5)` for spacing.
3. **For tables:** manual cell positioning with `border=1` works fine. No built-in table renderer — just loop and `pdf.ln()` after each row.
4. **Colored section headers:** set fill color before `cell(fill=True)`, then reset.
5. **Multi-cell text:** `pdf.multi_cell(width, line_height, text)` auto-wraps and advances Y position.

## Dossier page structure (proven layout)

- **Page 1:** Title bar (accent color rect) + info line + executive summary table + first section
- **Page 2:** Landed cost breakdown table + benchmark data
- **Page 3:** 3-scenario analysis blocks (color-coded) + risk matrix
- **Page 4:** Conclusion + investment table + next steps + sources footer

Keep font sizes: 18pt title, 13pt section headers, 9pt body, 8pt tables, 7pt footer.
