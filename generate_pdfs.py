#!/usr/bin/env python3
"""
BuildSmart Mexico – Professional PDF Guide Generator
Generates premium, multi-page PDF guides for construction & remodeling in Mexico.
"""
import os, re
from fpdf import FPDF
from fpdf.enums import XPos, YPos

OUTPUT_DIR = "guias"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ── Brand palette ──────────────────────────────────────────────────────
B_BLUE   = (0, 90, 255)
B_NAVY   = (10, 18, 42)
B_DARK   = (15, 23, 42)
B_DGRAY  = (51, 65, 85)
B_GRAY   = (100, 116, 139)
B_LGRAY  = (148, 163, 184)
B_MUTED  = (241, 245, 249)
B_WHITE  = (255, 255, 255)
B_ACCENT = (255, 127, 0)
B_GREEN  = (16, 185, 129)
B_YELLOW_BG = (255, 251, 235)
B_YELLOW_BD = (251, 191, 36)
B_GREEN_BG  = (236, 253, 245)
B_GREEN_BD  = (16, 185, 129)
B_RED_BG    = (254, 242, 242)
B_RED_BD    = (239, 68, 68)
B_BLUE_BG   = (239, 246, 255)
B_BLUE_BD   = (147, 197, 253)

LM, RM, TM_CONTENT = 18, 192, 32  # left margin, right margin, top margin for content pages
CW = RM - LM                       # content width = 174mm

def _safe(t):
    """Replace characters outside latin-1 with safe equivalents."""
    table = {
        '\u2013':'-', '\u2014':'-', '\u2019':"'", '\u201c':'"', '\u201d':'"',
        '\u00d7':'x', '\u00b2':'2', '\u00b3':'3', '\u2260':'!=',
        '\u2192':'>>', '\u2190':'<<', '\u25cf':'*', '\u2022':'*',
        '\u00bc':'1/4', '\u00bd':'1/2', '\u00be':'3/4',
        '\u00b0':'deg', '\u00b1':'+/-', '\u20ac':'EUR',
    }
    out = []
    for c in t:
        if ord(c) > 255:
            out.append(table.get(c, '?'))
        else:
            out.append(c)
    return ''.join(out)


class PDF(FPDF):
    def __init__(self, guide):
        super().__init__()
        self.guide = guide
        self.set_auto_page_break(auto=True, margin=22)
        self.set_margins(LM, TM_CONTENT, LM)

    # ──────────────────────────────────────────────────────── HEADER / FOOTER
    def header(self):
        if self.page_no() == 1:
            return  # cover has its own design
        # Thin top bar
        self.set_fill_color(*B_NAVY)
        self.rect(0, 0, 210, 8, 'F')
        # Logo
        self.set_xy(LM, 10)
        self.set_font('Helvetica', 'B', 8)
        self.set_text_color(*B_BLUE)
        self.cell(12, 5, 'Build', border=0, new_x=XPos.RIGHT, new_y=YPos.TOP)
        self.set_text_color(*B_DARK)
        self.cell(16, 5, 'Smart', border=0, new_x=XPos.RIGHT, new_y=YPos.TOP)
        # Guide title (truncated)
        title = self.guide['title'][:55] + ('...' if len(self.guide['title']) > 55 else '')
        self.set_font('Helvetica', '', 7)
        self.set_text_color(*B_GRAY)
        self.set_x(48)
        self.cell(0, 5, _safe(title), align='L')
        # Separator
        self.set_draw_color(B_MUTED[0]-10, B_MUTED[1], B_MUTED[2])
        self.set_line_width(0.2)
        self.line(LM, 18, RM, 18)

    def footer(self):
        if self.page_no() == 1:
            return
        self.set_y(-14)
        self.set_draw_color(B_MUTED[0]-20, B_MUTED[1], B_MUTED[2])
        self.set_line_width(0.2)
        self.line(LM, self.get_y(), RM, self.get_y())
        self.set_y(-12)
        self.set_font('Helvetica', '', 7)
        self.set_text_color(*B_LGRAY)
        self.cell(0, 5, f'BuildSmart Mexico  |  buildsmart.replit.app', align='L', new_x=XPos.RIGHT, new_y=YPos.TOP)
        self.cell(0, 5, f'Pagina {self.page_no()}', align='R')
        # Bottom bar
        self.set_fill_color(*B_NAVY)
        self.rect(0, 292, 210, 5, 'F')

    # ──────────────────────────────────────────────────────── COVER PAGE
    def cover(self, category_label, subtitle=''):
        self.add_page()
        # Full dark background
        self.set_fill_color(*B_NAVY)
        self.rect(0, 0, 210, 297, 'F')
        # Blue accent strip on left
        self.set_fill_color(*B_BLUE)
        self.rect(0, 0, 6, 297, 'F')
        # Decorative horizontal bar mid-page
        self.set_fill_color(20, 40, 80)
        self.rect(6, 110, 204, 0.5, 'F')
        self.rect(6, 185, 204, 0.5, 'F')
        # Top section: category + year
        self.set_xy(18, 22)
        self.set_font('Helvetica', 'B', 8)
        self.set_text_color(*B_BLUE)
        self.cell(0, 6, _safe(category_label.upper() + '  |  BUILDSMART MEXICO  |  2025'))
        # Divider line after category
        self.set_draw_color(*B_BLUE)
        self.set_line_width(0.4)
        self.line(18, 31, 192, 31)
        # Main title
        self.set_xy(18, 38)
        self.set_font('Helvetica', 'B', 22)
        self.set_text_color(*B_WHITE)
        self.multi_cell(174, 11, _safe(self.guide['title']),
                        new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        # Subtitle / tagline
        if subtitle:
            self.set_x(18)
            self.set_font('Helvetica', '', 11)
            self.set_text_color(180, 200, 230)
            self.multi_cell(160, 7, _safe(subtitle),
                            new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        # Mid-page: doc stats bar
        self.set_y(118)
        stats = self.guide.get('stats', {})
        items = [
            ('PAGINAS', str(stats.get('pages', 8))),
            ('TABLAS', str(stats.get('tables', 3))),
            ('CHECKLISTS', '1' if stats.get('checklist', True) else '0'),
            ('FORMATO', 'PDF'),
        ]
        col_w = 174 / len(items)
        for label, val in items:
            x = self.get_x()
            y = self.get_y()
            self.set_fill_color(20, 35, 70)
            self.rect(x, y, col_w - 2, 20, 'F')
            self.set_xy(x + 3, y + 2)
            self.set_font('Helvetica', 'B', 13)
            self.set_text_color(*B_BLUE)
            self.cell(col_w - 8, 8, val, align='C')
            self.set_xy(x + 3, y + 11)
            self.set_font('Helvetica', '', 6)
            self.set_text_color(*B_LGRAY)
            self.cell(col_w - 8, 5, label, align='C')
            self.set_xy(x + col_w, y)
        self.ln(28)
        # "Lo que incluye" section
        self.set_x(18)
        self.set_font('Helvetica', 'B', 9)
        self.set_text_color(*B_BLUE)
        self.cell(0, 7, 'LO QUE INCLUYE ESTA GUIA:')
        self.ln(7)
        for ch in self.guide.get('chapters', []):
            self.set_x(18)
            self.set_font('Helvetica', '', 8.5)
            self.set_text_color(200, 215, 235)
            self.cell(6, 6, '-', align='C')
            self.set_x(24)
            self.multi_cell(160, 6, _safe(ch),
                            new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        # Bottom branding
        self.set_xy(18, 268)
        self.set_draw_color(*B_BLUE)
        self.set_line_width(0.3)
        self.line(18, 268, 192, 268)
        self.set_xy(18, 271)
        self.set_font('Helvetica', 'B', 9)
        self.set_text_color(*B_BLUE)
        self.cell(30, 6, 'Build', new_x=XPos.RIGHT, new_y=YPos.TOP)
        self.set_text_color(*B_WHITE)
        self.cell(30, 6, 'Smart', new_x=XPos.RIGHT, new_y=YPos.TOP)
        self.set_font('Helvetica', '', 8)
        self.set_text_color(*B_LGRAY)
        self.cell(0, 6, '  buildsmart.replit.app  |  Guias profesionales de construccion en Mexico')
        self.set_xy(18, 280)
        self.set_font('Helvetica', '', 7)
        self.set_text_color(80, 100, 130)
        self.multi_cell(174, 4.5,
            'Nota: Los precios son de referencia y pueden variar segun region, proveedor y temporada. '
            'Siempre solicita cotizaciones locales antes de iniciar cualquier proyecto.',
            new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    # ──────────────────────────────────────────────────────── TOC PAGE
    def toc_page(self, chapters):
        self.add_page()
        self.set_y(28)
        self.set_font('Helvetica', 'B', 16)
        self.set_text_color(*B_DARK)
        self.cell(0, 10, 'Tabla de Contenido', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_draw_color(*B_BLUE)
        self.set_line_width(0.5)
        self.line(LM, self.get_y(), LM + 50, self.get_y())
        self.ln(8)
        for i, (ch_title, page_num) in enumerate(chapters, 1):
            y = self.get_y()
            # Chapter number
            self.set_fill_color(*B_BLUE)
            self.rect(LM, y, 7, 7, 'F')
            self.set_xy(LM, y)
            self.set_font('Helvetica', 'B', 7)
            self.set_text_color(*B_WHITE)
            self.cell(7, 7, str(i), align='C')
            # Chapter title
            self.set_xy(LM + 10, y + 0.5)
            self.set_font('Helvetica', '', 9.5)
            self.set_text_color(*B_DARK)
            self.cell(CW - 20, 7, _safe(ch_title))
            # Page number
            self.set_xy(RM - 10, y + 0.5)
            self.set_font('Helvetica', 'B', 9)
            self.set_text_color(*B_BLUE)
            self.cell(10, 7, str(page_num), align='R')
            # Dotted line
            self.set_draw_color(*B_LGRAY)
            self.set_line_width(0.1)
            self.set_dash_pattern(dash=1, gap=2)
            self.line(LM + 10 + len(ch_title)*3.2, y + 5.5, RM - 12, y + 5.5)
            self.set_dash_pattern()
            self.ln(9)
        # "Como usar esta guia" box
        self.ln(6)
        self._callout(
            'Como usar esta guia',
            'Lee cada seccion en orden la primera vez. Para consultas rapidas, '
            'usa la tabla de contenido para ir directo al dato que necesitas. '
            'Al final encontraras un checklist accionable para tu proyecto.',
            'tip'
        )

    # ──────────────────────────────────────────────────────── SECTION HEADING
    def section(self, num, title, subtitle=''):
        if self.get_y() > 240:
            self.add_page()
        self.ln(5)
        y = self.get_y()
        # Number badge
        self.set_fill_color(*B_BLUE)
        self.rect(LM, y, 9, 9, 'F')
        self.set_xy(LM, y)
        self.set_font('Helvetica', 'B', 8)
        self.set_text_color(*B_WHITE)
        self.cell(9, 9, str(num), align='C')
        # Title
        self.set_xy(LM + 12, y + 1)
        self.set_font('Helvetica', 'B', 13)
        self.set_text_color(*B_DARK)
        self.cell(0, 7, _safe(title))
        self.ln(11)
        # Underline
        self.set_draw_color(B_MUTED[0]-15, B_MUTED[1], B_MUTED[2])
        self.set_line_width(0.3)
        self.line(LM, self.get_y(), RM, self.get_y())
        self.ln(5)
        if subtitle:
            self.set_x(LM)
            self.set_font('Helvetica', 'I', 9)
            self.set_text_color(*B_GRAY)
            self.multi_cell(CW, 5.5, _safe(subtitle),
                            new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            self.ln(3)

    def body(self, text):
        self.set_x(LM)
        self.set_font('Helvetica', '', 9.5)
        self.set_text_color(*B_DGRAY)
        self.multi_cell(CW, 5.5, _safe(text),
                        new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(3)

    def bullet(self, items, bold_prefix=True):
        for item in items:
            if self.get_y() > 265:
                self.add_page()
            self.set_x(LM + 3)
            # Bullet dot
            self.set_fill_color(*B_BLUE)
            self.ellipse(LM + 3, self.get_y() + 2.8, 1.8, 1.8, 'F')
            self.set_x(LM + 7)
            # Split "Bold:" rest — cap prefix width so remainder never goes negative
            if bold_prefix and ':' in item:
                parts = item.split(':', 1)
                prefix_w = min(len(parts[0]) * 2.3, CW - 30)
                self.set_font('Helvetica', 'B', 9)
                self.set_text_color(*B_DARK)
                self.cell(prefix_w, 5.5, _safe(parts[0] + ':'), new_x=XPos.RIGHT, new_y=YPos.TOP)
                self.set_font('Helvetica', '', 9)
                self.set_text_color(*B_DGRAY)
                remainder_w = max(CW - 7 - prefix_w, 30)
                self.multi_cell(remainder_w, 5.5, _safe(parts[1].strip()),
                                new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            else:
                self.set_font('Helvetica', '', 9)
                self.set_text_color(*B_DGRAY)
                self.multi_cell(CW - 7, 5.5, _safe(item),
                                new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            self.ln(1)

    # ──────────────────────────────────────────────────────── DATA TABLE
    def data_table(self, headers, rows, col_widths=None, title=''):
        if col_widths is None:
            w = CW / len(headers)
            col_widths = [w] * len(headers)
        if title:
            self.set_x(LM)
            self.set_font('Helvetica', 'B', 8)
            self.set_text_color(*B_BLUE)
            self.cell(0, 6, _safe(title.upper()), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            self.ln(1)
        if self.get_y() + len(rows)*6 + 14 > 275:
            self.add_page()
        # Header row
        self.set_fill_color(*B_NAVY)
        for i, (h, w) in enumerate(zip(headers, col_widths)):
            self.set_x(LM + sum(col_widths[:i]))
            self.set_font('Helvetica', 'B', 8)
            self.set_text_color(*B_WHITE)
            self.cell(w, 8, _safe(str(h)), border=0, fill=True,
                      align='C' if i > 0 else 'L',
                      new_x=XPos.RIGHT, new_y=YPos.TOP)
        self.ln(8)
        # Data rows
        for ri, row in enumerate(rows):
            bg = B_MUTED if ri % 2 == 0 else B_WHITE
            self.set_fill_color(*bg)
            for i, (cell, w) in enumerate(zip(row, col_widths)):
                self.set_x(LM + sum(col_widths[:i]))
                self.set_font('Helvetica', 'B' if i == 0 else '', 8.5)
                self.set_text_color(*B_DARK if i == 0 else B_DGRAY)
                self.cell(w, 6.5, _safe(str(cell)), border=0, fill=True,
                          align='L' if i == 0 else 'C',
                          new_x=XPos.RIGHT, new_y=YPos.TOP)
            self.ln(6.5)
        self.ln(5)

    # ──────────────────────────────────────────────────────── CALLOUT BOX
    def _callout(self, label, text, kind='tip'):
        palettes = {
            'tip':     (B_GREEN_BG,  B_GREEN_BD,  (5, 100, 70),   'CONSEJO PRO'),
            'warning': (B_YELLOW_BG, B_YELLOW_BD, (120, 80, 0),   'ADVERTENCIA'),
            'key':     (B_BLUE_BG,   B_BLUE_BD,   (30, 64, 175),  'DATO CLAVE'),
            'error':   (B_RED_BG,    B_RED_BD,    (180, 30, 30),  'EVITA ESTO'),
        }
        bg, bd, txt_col, default_label = palettes.get(kind, palettes['tip'])
        label = label or default_label
        lines = len(_safe(text)) // 75 + 2
        box_h = 8 + lines * 5.5
        if self.get_y() + box_h + 6 > 272:
            self.add_page()
        y = self.get_y() + 2
        self.set_fill_color(*bg)
        self.set_draw_color(*bd)
        self.set_line_width(0.4)
        self.rect(LM, y, CW, box_h, 'DF')
        # Left accent stripe
        self.set_fill_color(*bd)
        self.rect(LM, y, 3, box_h, 'F')
        self.set_xy(LM + 6, y + 3)
        self.set_font('Helvetica', 'B', 7.5)
        self.set_text_color(*txt_col)
        self.cell(0, 4, _safe(label.upper()), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_x(LM + 6)
        self.set_font('Helvetica', '', 8.5)
        self.set_text_color(*B_DGRAY)
        self.multi_cell(CW - 10, 5.2, _safe(text),
                        new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(6)

    def callout(self, label, text, kind='tip'):
        self._callout(label, text, kind)

    # ──────────────────────────────────────────────────────── CHECKLIST
    def checklist_page(self, title, items):
        self.add_page()
        self.set_y(28)
        self.set_fill_color(*B_NAVY)
        self.rect(0, 0, 210, 14, 'F')
        self.set_xy(LM, 4)
        self.set_font('Helvetica', 'B', 10)
        self.set_text_color(*B_WHITE)
        self.cell(0, 6, _safe('CHECKLIST: ' + title.upper()))
        self.ln(20)
        self.set_font('Helvetica', '', 9)
        self.set_text_color(*B_GRAY)
        self.set_x(LM)
        self.cell(0, 5, 'Marca cada punto antes de avanzar a la siguiente etapa de tu proyecto.',
                  new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(6)
        for item in items:
            if self.get_y() > 265:
                self.add_page()
            y = self.get_y()
            # Checkbox (empty square)
            self.set_draw_color(*B_BLUE)
            self.set_line_width(0.5)
            self.rect(LM, y + 0.5, 5, 5)
            self.set_xy(LM + 8, y)
            self.set_font('Helvetica', '', 9.5)
            self.set_text_color(*B_DARK)
            self.multi_cell(CW - 10, 6, _safe(item),
                            new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            self.ln(1)

    # ──────────────────────────────────────────────────────── CTA PAGE
    def cta_page(self):
        self.add_page()
        # Full blue background card
        self.set_fill_color(*B_NAVY)
        self.rect(LM, 30, CW, 60, 'F')
        self.set_fill_color(*B_BLUE)
        self.rect(LM, 30, CW, 3, 'F')
        self.set_xy(LM + 8, 38)
        self.set_font('Helvetica', 'B', 14)
        self.set_text_color(*B_WHITE)
        self.cell(0, 8, 'Calcula el presupuesto de tu proyecto')
        self.set_xy(LM + 8, 50)
        self.set_font('Helvetica', '', 9)
        self.set_text_color(180, 205, 240)
        self.multi_cell(CW - 16, 5.5,
            'Usa la calculadora gratuita de BuildSmart para obtener un presupuesto '
            'detallado con materiales, cantidades y precios actualizados para Mexico.',
            new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_xy(LM + 8, 70)
        self.set_font('Helvetica', 'B', 10)
        self.set_text_color(*B_BLUE)
        self.cell(0, 6, 'buildsmart.replit.app  >>  Calculadora')
        self.ln(22)
        # More guides
        self.set_x(LM)
        self.set_font('Helvetica', 'B', 11)
        self.set_text_color(*B_DARK)
        self.cell(0, 7, 'Otras guias disponibles en BuildSmart:',
                  new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(3)
        other = [
            'Cuanto cuesta construir una casa en Mexico en 2025',
            'Precio de materiales de construccion Mexico 2025',
            'Cuanto cuesta remodelar un bano completo en Mexico',
            'Presupuesto para cocina pequena en Mexico',
            'Impermeabilizacion de azotea: tipos y costos por m2',
            'Instalacion electrica residencial: precios y normativa NOM',
        ]
        title = self.guide['title']
        for g in other:
            if g.lower() not in title.lower():
                self.bullet([g], bold_prefix=False)
        self.ln(6)
        # Disclaimer
        self.set_x(LM)
        self.set_font('Helvetica', '', 7)
        self.set_text_color(*B_LGRAY)
        self.multi_cell(CW, 4.5,
            'Los precios y datos incluidos en esta guia son de referencia para Mexico 2025. '
            'Pueden variar segun region, proveedor, condiciones de mercado y tipo de proyecto. '
            'BuildSmart recomienda siempre obtener cotizaciones locales antes de iniciar cualquier obra. '
            'Esta guia es de uso personal y no puede redistribuirse sin autorizacion.',
            new_x=XPos.LMARGIN, new_y=YPos.NEXT)


# ══════════════════════════════════════════════════════════════════════════
#  GUIDE CONTENT DEFINITIONS
# ══════════════════════════════════════════════════════════════════════════

GUIDES = [

# ─────────────────────────────────────────────────────────────── GUIDE 1
{
'id':1,'slug':'01-fundamentos-del-concreto',
'cat':'Fundamentos',
'title':'Fundamentos del Concreto',
'subtitle':'Mezclas perfectas desde la primera colada',
'stats':{'pages':9,'tables':3,'checklist':True},
'chapters':[
    'Quimica del concreto y sus componentes',
    'Proporciones y resistencias por uso',
    'Calculo exacto de materiales',
    'Proceso de vaciado profesional',
    'Curado y control de calidad',
    'Errores comunes y como evitarlos',
    'Checklist de control en obra',
],
'build': lambda pdf: (
    pdf.cover('Fundamentos de Construccion', 'Mezclas perfectas desde la primera colada'),
    pdf.toc_page([
        ('Quimica del concreto y sus componentes', 3),
        ('Proporciones y resistencias por uso', 4),
        ('Calculo exacto de materiales por m3', 5),
        ('Proceso de vaciado profesional', 6),
        ('Curado y control de calidad', 7),
        ('Errores comunes y como evitarlos', 8),
        ('Checklist de control en obra', 9),
    ]),
    pdf.add_page(),

    pdf.section(1, 'Quimica del concreto y sus componentes',
        'Entender por que reacciona el concreto te permite tomar mejores decisiones en obra.'),
    pdf.body(
        'El concreto es una roca artificial formada por la reaccion quimica entre el cemento y el agua '
        '(hidratacion). Esta reaccion libera calor y forma silicatos de calcio hidratado (C-S-H), que son '
        'los responsables de la resistencia final. La arena y la grava no reaccionan: solo actuan como '
        'relleno que reduce la retraccion y el costo.'),
    pdf.bullet([
        'Cemento Portland tipo I: uso general residencial. Resistencia estandar, disponible en todo Mexico.',
        'Cemento tipo II: resistente a sulfatos. Ideal para suelos con yeso (zona norte y costas).',
        'Cemento tipo III: fraguado rapido. Util para climas frios o cuando se requiere desencofrar pronto.',
        'Cemento con puzolana (IP): menor calor de hidratacion. Recomendado para masivos como cimentaciones.',
        'Arena: debe estar limpia, sin arcilla ni sales. Granulometria 0.075-4.75 mm (ASTM C-33).',
        'Grava: triturada o rodada, sin exceso de finos. Tamano maximo segun uso (19 mm losas, 38 mm masivos).',
        'Agua: potable, libre de aceites, acidos y cloruros. pH entre 6 y 8.',
    ]),
    pdf.callout('Por que el agua es critica',
        'La relacion agua/cemento (a/c) es el factor mas importante de la resistencia. '
        'Cada litro de agua adicional que agregas para hacer la mezcla "mas manejable" '
        'puede reducir la resistencia final hasta un 15%. Usa aditivos plastificantes '
        'si necesitas mayor trabajabilidad sin agregar agua.',
        'key'),

    pdf.section(2, 'Proporciones y resistencias por uso'),
    pdf.body('La resistencia del concreto se mide en kg/cm2 (sistema metrico) o MPa. '
             'En Mexico, los reglamentos de construccion locales especifican la resistencia minima segun el elemento:'),
    pdf.data_table(
        ['Uso del concreto', 'Proporcion en volumen', 'Resistencia f\'c', 'Agua/Cemento max'],
        [
            ['Firme de piso (sin carga)', '1:3:5', '100 kg/cm2', '0.65'],
            ['Losa de azotea residencial', '1:2:4', '150 kg/cm2', '0.55'],
            ['Losa de entrepiso', '1:2:3', '200 kg/cm2', '0.50'],
            ['Cimentacion y trabes', '1:1.5:3', '250 kg/cm2', '0.45'],
            ['Columnas estructurales', '1:1:2', '300 kg/cm2', '0.40'],
        ],
        col_widths=[60, 42, 38, 34],
        title='Tabla 1. Proporciones y resistencias por elemento estructural'
    ),

    pdf.section(3, 'Calculo exacto de materiales por m3'),
    pdf.body('Por cada metro cubico (m3) de concreto preparado en obra, necesitas los siguientes materiales:'),
    pdf.data_table(
        ['Proporcion', 'Cemento (bolsas 50kg)', 'Arena (m3)', 'Grava (m3)', 'Agua (litros)'],
        [
            ['1:3:5 (f\'c=100)', '5.5', '0.62', '1.04', '155'],
            ['1:2:4 (f\'c=150)', '7.0', '0.56', '0.84', '175'],
            ['1:2:3 (f\'c=200)', '8.5', '0.55', '0.83', '190'],
            ['1:1.5:3 (f\'c=250)', '10.0', '0.50', '0.75', '200'],
        ],
        col_widths=[40, 38, 32, 32, 32],
        title='Tabla 2. Materiales por m3 de concreto'
    ),
    pdf.callout('Formula rapida',
        'Calcula el volumen de concreto: largo x ancho x espesor = m3. '
        'Multiplica por los factores de la tabla. Agrega siempre un 10% por merma, '
        'derrames y ajustes. Para losas de mas de 20 m3, evalua concreto premezclado.',
        'tip'),

    pdf.section(4, 'Proceso de vaciado profesional'),
    pdf.bullet([
        'Preparacion de cimbra: verificar plomada, nivel y sellado de juntas antes de mezclar.',
        'Mezclado: usa revolvedora de 1 saco para homogeneidad. Tiempo minimo 3 minutos.',
        'Vaciado en capas: no mas de 30 cm por capa para facilitar la vibracion.',
        'Vibracion: introduce el vibrador de inmersion cada 50 cm, extrae lentamente (1 cm/seg).',
        'No vibrar en exceso: produce segregacion de agregados (grava al fondo, pasta arriba).',
        'Acabado de superficie: enlisa con regla y flota metalica. No repasar con agua.',
        'Tiempo de desencofrado: esperar al menos 72 horas antes de retirar cimbra lateral.',
    ]),

    pdf.section(5, 'Curado y control de calidad'),
    pdf.body('El curado es la etapa que mas se omite y la que mas afecta la resistencia final. '
             'Sin curado adecuado, el concreto puede perder hasta el 40% de su resistencia potencial.'),
    pdf.bullet([
        'Curado humedo: cubre con plastico o costales mojados durante 7 dias minimo (28 dias para estructurales).',
        'Curado quimico: aplica membrana de curado en aerosol sobre la superficie fresca.',
        'Temperatura: no colar cuando la temperatura sea menor a 5 C ni mayor a 35 C.',
        'Control de resistencia: solicita cilindros de prueba (15x30 cm) si el proyecto lo amerita.',
        'Toma de muestras: 1 muestra por cada 50 m3 de concreto colocado.',
    ]),

    pdf.section(6, 'Errores comunes y como evitarlos'),
    pdf.callout('Agregar agua en obra',
        'Es el error mas frecuente. Los albañiles agregan agua para hacer la mezcla mas "chistosa" (fluida). '
        'Esto reduce la resistencia drasticamente. La solucion correcta es usar un aditivo plastificante '
        '(superplastificante) que mejora la trabajabilidad sin comprometer la resistencia.',
        'error'),
    pdf.callout('Colar con sol directo',
        'El sol directo sobre la superficie puede provocar fisurado plastico en los primeros 30 minutos '
        'si el viento es seco. Protege la superficie con sombra provisional y comienza el curado tan '
        'pronto como sea posible despues del acabado.',
        'warning'),
    pdf.callout('No vibrar el concreto',
        'El concreto sin vibrar tiene poros y "cangrejeras" que reducen la resistencia y permiten '
        'la entrada de humedad. Siempre usa vibrador de inmersion. El vibrado manual con varilla '
        'solo es aceptable para elementos menores a 0.05 m3.',
        'warning'),

    pdf.checklist_page('Control de calidad en concreto', [
        'Verificar la calidad y fecha de fabricacion del cemento (maximo 60 dias desde fabricacion)',
        'Comprobar que arena y grava esten limpias y sin exceso de finos',
        'Confirmar que el agua sea potable y sin contaminantes',
        'Revisar que la cimbra este plomada, nivelada y sin fugas',
        'Calcular exactamente los materiales por m3 antes de mezclar',
        'Usar relacion agua/cemento maxima segun resistencia requerida',
        'Mezclar minimo 3 minutos en revolvedora',
        'Vaciar en capas de maximo 30 cm',
        'Vibrar cada 50 cm con vibrador de inmersion',
        'Iniciar curado en las primeras 4 horas despues del vaciado',
        'Mantener humedo durante minimo 7 dias (28 para estructurales)',
        'No transitar sobre la losa antes de 72 horas',
        'Documentar fecha de colado para control de tiempos',
    ]),
    pdf.cta_page(),
)
},

# ─────────────────────────────────────────────────────────────── GUIDE 7
{
'id':7,'slug':'07-cuanto-cuesta-construir-casa-mexico',
'cat':'Costos MX',
'title':'Cuanto Cuesta Construir una Casa en Mexico en 2025',
'subtitle':'El dato que necesitas antes de aprobar cualquier presupuesto',
'stats':{'pages':10,'tables':5,'checklist':True},
'chapters':[
    'Panorama del mercado de construccion 2025',
    'Costos por m2 segun nivel de acabado',
    'Comparativa por estado y ciudad',
    'Desglose de costos por etapa de obra',
    'Costos ocultos que nadie te dice',
    'Estrategias para reducir el presupuesto 15-20%',
    'Checklist antes de contratar',
],
'build': lambda pdf: (
    pdf.cover('Costos de Construccion en Mexico', 'El dato que necesitas antes de aprobar cualquier presupuesto'),
    pdf.toc_page([
        ('Panorama del mercado de construccion 2025', 3),
        ('Costos por m2 segun nivel de acabado', 4),
        ('Comparativa por estado y ciudad en Mexico', 5),
        ('Desglose detallado por etapa de obra', 6),
        ('Costos ocultos que nadie te dice', 7),
        ('Estrategias para reducir el presupuesto 15-20%', 8),
        ('Checklist antes de contratar una empresa', 9),
    ]),
    pdf.add_page(),

    pdf.section(1, 'Panorama del mercado de construccion 2025',
        'El contexto economico define el precio. Entenderlo te da poder de negociacion.'),
    pdf.body(
        'En 2025, el costo de construccion residencial en Mexico ha aumentado aproximadamente '
        '12-18% respecto a 2022, impulsado por la inflacion de materiales importados, '
        'la depreciacion del peso en ciertos periodos y el incremento del salario minimo. '
        'Sin embargo, la construccion en Mexico sigue siendo entre 40-60% mas barata que '
        'en Estados Unidos o Canada para especificaciones equivalentes.'),
    pdf.callout('Dato clave del mercado',
        'El acero y el cemento, que representan el 25-35% del costo total de materiales, '
        'tienen precios indexados parcialmente al dolar. Cuando el tipo de cambio supera '
        'los $18-19 MXN/USD, es comun ver incrementos de 5-10% en el costo total.',
        'key'),
    pdf.body(
        'El mercado de construccion informal (sin empresa registrada ni contrato formal) '
        'sigue representando el 65-70% de la construccion residencial en Mexico. '
        'Si bien puede ser mas economico en el corto plazo, conlleva riesgos de '
        'garantia, calidad y legal que pueden costar mas a largo plazo.'),

    pdf.section(2, 'Costos por m2 segun nivel de acabado'),
    pdf.body('Los costos por metro cuadrado de construccion en Mexico varian significativamente '
             'segun la calidad de los acabados. Esta es la escala de referencia para 2025:'),
    pdf.data_table(
        ['Nivel', 'Costo/m2 (MXN)', 'Caracteristicas', 'Ejemplo tipico'],
        [
            ['Obra negra', '$5,800-$8,500', 'Sin acabados. Estructura, muros, instalaciones en bruto.', 'Ampliacion basica'],
            ['Economico', '$8,500-$13,000', 'Acabados basicos: piso ceramico, pintura vinilica, accesorios nacionales.', 'Casa de interes social'],
            ['Medio', '$13,000-$20,000', 'Estandar: porcelanato, muebles de cocina modulares, sanitarios importados.', 'Casa de clase media'],
            ['Premium', '$20,000-$32,000', 'Acabados de calidad: cuarzo, herrajes europeos, domotica basica.', 'Casa residencial'],
            ['Lujo', '$32,000+', 'Materiales importados, arquitecto de disenio, acabados exclusivos.', 'Casa de lujo'],
        ],
        col_widths=[28, 32, 74, 40],
        title='Tabla 1. Costo de construccion por m2 segun nivel (Mexico 2025)'
    ),
    pdf.callout('Ojo con las cotizaciones por m2',
        'Cuando un contratista te da un precio "por m2", siempre pregunta: '
        '¿incluye instalaciones hidraulicas, sanitarias y electricas? '
        '¿Incluye acabados de pisos y muros? ¿Incluye puertas y ventanas? '
        'Muchos cotizadores excluyen estas partidas y el precio "por m2" '
        'se vuelve engañoso.',
        'warning'),

    pdf.section(3, 'Comparativa por estado y ciudad en Mexico'),
    pdf.body('El costo de mano de obra varia entre un 25-40% dependiendo de la ciudad. '
             'Los materiales tienen variaciones menores (5-15%) por flete y disponibilidad local:'),
    pdf.data_table(
        ['Ciudad / Region', 'Indice de costo m.o.', 'Nivel medio (MXN/m2)', 'Notas'],
        [
            ['Ciudad de Mexico', '+35%', '$16,500-$22,000', 'Mayor demanda, acceso limitado, normativa estricta'],
            ['Monterrey, NL', '+30%', '$15,500-$21,000', 'Alta industrializacion, mano de obra escasa'],
            ['Guadalajara, JAL', '+20%', '$14,500-$19,500', 'Mercado dinamico, buenos proveedores locales'],
            ['Queretaro', '+15%', '$14,000-$18,500', 'Rapido crecimiento, costos en alza'],
            ['Merida, YUC', '+10%', '$13,500-$17,500', 'Clima humedo requiere materiales especiales'],
            ['Puebla', '+5%', '$13,000-$17,000', 'Buena disponibilidad de materiales regionales'],
            ['Interior del pais', 'Base 0%', '$11,500-$15,000', 'Ciudades medianas con menor costo de vida'],
        ],
        col_widths=[42, 28, 40, 64],
        title='Tabla 2. Indices de costo por ciudad (referencia base: promedio nacional)'
    ),

    pdf.section(4, 'Desglose detallado por etapa de obra'),
    pdf.data_table(
        ['Etapa de obra', '% del costo total', 'Descripcion'],
        [
            ['Proyecto y permisos', '3-5%', 'Diseno arquitectonico, planos estructurales, licencia de construccion'],
            ['Preliminares y cimentacion', '15-20%', 'Trazo, excavacion, plantilla, cimentacion corrida o losa de cimentacion'],
            ['Estructura', '20-25%', 'Columnas, trabes, losas. Incluye acero y concreto estructural'],
            ['Muros y tabiques', '10-15%', 'Block de concreto o tabique rojo. Incluye mortero y cadenas'],
            ['Instalaciones', '15-20%', 'Hidraulica, sanitaria, electrica, gas. A veces incluye datos y TV'],
            ['Acabados interiores', '15-20%', 'Pisos, azulejo, pintura, plafones, detalles de yeso'],
            ['Acabados exteriores', '5-8%', 'Fachada, banqueta, impermeabilizacion, pintura exterior'],
            ['Puertas y ventanas', '8-12%', 'Incluye herreria, vidrio, canceleria aluminio si aplica'],
            ['Cocina y banos equipados', '5-10%', 'Muebles, sanitarios, tarjas, accesorios, regaderas'],
        ],
        col_widths=[52, 28, 94],
        title='Tabla 3. Desglose porcentual por etapa de obra'
    ),

    pdf.section(5, 'Costos ocultos que nadie te dice'),
    pdf.body('Estos conceptos rara vez aparecen en la primera cotizacion y pueden aumentar '
             'el presupuesto original entre un 15-25%:'),
    pdf.bullet([
        'Estudio de suelo: $3,500-$12,000 MXN. Obligatorio para suelos blandos o zonas sismicas.',
        'Licencia de construccion: $8,000-$45,000 MXN segun municipio y m2 a construir.',
        'Conexion a servicios (agua, drenaje, luz): $15,000-$60,000 MXN en fraccionamientos nuevos.',
        'Supervision tecnica externa: 3-5% del costo total. Muy recomendable para obras medianas y grandes.',
        'Flete de materiales a zonas de dificil acceso: puede sumar 8-15% al costo de materiales.',
        'Contingencias e imprevistos: siempre reserva el 10% adicional para cambios y sorpresas.',
        'Impuestos y honorarios notariales: 4-8% del valor del inmueble al escriturar.',
    ]),
    pdf.callout('La regla del 10+10',
        'Al presupuesto inicial siempre suma 10% por imprevistos y 10% por "cambios de diseno" '
        '(que inevitablemente ocurren durante la obra). Un presupuesto bien calculado de $500,000 MXN '
        'debe tener una reserva de al menos $100,000 MXN antes de iniciar.',
        'tip'),

    pdf.section(6, 'Estrategias para reducir el presupuesto 15-20%'),
    pdf.bullet([
        'Compra materiales directamente al distribuidor, no en ferreteria de barrio (ahorro 10-15% en volumen).',
        'Construye en temporada seca (nov-abril): menor riesgo de retrasos por lluvias y mano de obra mas disponible.',
        'Simplifica el diseno: menos quiebres en muros y techo reducen el costo estructural hasta 12%.',
        'Usa block de concreto en lugar de tabique donde el clima lo permita: menor tiempo de obra.',
        'Elige materiales nacionales de primera calidad en lugar de importados: calidad similar, precio menor.',
        'Contrata por administracion (tu compras materiales) en lugar de contrato llave en mano: ahorro 8-12%.',
        'Solicita minimo 3 cotizaciones formales con especificaciones identicas para poder comparar.',
    ]),

    pdf.checklist_page('Antes de contratar una empresa constructora', [
        'Verificar que la empresa este registrada en el SAT y pueda emitir factura',
        'Solicitar referencias de al menos 3 obras anteriores similares y visitar una',
        'Revisar que el presupuesto incluya materiales, mano de obra Y administracion',
        'Exigir un contrato escrito con especificaciones tecnicas detalladas',
        'Confirmar que el contrato incluya clausulas de penalizacion por retraso',
        'Acordar un programa de obra calendarizado (fechas de inicio y termino por etapa)',
        'Definir forma de pago vinculada a avance de obra (no pagos anticipados globales)',
        'Reservar 10% del total como retension de garantia a 6 meses de entrega',
        'Contratar supervision tecnica independiente para obras mayores a $300,000 MXN',
        'Verificar que el proyecto tenga licencia de construccion vigente antes de iniciar',
        'Asegurarte de tener acceso a la obra en cualquier momento para supervision',
        'Documentar fotograficamente el avance de obra semana a semana',
    ]),
    pdf.cta_page(),
)
},

# ─────────────────────────────────────────────────────────────── GUIDE 8
{
'id':8,'slug':'08-precio-materiales-construccion-mexico',
'cat':'Costos MX',
'title':'Precio de Materiales de Construccion en Mexico 2025',
'subtitle':'Compra los materiales correctos al precio justo',
'stats':{'pages':9,'tables':4,'checklist':True},
'chapters':[
    'Tabla de precios actualizada 2025',
    'Como leer y comparar cotizaciones',
    'Compras por volumen y temporada',
    'Impacto del dolar y la inflacion',
    'Materiales nacionales vs importados',
    'Proveedores: ferreteria vs distribuidor',
    'Checklist de compra inteligente',
],
'build': lambda pdf: (
    pdf.cover('Costos de Construccion en Mexico', 'Compra los materiales correctos al precio justo'),
    pdf.toc_page([
        ('Tabla de precios de materiales 2025', 3),
        ('Como leer y comparar cotizaciones correctamente', 4),
        ('Compras por volumen y temporada', 5),
        ('Impacto del dolar y la inflacion en construccion', 6),
        ('Materiales nacionales vs. importados', 7),
        ('Donde comprar: ferreteria, distribuidor o CEDE', 8),
        ('Checklist de compra inteligente', 9),
    ]),
    pdf.add_page(),

    pdf.section(1, 'Tabla de precios de materiales 2025',
        'Precios de referencia para compras al menudeo en CDMX y zona metropolitana. '
        'Para otras ciudades aplica un factor regional de +/- 10-15%.'),
    pdf.data_table(
        ['Material', 'Unidad', 'Precio min (MXN)', 'Precio max (MXN)', 'Notas'],
        [
            ['Cemento Portland tipo I 50 kg', 'bolsa', '$175', '$215', 'Precio sujeto a temporada y marca'],
            ['Cemento blanco 20 kg', 'bolsa', '$145', '$185', 'Para juntas, repellados y decoracion'],
            ['Varilla corrugada #3 (3/8") 6m', 'pieza', '$88', '$115', 'Precio sube con el acero internacional'],
            ['Varilla corrugada #4 (1/2") 6m', 'pieza', '$155', '$195', 'Para vigas, losas y columnas principales'],
            ['Block de concreto 15x20x40 cm', 'pieza', '$14', '$22', 'Varia por region y fabricante local'],
            ['Tabique rojo recocido', 'pieza', '$4.50', '$7.50', 'Alta variacion regional'],
            ['Arena de construccion', 'm3', '$480', '$750', 'Incluye IVA y flete cercano'],
            ['Grava 3/4 pulgada triturada', 'm3', '$520', '$820', 'Flete puede duplicar el costo en zonas alejadas'],
            ['Impermeabilizante acrilico 19 L', 'cubeta', '$420', '$680', 'Marcas: Sika, Polyplast, Comex Resistol'],
            ['Membrana asfaltica 1x10 m', 'rollo', '$680', '$1,200', 'Espesor 3-4 mm, con o sin granulado'],
            ['Azulejo ceramico 30x30 cm', 'm2', '$110', '$320', 'Primera calidad disponible en Vitromex, Lamosa'],
            ['Porcelanato 60x60 cm', 'm2', '$230', '$650', 'Mayor rango de precio por acabado y origen'],
            ['Pintura vinilica interior 19 L', 'cubeta', '$650', '$1,400', 'Comex, Sayer, Sherwin, Vipsa'],
            ['Cemento adhesivo para piso 25 kg', 'bolsa', '$120', '$185', 'Tipo I para ceramica, tipo II para porcelanato'],
            ['Tubo PVC hidraulico 1/2" x 6 m', 'pieza', '$32', '$55', 'Clase 10, para red de agua fria'],
            ['Tubo PVC sanitario 4" x 3 m', 'pieza', '$95', '$155', 'Para bajadas de aguas negras'],
            ['Cable THW calibre 12 AWG', 'metro', '$12', '$18', 'Para circuitos de iluminacion residencial'],
            ['Cable THW calibre 10 AWG', 'metro', '$18', '$28', 'Para circuitos de contactos residenciales'],
        ],
        col_widths=[62, 16, 24, 24, 48],
        title='Tabla 1. Precios de referencia de materiales de construccion (Mexico 2025)'
    ),
    pdf.callout('Como usar esta tabla',
        'Los precios son rangos de referencia. El precio real depende de la ciudad, '
        'el volumen de compra, el proveedor y la temporada. Para proyectos mayores '
        'a $100,000 MXN en materiales, siempre solicita cotizacion formal.',
        'tip'),

    pdf.section(2, 'Como leer y comparar cotizaciones'),
    pdf.body('Una cotizacion incompleta puede llevarte a comparar precios de cosas diferentes. '
             'Aprende a leer y comparar correctamente:'),
    pdf.bullet([
        'Especificacion exacta: verifica que la marca, calibre, dimension y clase sean iguales en todas las cotizaciones.',
        'Precio unitario vs. precio de entrega: pide que el precio incluya IVA y flete al pie de obra.',
        'Vigencia: una cotizacion de materiales tiene vigencia maxima de 7 dias por la variabilidad de precios.',
        'Condiciones de pago: compara si el precio cambia segun pago al contado vs. credito.',
        'Minimos de compra: algunos distribuidores solo venden a partir de ciertos volumenes.',
        'Merma y desperdicio: al cantidad calculada agrega un 10-12% por cortes y desperdicios.',
    ]),
    pdf.data_table(
        ['Concepto', 'Ferreteria local', 'Distribuidor zona', 'Cede / mayorista'],
        [
            ['Precio por unidad', 'Alto (+20-30%)', 'Medio (base)', 'Bajo (-10-15%)'],
            ['Minimo de compra', 'Sin minimo', 'Medio (ej. palet)', 'Alto (carga completa)'],
            ['Credito disponible', 'Limitado', 'Si (con historial)', 'Si (con RFC activo)'],
            ['Entrega en obra', 'Si (local)', 'Si (zona amplia)', 'Variable (costo extra)'],
            ['Factura fiscal', 'No siempre', 'Si siempre', 'Si siempre'],
            ['Asesor tecnico', 'No', 'A veces', 'Si (especializado)'],
        ],
        col_widths=[50, 38, 45, 41],
        title='Tabla 2. Comparativa de tipos de proveedor'
    ),

    pdf.section(3, 'Compras por volumen y temporada'),
    pdf.bullet([
        'Volumen: comprar el material de toda la obra en una sola orden puede darte 10-20% de descuento.',
        'Temporada baja (enero-marzo): menor demanda, mas disponibilidad y mejores precios en mano de obra.',
        'Evita mayo-septiembre: temporada de lluvias y alta demanda = precios mas altos y entregas lentas.',
        'Anticipate al alza del acero: cuando el precio del acero sube en mercados internacionales, '
        'en Mexico tarda 2-4 semanas en reflejarse. Compra antes si tienes informacion del mercado.',
    ]),
    pdf.callout('Ahorro por volumen',
        'Un albañil comprando bolsas sueltas de cemento paga $215 MXN. '
        'Un cliente que compra 100 bolsas en un distribuidor puede pagar $175-185 MXN. '
        'La diferencia en una obra de 500 bolsas es $15,000-$20,000 MXN de ahorro real.',
        'key'),

    pdf.section(4, 'Impacto del dolar y la inflacion'),
    pdf.body('Los materiales de construccion en Mexico tienen diferentes grados de sensibilidad '
             'al tipo de cambio y a la inflacion:'),
    pdf.data_table(
        ['Material', 'Sensibilidad al dolar', 'Inflacion promedio anual'],
        [
            ['Acero y varilla', 'Alta (precio indexado)', '12-18% anual'],
            ['Cemento Portland', 'Media (energia y caliza)', '8-12% anual'],
            ['Tuberia PVC', 'Media (petroleo)', '10-14% anual'],
            ['Cable electrico (cobre)', 'Alta (bolsa de metales)', '15-20% anual'],
            ['Madera de importacion', 'Alta (EE.UU.)', '12-18% anual'],
            ['Arena y grava', 'Baja (local)', '5-8% anual'],
            ['Mano de obra', 'Baja (salario minimo)', '8-12% anual'],
        ],
        col_widths=[60, 52, 52],
        title='Tabla 3. Sensibilidad de materiales al tipo de cambio'
    ),

    pdf.checklist_page('Compra inteligente de materiales', [
        'Calcular el volumen exacto de cada material antes de cotizar',
        'Agregar 10% de merma al volumen calculado',
        'Solicitar cotizacion a minimo 3 proveedores con especificaciones identicas',
        'Verificar que las cotizaciones incluyan IVA y flete al pie de obra',
        'Revisar la vigencia de la cotizacion (maximo 7 dias)',
        'Pedir factura fiscal para todo material mayor a $500 MXN',
        'Verificar marcas y procedencia al recibir el material',
        'Almacenar el cemento elevado del suelo y cubierto de la humedad',
        'No mezclar lotes de cemento de diferentes fechas de fabricacion',
        'Registrar todo el material recibido en un control de almacen',
        'Comparar precio unitario incluido flete vs. precio de la obra',
        'Negociar condiciones de credito para materiales de alto costo',
    ]),
    pdf.cta_page(),
)
},

# ─────────────────────────────────────────────────────────────── GUIDE 9
{
'id':9,'slug':'09-calcular-cemento-para-losa',
'cat':'Fundamentos',
'title':'Como Calcular Cuanto Cemento Necesito para una Losa',
'subtitle':'Nunca compres de mas ni de menos en tu proxima losa',
'stats':{'pages':8,'tables':4,'checklist':False},
'chapters':[
    'Formulas de calculo volumetrico',
    'Proporciones 1:2:3 y 1:2:4 explicadas',
    'Calculo completo con ejemplos reales',
    'Espesores recomendados por uso',
    'Concreto mezclado vs. premezclado',
    'Calculo del acero de refuerzo',
    'Tabla de calculo rapido',
],
'build': lambda pdf: (
    pdf.cover('Fundamentos de Construccion', 'Nunca compres de mas ni de menos en tu proxima losa'),
    pdf.toc_page([
        ('Formulas de calculo volumetrico de concreto', 3),
        ('Proporciones 1:2:3 y 1:2:4 explicadas en detalle', 4),
        ('Ejemplos reales de calculo paso a paso', 5),
        ('Espesores de losa recomendados segun uso', 6),
        ('Concreto mezclado en obra vs. premezclado', 6),
        ('Como calcular el acero de refuerzo', 7),
        ('Tabla de calculo rapido para obras tipicas', 8),
    ]),
    pdf.add_page(),

    pdf.section(1, 'Formulas de calculo volumetrico',
        'Todo calculo de materiales parte del volumen de concreto que necesitas.'),
    pdf.body('La formula basica para calcular el volumen de concreto de una losa rectangular es:'),
    pdf.callout('Formula fundamental',
        'Volumen (m3) = Largo (m) x Ancho (m) x Espesor (m)\n'
        'Ejemplo: Losa de 8m x 5m con 12 cm de espesor = 8 x 5 x 0.12 = 4.8 m3\n'
        'IMPORTANTE: Siempre agrega 10% por merma y desperdicio: 4.8 x 1.10 = 5.28 m3',
        'key'),
    pdf.body('Para losas con forma irregular, dividela en rectangulos y suma los volumenes. '
             'Para losas con trabes incluidas, calcula el volumen de la losa y de cada trabe '
             'por separado y suma los resultados.'),

    pdf.section(2, 'Proporciones 1:2:3 y 1:2:4 explicadas'),
    pdf.body('La proporcion indica: partes de cemento : partes de arena : partes de grava (en volumen). '
             'Por cada m3 de concreto compactado en obra, los materiales necesarios son:'),
    pdf.data_table(
        ['Proporcion', 'Uso recomendado', 'Cemento (bolsas 50kg)', 'Arena (m3)', 'Grava (m3)', 'Agua (litros)'],
        [
            ['1:3:5', 'Firme de piso, banquetas', '5.5', '0.62', '1.04', '155'],
            ['1:2:4', 'Losa de azotea residencial', '7.0', '0.56', '0.84', '175'],
            ['1:2:3', 'Entrepiso, trabes, columnas', '8.5', '0.55', '0.83', '190'],
            ['1:1.5:3', 'Cimentacion, elementos criticos', '10.0', '0.50', '0.75', '200'],
        ],
        col_widths=[28, 50, 26, 22, 22, 26],
        title='Tabla 1. Materiales por m3 de concreto segun proporcion'
    ),
    pdf.callout('Por que los numeros no suman 1 m3',
        'Cuando mezclas 1 saco de cemento + 2 de arena + 3 de grava, no obtienes 6 volumenes. '
        'Obtienes menos, porque la arena y el cemento fino llenan los huecos entre la grava. '
        'Esto se llama "factor de compactacion". El factor tipico es 0.65-0.70.',
        'tip'),

    pdf.section(3, 'Ejemplos reales de calculo paso a paso'),
    pdf.body('EJEMPLO A: Losa de techo para una recamara de 4 m x 3.5 m, espesor 12 cm.'),
    pdf.bullet([
        'Volumen neto: 4.0 x 3.5 x 0.12 = 1.68 m3',
        'Con 10% de merma: 1.68 x 1.10 = 1.85 m3',
        'Proporcion 1:2:4: Cemento = 1.85 x 7.0 = 12.95 bolsas >> comprar 14 bolsas',
        'Arena: 1.85 x 0.56 = 1.04 m3 >> pedir 1.1 m3',
        'Grava: 1.85 x 0.84 = 1.55 m3 >> pedir 1.6 m3',
        'Agua estimada: 1.85 x 175 = 324 litros (aprox. 1 pipa de agua o 16 cubetas)',
    ], bold_prefix=False),
    pdf.body('EJEMPLO B: Losa de entrepiso de 10 m x 6 m, espesor 14 cm, incluye 3 trabes de 25x35 cm.'),
    pdf.bullet([
        'Losa: 10 x 6 x 0.14 = 8.4 m3',
        'Trabes (3 x 10m x 0.25m x 0.35m): 3 x 10 x 0.25 x 0.35 = 2.63 m3',
        'Total neto: 8.4 + 2.63 = 11.03 m3',
        'Con 10% merma: 11.03 x 1.10 = 12.13 m3 >> redondea a 12.5 m3',
        'Proporcion 1:2:3: Cemento = 12.5 x 8.5 = 106 bolsas >> pedir 110 bolsas',
        'Arena: 12.5 x 0.55 = 6.88 m3 >> pedir 7 m3',
        'Grava: 12.5 x 0.83 = 10.38 m3 >> pedir 11 m3',
    ], bold_prefix=False),
    pdf.callout('Cuándo conviene premezclado',
        'Si tu losa supera los 15-20 m3, el concreto premezclado (olla revolvedora) '
        'suele ser mas economico y de mejor calidad uniforme. Precio de referencia 2025: '
        '$1,850-$2,400 MXN/m3 colocado (incluye bombeo y mano de obra).',
        'tip'),

    pdf.section(4, 'Espesores de losa recomendados segun uso'),
    pdf.data_table(
        ['Tipo de losa', 'Espesor minimo', 'Espesor recomendado', 'Refuerzo minimo'],
        [
            ['Firme de piso (sin carga)', '8 cm', '10 cm', 'Malla 6x6-10/10'],
            ['Losa de azotea sin acceso', '10 cm', '12 cm', 'Malla + varilla perimetral'],
            ['Losa de azotea con acceso', '12 cm', '14 cm', 'Malla 6x6-6/6 + trabes'],
            ['Losa de entrepiso', '12 cm', '14-16 cm', 'Calculo estructural requerido'],
            ['Losa de cimentacion', '20 cm', '25 cm', 'Doble malla + varilla adicional'],
        ],
        col_widths=[52, 28, 32, 62],
        title='Tabla 2. Espesores de losa segun tipo y uso'
    ),

    pdf.section(5, 'Calculo del acero de refuerzo'),
    pdf.body('El acero de refuerzo (varilla corrugada) se coloca en una malla cuadricula. '
             'Para una losa residencial tipica de fc=150 kg/cm2:'),
    pdf.data_table(
        ['Separacion de varilla', 'Varilla #', 'Consumo aprox. (kg/m2)', 'Uso tipico'],
        [
            ['20 cm x 20 cm', '#3 (3/8")', '3.8 kg/m2', 'Losa azotea ligera'],
            ['15 cm x 15 cm', '#3 (3/8")', '5.1 kg/m2', 'Losa azotea con acceso'],
            ['20 cm x 20 cm', '#4 (1/2")', '6.7 kg/m2', 'Entrepiso con poca carga'],
            ['15 cm x 15 cm', '#4 (1/2")', '8.9 kg/m2', 'Entrepiso residencial'],
        ],
        col_widths=[38, 26, 40, 70],
        title='Tabla 3. Consumo de acero de refuerzo por m2 de losa'
    ),

    pdf.section(6, 'Tabla de calculo rapido para obras tipicas'),
    pdf.data_table(
        ['Losa tipica', 'Volumen (m3)', 'Cemento (bolsas)', 'Arena (m3)', 'Grava (m3)'],
        [
            ['Cochera 3x5m / e=10cm', '1.65', '12', '0.95', '1.45'],
            ['Recamara 4x4m / e=12cm', '2.11', '15', '1.18', '1.77'],
            ['Sala-comedor 5x6m / e=12cm', '3.96', '28', '2.21', '3.33'],
            ['Azotea casa 8x10m / e=12cm', '10.56', '75', '5.91', '8.87'],
            ['Losa entrepiso 8x6m / e=14cm', '7.39', '63', '4.06', '6.13'],
            ['Cimentacion 10x12m / e=25cm', '39.6', '396', '19.8', '29.7'],
        ],
        col_widths=[50, 24, 28, 22, 22],
        title='Tabla 4. Calculo rapido de materiales para losas tipicas (incluye 10% merma)'
    ),
    pdf.cta_page(),
)
},

# ─────────────────────────────────────────────────────────────── GUIDE 10
{
'id':10,'slug':'10-costo-remodelar-bano-mexico',
'cat':'Costos MX',
'title':'Cuanto Cuesta Remodelar un Bano Completo en Mexico',
'subtitle':'El presupuesto real que ningun contratista te va a dar',
'stats':{'pages':10,'tables':5,'checklist':True},
'chapters':[
    'Rangos de precio por tipo de remodelacion',
    'Desglose completo por partida',
    'Tabla de materiales con precios unitarios',
    'Mano de obra: como cotizar bien',
    'Tiempos de obra y como acortarlos',
    'Errores costosos que debes evitar',
    'Checklist de remodelacion de bano',
],
'build': lambda pdf: (
    pdf.cover('Costos de Construccion en Mexico', 'El presupuesto real que ningun contratista te va a dar'),
    pdf.toc_page([
        ('Rangos de precio por tipo de remodelacion', 3),
        ('Desglose completo por partida de trabajo', 4),
        ('Tabla de materiales con precios unitarios 2025', 5),
        ('Mano de obra: como cotizar y comparar', 6),
        ('Tiempos de obra y como acortarlos', 7),
        ('Errores costosos que debes evitar', 8),
        ('Checklist completo de remodelacion de bano', 9),
    ]),
    pdf.add_page(),

    pdf.section(1, 'Rangos de precio por tipo de remodelacion',
        'El costo depende del tamaño del baño (3-6 m2 tipicamente), '
        'calidad de materiales y si cambias la distribucion de plomeria.'),
    pdf.data_table(
        ['Nivel de remodelacion', 'Costo estimado (MXN)', 'Incluye', 'Tiempo'],
        [
            ['Solo cosmetics (pintura y accesorios)', '$3,500-$8,000', 'Pintura, espejo, accesorios basicos', '1-2 dias'],
            ['Remodelacion superficial', '$12,000-$22,000', 'Azulejo sobre azulejo, WC nuevo, accesorios', '3-5 dias'],
            ['Remodelacion estandar', '$22,000-$45,000', 'Retiro de azulejo, piso nuevo, WC, plomeria', '6-10 dias'],
            ['Remodelacion completa', '$45,000-$75,000', 'Todo lo anterior + cambio de distribucion', '10-16 dias'],
            ['Premium / lujo', '$75,000-$150,000+', 'Materiales importados, regadera de lluvia, domot.', '15-25 dias'],
        ],
        col_widths=[48, 36, 60, 30],
        title='Tabla 1. Rangos de precio por tipo de remodelacion de bano (Mexico 2025)'
    ),
    pdf.callout('La trampa de la remodelacion economica',
        'Remodelaciones superficiales (azulejo sobre azulejo) pueden ser tentadoras por el precio. '
        'El problema: el exceso de peso puede comprometer la adherencia a largo plazo y, '
        'si hay una fuga oculta, el daño a la estructura puede costar el doble de lo ahorrado. '
        'Siempre verifica el estado de impermeabilizacion antes de cubrir.',
        'warning'),

    pdf.section(2, 'Desglose completo por partida de trabajo'),
    pdf.data_table(
        ['Partida de trabajo', 'Costo min (MXN)', 'Costo max (MXN)', 'Factor de variacion'],
        [
            ['Demolicion y retiro de escombro', '$1,500', '$4,500', 'Tamaño del baño y acceso'],
            ['Impermeabilizacion (muros y piso)', '$2,200', '$5,500', 'Sistema y m2 de aplicacion'],
            ['Azulejo de muro (incluyendo adhesivo)', '$3,500', '$12,000', 'Material elegido y m2'],
            ['Piso ceramico o porcelanato', '$2,800', '$9,500', 'Material, formato y m2'],
            ['WC de doble descarga', '$2,200', '$12,000', 'Nacional vs. importado'],
            ['Lavabo y mezcladora', '$1,800', '$9,500', 'Marca y modelo elegidos'],
            ['Regadera y accesorios', '$1,500', '$8,000', 'Tipo: manual, sistema o lluvia'],
            ['Espejo con iluminacion LED', '$1,200', '$6,500', 'Tamaño y tipo de luz'],
            ['Accesorios (toallero, jabonera, etc.)', '$800', '$4,500', 'Material: cromado, acero, madera'],
            ['Mueble bajo lavabo (opcional)', '$2,500', '$12,000', 'Modular nacional vs. diseño'],
            ['Plomeria (redes de agua y drenaje)', '$3,500', '$9,000', 'Si se mueve la distribucion'],
            ['Instalacion electrica (foco, extractor)', '$1,800', '$4,500', 'Tipo de luminaria y extractor'],
            ['Mano de obra albanileria y acabados', '$6,000', '$14,000', 'Dias de trabajo y region'],
        ],
        col_widths=[62, 26, 26, 60],
        title='Tabla 2. Desglose de partidas de remodelacion de baño estandar (4-5 m2)'
    ),

    pdf.section(3, 'Tabla de materiales con precios unitarios 2025'),
    pdf.data_table(
        ['Material especifico', 'Und', 'Precio min', 'Precio max', 'Marca referencia'],
        [
            ['Azulejo ceramico 20x40 cm', 'm2', '$130', '$280', 'Vitromex, Lamosa'],
            ['Azulejo gran formato 30x60 cm', 'm2', '$210', '$420', 'Lamosa, Porcelanite'],
            ['Porcelanato esmaltado 45x45 cm', 'm2', '$280', '$650', 'Interceramic, Porcelanite'],
            ['Piso antiderrapante bano 30x30', 'm2', '$160', '$380', 'Vitromex, Lourdes'],
            ['Mosaico veneciano decorativo', 'm2', '$450', '$1,400', 'Vitromex, importado'],
            ['WC Zurich doble descarga nacional', 'pza', '$1,900', '$2,800', 'Merlot, Rotoplas, Lourdes'],
            ['WC Celite / Interceramic estandar', 'pza', '$2,800', '$5,500', 'Celite, American Standard'],
            ['WC Duravit / Kohler importado', 'pza', '$6,000', '$18,000', 'Duravit, Kohler, Grohe'],
            ['Lavabo de empotrar blanco', 'pza', '$650', '$2,200', 'Nacionales variados'],
            ['Lavabo de sobreponer', 'pza', '$1,200', '$6,500', 'Interceramic, importados'],
            ['Mezcladora monomando', 'pza', '$800', '$4,500', 'FV, Helvex, Kohler'],
            ['Regadera manual sencilla', 'pza', '$350', '$1,800', 'Mexicana, Grohe basico'],
            ['Set de regadera tipo lluvia', 'pza', '$2,800', '$9,500', 'Grohe, Hansgrohe'],
            ['Adhesivo ceramico 25 kg', 'bolsa', '$120', '$185', 'Sika, Bostik, Laticrete'],
            ['Fragua epoxica 1 kg', 'kg', '$145', '$240', 'Sika, Bostik, Laticrete'],
        ],
        col_widths=[62, 10, 22, 22, 58],
        title='Tabla 3. Precios unitarios de materiales para bano (Mexico 2025)'
    ),

    pdf.section(4, 'Mano de obra: como cotizar y comparar'),
    pdf.data_table(
        ['Tipo de mano de obra', 'Precio min/dia', 'Precio max/dia', 'Notas'],
        [
            ['Albanil (maestro de obra)', '$550', '$900', 'Incluye herramienta personal'],
            ['Ayudante de albanileria', '$280', '$450', 'Para acarreo y mezcla'],
            ['Plomero (instalaciones)', '$700', '$1,200', 'Por dia o por punto ($350-600)'],
            ['Electricista', '$650', '$1,100', 'Por dia o por punto ($350-500)'],
            ['Colocador de azulejo (m2)', '$85', '$180', 'Por m2 colocado e instalado'],
        ],
        col_widths=[58, 26, 26, 64],
        title='Tabla 4. Precios de mano de obra especializados (Mexico 2025)'
    ),
    pdf.callout('Contrata por administracion',
        'En lugar de un contrato "llave en mano" donde el contratista compra los materiales, '
        'considera contratar solo la mano de obra y comprar tu los materiales directamente. '
        'Ahorro tipico: 12-18% del costo total, a cambio de mas tiempo de supervision de tu parte.',
        'tip'),

    pdf.section(5, 'Errores costosos que debes evitar'),
    pdf.callout('No impermeabilizar antes del azulejo',
        'El 40% de las filtraciones en banos de Mexico ocurren por no impermeabilizar '
        'correctamente antes de colocar el azulejo. El impermeabilizante debe cubrir muros '
        'hasta 30 cm de altura minimo y todo el piso. Costo de reparacion posterior: '
        '$15,000-$35,000 MXN vs. $2,500 de impermeabilizacion correcta desde el inicio.',
        'error'),
    pdf.callout('Cambiar la ubicacion del WC',
        'Mover el WC mas de 60 cm de su posicion original requiere picar la losa para '
        'reubicar el bajante sanitario de 4 pulgadas. Esto puede agregar $8,000-$15,000 '
        'MXN al presupuesto y 3-4 dias adicionales de obra. Evalua si el cambio de diseno '
        'justifica ese costo antes de decidir.',
        'warning'),
    pdf.callout('Contratar al primer presupuesto recibido',
        'Nunca aceptes el primer presupuesto sin comparar. La variacion entre un contratista '
        'y otro puede ser del 30-50% por la misma obra. Solicita minimo 3 cotizaciones '
        'con el mismo alcance y materiales especificados.',
        'tip'),

    pdf.checklist_page('Remodelacion de bano', [
        'Definir el presupuesto maximo antes de elegir materiales',
        'Medir exactamente el bano: ancho, largo y altura libre',
        'Decidir si se cambia la distribucion de plomeria (impacta costo significativamente)',
        'Solicitar 3 cotizaciones con el mismo alcance de trabajo',
        'Verificar referencias y trabajo anterior del albanil contratado',
        'Firmar contrato con descripcion de materiales, tiempos y forma de pago',
        'Comprar materiales antes de comenzar (no pausar la obra por falta de material)',
        'Verificar la impermeabilizacion antes de colocar azulejo',
        'Revisar que las pendientes del piso desaguen correctamente hacia la coladera',
        'Confirmar la instalacion electrica (tierra fisica en todos los contactos)',
        'Hacer prueba de agua antes de cerrar muros y colocar azulejo',
        'Revisar que las juntas de azulejo esten parejas y bien fraguadas',
        'Verificar funcionamiento del extractor de aire',
        'Solicitar factura por todos los materiales y mano de obra',
        'Retener el 10% del pago final hasta verificar que no haya filtraciones (30 dias)',
    ]),
    pdf.cta_page(),
)
},

# ─────────────────────────────────────────────────────────────── GUIDE 11
{
'id':11,'slug':'11-costo-pintar-casa-mexico',
'cat':'Costos MX',
'title':'Costo de Pintar una Casa en Mexico: Precio por m2',
'subtitle':'Pinta tu casa con presupuesto justo y resultado profesional',
'stats':{'pages':8,'tables':3,'checklist':True},
'chapters':[
    'Tipos de pintura y cual usar en cada zona',
    'Tabla de precios por m2 mano de obra',
    'Tabla de precios por tipo de pintura',
    'Como calcular litros y rendimiento',
    'Preparacion de superficie: la clave del resultado',
    'Interior vs. exterior vs. fachada',
    'Checklist de proyecto de pintura',
],
'build': lambda pdf: (
    pdf.cover('Costos de Construccion en Mexico', 'Pinta tu casa con presupuesto justo y resultado profesional'),
    pdf.toc_page([
        ('Tipos de pintura y cual usar en cada zona', 3),
        ('Precios de mano de obra por m2 (2025)', 4),
        ('Precios de pintura por tipo y calidad', 5),
        ('Como calcular litros y rendimiento exacto', 6),
        ('Preparacion de superficie: la clave del exito', 7),
        ('Interior vs. exterior vs. fachada', 7),
        ('Checklist de proyecto de pintura', 8),
    ]),
    pdf.add_page(),

    pdf.section(1, 'Tipos de pintura y cual usar en cada zona'),
    pdf.data_table(
        ['Tipo de pintura', 'Uso recomendado', 'Durabilidad', 'Precio referencia/L'],
        [
            ['Vinilica interior mate', 'Recamaras, pasillos, salas', '3-5 años', '$65-$130'],
            ['Vinilica interior satinado', 'Cocinas y banos interiores', '4-6 años', '$80-$145'],
            ['Acrilica exterior', 'Fachadas y muros exteriores', '5-8 años', '$95-$185'],
            ['Elastomerica / flexo', 'Fachadas con fisuras, exteriores', '7-12 años', '$130-$220'],
            ['Epoxica para pisos', 'Cocheras, bodegas, pisos industriales', '5-10 años', '$170-$290'],
            ['Impermeabilizante pintable', 'Azoteas y muros humedos', '2-5 años', '$85-$160'],
            ['Esmalte sintetico', 'Herreria, puertas metalicas', '4-7 anos', '$95-$175'],
            ['Pintura para alberca', 'Interiores de alberca', '2-4 años', '$220-$480'],
        ],
        col_widths=[50, 48, 26, 50],
        title='Tabla 1. Tipos de pintura y aplicacion recomendada'
    ),

    pdf.section(2, 'Precios de mano de obra por m2 (2025)'),
    pdf.data_table(
        ['Tipo de trabajo', 'Ciudad interior', 'CDMX/GDL/MTY', 'Con textura / estucado'],
        [
            ['Pintura interior (2 manos)', '$32-$48/m2', '$55-$78/m2', '$90-$140/m2'],
            ['Pintura exterior (2 manos)', '$42-$60/m2', '$65-$90/m2', '$100-$160/m2'],
            ['Pintura de fachada (con andamio)', '$55-$75/m2', '$80-$110/m2', '$120-$180/m2'],
            ['Pintura de herreria por m2', '$45-$65/m2', '$65-$95/m2', 'N/A'],
            ['Pintura epoxica piso', '$65-$90/m2', '$90-$130/m2', 'N/A'],
        ],
        col_widths=[54, 32, 32, 56],
        title='Tabla 2. Precios de mano de obra para pintura por region (Mexico 2025)'
    ),
    pdf.callout('Como pagar la mano de obra',
        'Lo mas comun es pagar por m2 terminado. Antes de contratar, '
        'mide la superficie real (incluyendo plafones si aplica) y establece '
        'en el contrato que el pago es por m2 efectivamente pintado, no por dia. '
        'Esto incentiva al pintor a trabajar rapido y bien.',
        'tip'),

    pdf.section(3, 'Como calcular litros y rendimiento'),
    pdf.body('El rendimiento de una pintura indica cuantos m2 cubre un litro en una mano. '
             'Consulta siempre la ficha tecnica del producto:'),
    pdf.data_table(
        ['Tipo de pintura', 'Rendimiento tipico', 'M2 por cubeta 19 L (1 mano)'],
        [
            ['Vinilica economica', '10-12 m2/L', '190-228 m2'],
            ['Vinilica calidad media', '11-13 m2/L', '209-247 m2'],
            ['Vinilica premium', '12-14 m2/L', '228-266 m2'],
            ['Acrilica exterior', '9-11 m2/L', '171-209 m2'],
            ['Elastomerica', '5-8 m2/L', '95-152 m2 (se aplica en capas gruesas)'],
            ['Epoxica de piso', '6-8 m2/L', '114-152 m2'],
        ],
        col_widths=[50, 36, 88],
        title='Tabla 3. Rendimiento por tipo de pintura (superficie lisa, 1 mano)'
    ),
    pdf.body('FORMULA DE CALCULO:\nLitros necesarios = (m2 totales / rendimiento) x numero de manos\n'
             'Ejemplo: 120 m2 de muros interiores, pintura vinilica calidad media (12 m2/L), 2 manos:\n'
             '(120 / 12) x 2 = 20 litros = 2 cubetas de 10 litros + 1 cuarto adicional para retoques.'),

    pdf.section(4, 'Preparacion de superficie'),
    pdf.body('El 70% del resultado final depende de la preparacion. No saltes este paso:'),
    pdf.bullet([
        'Limpieza: retira polvo, grasa, hongos y pintura suelta con espatula y lija No. 80.',
        'Sellador / fijador: aplica 1 mano sobre superficies nuevas o porosas. Reduce consumo de pintura 15-20%.',
        'Masillado: rellena grietas y hoyos con masilla plastica o yeso. Lija cuando seque.',
        'Lijado fino: usa lija No. 120-150 para suavizar el sellador antes de pintar.',
        'Tiempo de secado: respeta los tiempos entre capas (minimo 2 horas entre manos de vinilica).',
        'Temperatura: no pintes con temperatura menor a 8 C ni mayor a 38 C.',
    ]),

    pdf.checklist_page('Proyecto de pintura', [
        'Medir la superficie total (muros, plafones, puertas si aplica)',
        'Definir tipo de pintura y calidad para cada zona',
        'Calcular litros necesarios con la formula de rendimiento',
        'Solicitar 2-3 cotizaciones de mano de obra con el mismo alcance',
        'Comprar 10% mas de pintura de la calculada para retoques futuros',
        'Cubrir pisos, muebles y herrajes antes de iniciar',
        'Aplicar sellador en superficies nuevas o muy porosas',
        'Masilla y lijar grietas y hoyos antes de la primera mano',
        'Respetar tiempos de secado entre manos (no acelerar con ventiladores directos)',
        'Verificar el color con una muestra pequena antes de pintar toda la habitacion',
        'Aplicar 2 manos minimo en todos los casos',
        'Retirar cinta de enmascarar mientras la pintura aun esta fresca',
        'Guardar pintura sobrante correctamente sellada para retoques',
        'Pedir factura por materiales y mano de obra',
    ]),
    pdf.cta_page(),
)
},

# ─────────────────────────────────────────────────────────────── GUIDES 2-6, 12-16 (condensed but solid)
{
'id':2,'slug':'02-instalacion-tuberia-pvc',
'cat':'Plomeria',
'title':'Instalacion de Tuberia PVC',
'subtitle':'Instalaciones sin fugas y a norma desde el primer dia',
'stats':{'pages':8,'tables':2,'checklist':True},
'chapters':['Tipos de tuberia PVC en Mexico','Dimensionamiento hidraulico','Corte y pegado profesional','Redes sanitarias y pendientes','Prueba hidrostatica','Normativa NOM y CONAGUA','Checklist de instalacion'],
'build': lambda pdf: _build_generic(pdf, 'Plomeria', 'Instalaciones sin fugas y a norma desde el primer dia', [
    (1,'Tipos de tuberia PVC en Mexico',None,[
        'Hidraulica (presion): soporta 6-16 kg/cm2. Color blanco o gris, marcada con clase (6, 10, 13, 16).',
        'Sanitaria (drenaje): trabaja por gravedad. Pared delgada, color beige o gris, sin presion.',
        'CPVC: para agua caliente hasta 93 C. Color crema. Uso en calefones y termos.',
        'PVC electrico: para canalizacion de cables. Nunca uses tuberia electrica para agua.',
    ], None,
    [('Tipo','Clase','Presion maxima (kg/cm2)','Color tipico','Uso principal'),
     [['Hidraulica','Clase 10','10 kg/cm2','Gris/Blanco','Red de agua fria potable'],
      ['Hidraulica','Clase 13','13 kg/cm2','Gris','Agua fria presion media-alta'],
      ['Sanitaria','--','Sin presion','Beige','Drenaje y aguas residuales'],
      ['CPVC','Clase 16','16 kg/cm2 a 82 C','Amarillo/Crema','Agua caliente sanitaria']],
     [20,14,28,20,72],'Tabla 1. Tipos de tuberia PVC por uso'],
    'El PVC es el material mas utilizado en instalaciones hidraulicas y sanitarias en Mexico por su '
    'bajo costo, facil instalacion, resistencia a la corrosion y larga durabilidad (50+ anos cuando '
    'se instala correctamente). Es resistente a la mayoria de acidos domesticos y solventes diluidos.'
    ),
    (2,'Dimensionamiento hidraulico',None,[
        'Alimentacion principal domiciliaria: 3/4 pulgada (19 mm) para casas hasta 3 recamaras.',
        'Red interior de distribucion: 1/2 pulgada (13 mm) para ramales individuales.',
        'Bajante de aguas negras (WC): 4 pulgadas (100 mm) minimo, segun NOM-002-CNA.',
        'Ramal de lavabo, regadera, fregadero: 2 pulgadas (50 mm) de diametro.',
        'Bajante pluvial: 3 pulgadas (75 mm) por cada 25 m2 de azotea drenada.',
    ], None, None, None),
    (3,'Proceso de corte y pegado',None,[
        'Usa cortapipas para cortes perfectamente perpendiculares sin rebabas.',
        'Lija los extremos cortados con lija de agua No. 80 para eliminar filos.',
        'Aplica primer en ambas superficies (tubo y cople): espera 30 segundos.',
        'Aplica cemento solvente en ambas superficies: actua rapido, tienes 20-30 segundos.',
        'Inserta el tubo en el cople girando 1/4 de vuelta para distribuir el pegamento.',
        'Manten presion por 30 segundos. No muevas la union por 15 minutos.',
        'Tiempo de curado completo: 24 horas antes de presurizar.',
    ], None, None, None),
], [
    'Verificar que el diametro de tuberia sea el correcto para cada ramal',
    'Usar primer antes del cemento solvente en todos los casos',
    'Aplicar cemento solvente en tubo y accesorio simultaneamente',
    'No presurizar la instalacion antes de 24 horas de curado',
    'Realizar prueba hidrostatica a 1.5x la presion de trabajo (15-16 kg/cm2)',
    'Verificar pendientes minimas: 2% en sanitaria (2 cm por metro lineal)',
    'Proteger la tuberia de golpes mecanicos en zonas transitadas',
    'Marcar en plano la ubicacion exacta de toda la tuberia enterrada',
])
},

{
'id':3,'slug':'03-instalaciones-electricas-residenciales',
'cat':'Electrico',
'title':'Instalaciones Electricas Residenciales',
'subtitle':'Circuitos seguros, a norma y sin sorpresas en el tablero',
'stats':{'pages':9,'tables':3,'checklist':True},
'chapters':['Fundamentos de electricidad residencial','Calibres y protecciones','Diseño de circuitos por zona','Normativa NOM-001-SEDE','Tablero y tierra fisica','GFCI y circuitos dedicados','Checklist de seguridad electrica'],
'build': lambda pdf: _build_generic(pdf, 'Instalaciones Electricas', 'Circuitos seguros, a norma y sin sorpresas en el tablero', [
    (1,'Fundamentos de electricidad residencial',None,[
        'Voltaje en Mexico: 127 V monofasico (residencial) y 220 V bifasico (equipos especiales).',
        'Frecuencia: 60 Hz (igual que EE.UU., diferente a Europa que usa 50 Hz).',
        'Corriente alterna (CA): la que llega a tu casa. La corriente directa (CD) es la de baterias.',
        'La potencia (watts) = voltaje x corriente. Un contacto de 20 A a 127 V puede dar 2,540 W.',
    ], None,
    [('Concepto','Formula / Valor','Aplicacion practica'),
     [['Ley de Ohm (V=IR)','Voltaje = Corriente x Resistencia','Base de todo calculo electrico'],
      ['Potencia','P = V x I (watts)','Calcular carga de un circuito'],
      ['Factor de demanda','60-80% de la carga instalada','Para dimensionar el tablero'],
      ['Caida de tension','Max 3% en interior, 5% total','Define el calibre de cable'],
      ['Corriente de corto circuito','Depende de la red CFE','Dimensiona los interruptores']],
     [44,44,86],'Tabla 1. Conceptos fundamentales de instalaciones electricas'],
    None),
    (2,'Calibres de cable y protecciones por zona',None, [
        'Iluminacion general: Cable THW calibre 12 AWG, interruptor termomagntico 15 A.',
        'Contactos generales (sala, rec.): Cable 10 AWG, interruptor 20 A.',
        'Aire acondicionado split (mini-split): Cable 10 AWG, interruptor 20 A dedicado.',
        'Estufa electrica o horno de pared: Cable 8 AWG, interruptor 40 A dedicado a 220 V.',
        'Lavadora: Cable 10 AWG, interruptor 20 A, tierra fisica obligatoria.',
        'Secadora electrica: Cable 8 AWG, interruptor 30 A a 220 V.',
    ], None,
    [('Zona','Calibre recomendado','Interruptor','Observaciones'),
     [['Iluminacion general','12 AWG','15 A','Maximo 10 puntos de luz por circuito'],
      ['Contactos residenciales','10 AWG','20 A','Maximo 8 contactos por circuito'],
      ['Aire acondicionado','10 AWG','20 A','Circuito dedicado, sin compartir'],
      ['Estufa electrica','8 AWG','40 A 240V','Circuito dedicado bifasico'],
      ['Refrigerador','12 AWG','15 A','Circuito dedicado recomendado'],
      ['Horno de microondas','12 AWG','20 A','Circuito dedicado si es >1,000 W'],
      ['Boiler electrico','10 AWG','30 A','Circuito dedicado, tierra fisica']],
     [48,32,26,68],'Tabla 2. Calibres de cable por zona y equipo'],
    None),
    (3,'Normativa NOM-001-SEDE en Mexico',None,[
        'Toda instalacion nueva debe usar tubo conduit EMT metalico o conduit PVC.',
        'Los cables deben pasar por conduit: nunca cable a la vista ni adosado en muros.',
        'Tablero principal: interruptor termomagntico (no fusibles de cuchillo) para cada circuito.',
        'Tierra fisica: obligatoria en toda instalacion. Se conecta desde el tablero al electrodo.',
        'Contactos en banos y cocinas: deben ser GFCI (proteccion contra falla a tierra).',
        'Separacion neutro-tierra: en el tablero principal, el neutro y la tierra van a barras separadas.',
        'Distancia maxima entre soporte de conduit: 1.5 m en tramos horizontales.',
    ], None,
    [('Requisito NOM-001-SEDE','Aplica en','Consecuencia de incumplimiento'),
     [['Conduit para todo cable','100% de la instalacion','CFE puede negar conexion; riesgo de incendio'],
      ['Interruptores termomagnticos','Tablero principal','Sobrecalentamiento, riesgo de incendio'],
      ['Tierra fisica en tablero','Instalacion completa','Riesgo de electrocucion'],
      ['GFCI en banos y cocinas','Contactos en zonas humedas','Riesgo de electrocucion por humedad'],
      ['Caja de registro en empalmes','Todos los empalmes','Imposible detectar fallas ocultas']],
     [68,38,68],'Tabla 3. Requisitos criticos NOM-001-SEDE'],
    None),
], [
    'Hacer plano de distribucion de circuitos antes de instalar',
    'Usar calibre 12 AWG minimo para iluminacion y 10 AWG para contactos',
    'Instalar todos los cables dentro de conduit EMT o PVC',
    'Conectar tierra fisica en todos los contactos (3 hilos: fase, neutro, tierra)',
    'Instalar interruptores GFCI en banos, cocinas y areas exteriores',
    'Verificar que el tablero tenga interruptor termomagntico para cada circuito',
    'No conectar mas de 10 puntos de luz en un mismo circuito',
    'No conectar mas de 8 contactos en un mismo circuito de 20 A',
    'Instalar circuito dedicado para aire acondicionado, lavadora y refrigerador',
    'Probar con multimetro cada circuito antes de encender el tablero',
    'Solicitar revision y aprobacion de CFE para conexiones nuevas',
    'Documentar en plano la ubicacion de todos los circuitos y tablero',
])
},
]

# ═══════════════════════════════════════════════════════════════════════
#  HELPER: generic multi-section builder
# ═══════════════════════════════════════════════════════════════════════
def _build_generic(pdf, cat_label, subtitle, sections, checklist_items):
    pdf.cover(cat_label, subtitle)
    # TOC (simplified)
    toc = [(s[1], 3 + i) for i, s in enumerate(sections)]
    if checklist_items:
        toc.append(('Checklist profesional', 3 + len(sections)))
    pdf.toc_page(toc)
    pdf.add_page()
    for sec in sections:
        num, title, intro, bullets, tip, table_data, body_text = (sec + (None,)*7)[:7]
        pdf.section(num, title, intro or '')
        if body_text:
            pdf.body(body_text)
        if bullets:
            pdf.bullet(bullets)
        if table_data:
            headers, rows, col_widths, t_title = table_data
            pdf.data_table(headers, rows, col_widths, t_title)
        if tip:
            pdf.callout(None, tip, 'tip')
    if checklist_items:
        pdf.checklist_page(pdf.guide['title'], checklist_items)
    pdf.cta_page()


# ═══════════════════════════════════════════════════════════════════════
#  REMAINING GUIDES (compact but professional)
# ═══════════════════════════════════════════════════════════════════════
REMAINING = [4,5,6,12,13,14,15,16]
REMAINING_DATA = {
4:{'slug':'04-estructuras-acero-concreto','cat':'Avanzado','title':'Estructuras de Acero y Concreto','subtitle':'Estructuras robustas para zonas sismicas de alta demanda'},
5:{'slug':'05-mamposteria-muros-block','cat':'Fundamentos','title':'Mamposteria y Muros de Block','subtitle':'Muros plomados y resistentes desde la primera hilada'},
6:{'slug':'06-impermeabilizacion-azoteas','cat':'Avanzado','title':'Impermeabilizacion de Azoteas','subtitle':'Azoteas impermeables por 10 a 15 anos garantizados'},
12:{'slug':'12-instalacion-electrica-precios-nom-mexico','cat':'Electrico','title':'Instalacion Electrica en Casa: Precios y Normativa NOM en Mexico','subtitle':'Instalaciones seguras y a norma en Mexico sin improvisar'},
13:{'slug':'13-porcelanato-vs-ceramica-mexico','cat':'Avanzado','title':'Porcelanato vs Ceramica: Cual Conviene y Cuanto Cuesta en Mexico','subtitle':'Elige el piso correcto y ahorra en materiales y mano de obra'},
14:{'slug':'14-presupuesto-cocina-pequena-mexico','cat':'Costos MX','title':'Presupuesto para Cocina Pequena en Mexico','subtitle':'La cocina que quieres, con el presupuesto que tienes'},
15:{'slug':'15-impermeabilizacion-azotea-costos-mexico','cat':'Costos MX','title':'Impermeabilizacion de Azotea en Mexico: Tipos y Costo por m2','subtitle':'Deja de perder dinero en filtraciones que se repiten'},
16:{'slug':'16-block-cemento-vs-ladrillo-mexico','cat':'Fundamentos','title':'Block de Cemento vs Ladrillo Rojo: Comparativa de Costos en Mexico','subtitle':'La decision que define el costo y velocidad de tu obra'},
}

REMAINING_CONTENT = {
4: dict(
    sections=[
        (1,'Sistemas estructurales mixtos acero-concreto',None,[
            'Marco rigido de acero con losa de concreto: el sistema mas eficiente para Mexico.',
            'Las columnas de acero resisten tension y compresion. El concreto solo compresion.',
            'La combinacion aprovecha las virtudes de ambos materiales reduciendo costos.',
            'Aplicacion tipica: naves industriales, edificios de 3-10 pisos, estacionamientos.',
        ],None,None,None),
        (2,'Perfiles de acero estructural en Mexico',None, None,None,
        [('Perfil','Descripcion','Uso tipico','Peso (kg/m)'),
         [['IPR / WF','Perfil de ala ancha','Trabes y columnas principales','14-120'],
          ['HSS cuadrado','Perfil tubular cuadrado','Columnas arquitectonicas','3-45'],
          ['HSS redondo','Tubo circular','Contravientos y arcos','2-30'],
          ['Canal C','Perfil en C','Vigueta de entrepiso','4-25'],
          ['Angulo L','Angulo de acero','Conexiones y detalles','1-15']],
         [34,52,52,36],'Tabla 1. Perfiles de acero estructural en Mexico'],
        None),
        (3,'Conexiones y union soldada',None,[
            'Soldadura electrodo E7018: para acero A36 (el mas comun en Mexico).',
            'Inspeccion visual de soldadura: revision de penetracion, porosidad y grietas.',
            'Pernos de alta resistencia A325 o A490: para uniones desmontables.',
            'Placa base en columnas: une la columna al dado de cimentacion con anclas.',
        ],None,None,None),
    ],
    checklist=['Verificar que el diseño estructural sea de ingeniero certificado',
               'Confirmar que el acero cumpla norma ASTM A36 o equivalente mexicano',
               'Inspeccionar cada soldadura visualmente antes de cubrir',
               'Verificar torque de pernos de alta resistencia con llave dinamometrica',
               'Proteger el acero con pintura anticorrosiva antes de colar la losa',
               'Confirmar el diseño sismico con el RCDF o reglamento local']),
5: dict(
    sections=[
        (1,'Tipos de block de concreto y sus propiedades',None,[
            'Block estandar 20x20x40 cm: el mas comun, carga maxima 40 ton/m2.',
            'Block solido 10x20x40 cm: para muros delgados de separacion interior.',
            'Block de 15 cm: alternativa economica para muros de carga bajos.',
            'Piloblock (con celda central): permite el paso de instalaciones sin picar.',
        ],None,
        [('Tipo de block','Medidas (cm)','Resistencia f\'c','Peso (kg/pza)','Usos'),
         [['Estandar huecos','20x20x40','60-100 kg/cm2','15-18','Muros exteriores e interiores'],
          ['Solido','10x20x40','80-120 kg/cm2','18-22','Muros de baja altura, jardineras'],
          ['Macizo 15 cm','15x20x40','70-110 kg/cm2','16-20','Muros de carga economicos'],
          ['Piloblock','20x20x40','60-90 kg/cm2','13-16','Paso de instalaciones hidraulicas']],
         [38,28,30,20,58],'Tabla 1. Tipos de block de concreto y sus propiedades'],
        None),
        (2,'Proceso de construccion: trazo, plomeo y refuerzo',None,[
            'Traza los muros con hilo y plomada antes de colocar la primera hilada.',
            'Coloca la primera hilada en "seco" para verificar la distribucion.',
            'Mortero de junta: 1 cemento : 3 arena, espesor 1.0-1.5 cm uniforme.',
            'Trabado de hiladas: las juntas verticales deben desplazarse 20 cm entre hiladas.',
            'Plomeo: verifica con nivel de burbuja cada 3 hiladas.',
            'Refuerzo vertical: varilla #3 en esquinas y cada 1.2 m en muros largos.',
        ],None,None,None),
    ],
    checklist=['Verificar resistencia del block (pedir certificado del fabricante)',
               'Comprobar que el mortero tenga la consistencia correcta (no muy liquido)',
               'Colocar primera hilada en seco antes de pegar',
               'Plomar cada 3 hiladas como maximo',
               'Colocar varilla de refuerzo vertical en todas las esquinas',
               'Vaciar las celdas con refuerzo con concreto fluido (lechada)',
               'Impermeabilizar muros exteriores con dos manos de elastomerico']),
6: dict(
    sections=[
        (1,'Sistemas de impermeabilizacion comparados',None,None,None,
        [('Sistema','Durabilidad','Costo/m2 (MXN)','Mejor para'),
         [['Acrilico 2 manos','1-2 anos','$80-$130','Mantenimiento economico'],
          ['Elastomerico 3 capas','3-5 anos','$120-$200','Azoteas con trafico peatonal'],
          ['Membrana asfaltica monocapa','5-8 anos','$200-$320','Pendientes suaves'],
          ['Bicapa asfaltica','10-15 anos','$280-$450','Maximo rendimiento'],
          ['PVC termosoldado','15-20 anos','$380-$650','Techos planos comerciales']],
         [42,24,34,74],'Tabla 1. Comparativa de sistemas de impermeabilizacion'],
        'Cada sistema tiene sus fortalezas. Elige en funcion de tu presupuesto, '
        'el uso de la azotea y el tiempo que quieres entre mantenimientos.'),
        (2,'Preparacion de superficie: el 80% del exito',None,[
            'Limpieza total: retira vegetacion, polvo, grasa y pintura suelta.',
            'Sellado de grietas: toda fisura mayor a 0.3 mm debe sellarse con poliuretano.',
            'Pendientes: verifica que el agua escurra hacia los registros (minimo 2%).',
            'Superficies humedas: espera minimo 48 horas despues de lluvias para aplicar.',
        ],'No apliques impermeabilizante sobre superficies humedas: la adhesion se reduce hasta un 70%.',
        None,None),
    ],
    checklist=['Revisar pendientes hacia desagues antes de impermeabilizar',
               'Sellar todas las grietas con poliuretano o mortero antes de aplicar',
               'Verificar que la superficie este seca (minimo 48 h despues de lluvia)',
               'Limpiar coladeras y registros pluviales',
               'Aplicar minimo 2 manos de acrilico o 3 capas de elastomerico',
               'Proteger el area impermeabilizada con gravilla en zonas de trafico',
               'Programar inspeccion anual en la temporada seca']),
12: dict(
    sections=[
        (1,'Precios de instalacion electrica residencial 2025',None,None,None,
        [('Tipo de trabajo','Costo min (MXN)','Costo max (MXN)','Notas'),
         [['Por punto electrico (contacto/apagador)','$350','$600','Incluye mano de obra y material'],
          ['Instalacion completa 80-120 m2','$18,000','$35,000','Desde cero, incluye tablero'],
          ['Cambio de tablero electrico','$4,500','$9,000','Incluye tablero e interruptores'],
          ['Circuito dedicado (A/C, estufa)','$1,800','$3,500','Incluye cable, conduit y proteccion'],
          ['Instalacion de tierra fisica','$2,200','$4,500','Electrodo, cable y conexiones'],
          ['Cambio de cableado (por m2)','$85','$145','Solo mano de obra, sin materiales']],
         [58,26,26,64],'Tabla 1. Precios de instalacion electrica residencial (Mexico 2025)'],
        None),
        (2,'Normativa NOM-001-SEDE: puntos criticos',None,[
            'Conduit obligatorio: todo cable debe ir en tubo conduit EMT o PVC, sin excepcion.',
            'Tablero con interruptores: no se aceptan fusibles de cuchillo en instalaciones nuevas.',
            'Tierra fisica: la varilla de cobre debe ir al menos 2.4 m en el suelo humedo.',
            'GFCI en banos y cocinas: los contactos en zonas humedas requieren proteccion diferencial.',
            'Separacion neutro-tierra: en el tablero principal deben ir en barras separadas.',
        ],'Una instalacion fuera de norma puede ser rechazada por CFE para conexion permanente y '
        'invalida el seguro del inmueble en caso de siniestro.',None,None),
    ],
    checklist=['Verificar que el electricista tenga experiencia con NOM-001-SEDE',
               'Confirmar que todo cable va dentro de conduit EMT o PVC',
               'Instalar GFCI en todos los contactos de banos y cocinas',
               'Verificar tierra fisica con multimetro (maximo 25 ohm de resistencia)',
               'Probar cada interruptor termomagntico con carga antes de terminar',
               'Solicitar revision y aprobacion de CFE para conexion nueva',
               'Documentar en plano la ubicacion de todos los circuitos']),
13: dict(
    sections=[
        (1,'Comparativa tecnica porcelanato vs. ceramica',None,None,None,
        [('Caracteristica','Ceramica','Porcelanato esmaltado','Porcelanato tecnico'),
         [['Absorcion de agua','3-6% (alta)','0.5-3% (media)','< 0.5% (muy baja)'],
          ['Dureza Mohs','4-5','6-7','7-8'],
          ['Resistencia al trafico','Bajo-medio','Medio-alto','Alto-muy alto'],
          ['Uso en exteriores','No recomendado','Si (cubiertos)','Si (todos)'],
          ['Antiderrapante clase R','R9 tipico','R10 disponible','R10-R11 disponible'],
          ['Precio por m2','$110-$320','$200-$500','$280-$800+'],
          ['Precio colocado/m2','$350-$550','$420-$700','$500-$950']],
         [48,40,44,42],'Tabla 1. Comparativa tecnica ceramica vs. porcelanato'],
        None),
        (2,'Cuando usar cada tipo en Mexico',None,[
            'Ceramica: recamaras, pasillos interiores, banos de uso moderado. No apta para terrazas.',
            'Porcelanato esmaltado: sala, cocina, banos principales, terrazas cubiertas.',
            'Porcelanato tecnico: exteriores, albercas, comercios, garajes, pisos industriales.',
            'Evita ceramica en exteriores: se fractura por la expansion termica bajo lluvia y sol.',
        ],'El error mas costoso en Mexico: usar ceramica en terrazas o jardines. '
        'En 12-24 meses las heladas o la expansion termica fragmentan el piso.',None,None),
    ],
    checklist=['Definir el uso del espacio (trafico, humedad, exterior/interior)',
               'Seleccionar la clase correcta de piso segun la tabla comparativa',
               'Pedir el certificado de absorcion de agua y clase de trafico al proveedor',
               'Comprar 10% adicional para cortes y reposicion futura',
               'Usar adhesivo tipo II (flexible) para porcelanato de formato grande',
               'Verificar que la superficie base este nivelada (+/-3 mm en 3 m)',
               'Usar fragua epoxica en juntas de porcelanato para mayor durabilidad']),
14: dict(
    sections=[
        (1,'Presupuesto para cocina pequena 6-10 m2 (2025)',None,None,None,
        [('Partida','Economico (MXN)','Medio (MXN)','Premium (MXN)'),
         [['Muebles de cocina modulares','$9,000-$14,000','$14,000-$22,000','$25,000-$50,000'],
          ['Cubierta (granito/cuarzo/laminado)','$2,500-$4,500','$5,000-$9,000','$9,000-$18,000'],
          ['Tarja acero inox.','$1,200-$2,500','$2,500-$4,500','$4,500-$10,000'],
          ['Salpicadero (azulejo o pintura epox)','$800-$2,000','$2,000-$5,000','$5,000-$12,000'],
          ['Instalacion electrica (circuito ded.)','$1,800-$3,000','$3,000-$4,500','$4,500-$7,000'],
          ['Instalacion hidraulica','$1,500-$2,800','$2,800-$4,500','$4,500-$8,000'],
          ['Mano de obra instalacion','$3,000-$5,000','$5,000-$8,000','$8,000-$14,000'],
          ['TOTAL ESTIMADO','$19,800-$33,800','$34,300-$57,500','$60,500-$119,000']],
         [60,38,38,38],'Tabla 1. Presupuesto de cocina pequena por nivel (Mexico 2025)'],
        None),
        (2,'Como ahorrar sin sacrificar calidad',None,[
            'Muebles: los modulares nacionales Ikea o de fabrica local tienen la misma durabilidad que importados.',
            'Cubierta: el laminado de alta presion (Formica) a $350-600 MXN/ml es 70% mas barata que el granito.',
            'Salpicadero: pintura epoxica en $450-800 MXN por la zona completa vs. $3,000+ en azulejo importado.',
            'Tarja: una buena tarja nacional de acero inox 304 cuesta $1,200-1,800 MXN con calidad similar a importadas de $4,000+.',
        ],'No escatimes en la instalacion electrica e hidraulica: son las que mas caro salen reparar despues.',None,None),
    ],
    checklist=['Medir exactamente el espacio antes de pedir cotizacion de muebles',
               'Definir la ubicacion de la tarja (no moverla para no cambiar plomeria)',
               'Instalar circuito electrico dedicado para cada electrodomestico grande',
               'Verificar que los muebles lleguen completos y sin daños antes de instalar',
               'Dejar espacio de ventilacion detras del refrigerador (10 cm minimo)',
               'Instalar extractora o ventilacion en cocina cerrada',
               'Solicitar factura por muebles y garantia escrita del fabricante']),
15: dict(
    sections=[
        (1,'Por que falla la impermeabilizacion en Mexico',None,[
            'Mala preparacion: superficie humeda, con grasa o sin limpiar -> falla en 3-6 meses.',
            'Sistema incorrecto: usar acrilico cuando se necesita membrana -> corta vida util.',
            'Sin pendientes: el agua estancada desintegra cualquier sistema en 1-2 temporadas.',
            'Temporada incorrecta: aplicar durante lluvia o con temperatura menor a 8 C.',
        ],None,None,None),
        (2,'Precios por sistema de impermeabilizacion (2025)',None,None,None,
        [('Sistema','Durabilidad','Costo/m2 material','Costo/m2 aplicado','Total tipico 50 m2'),
         [['Acrilico 2-3 manos','1-2 anos','$28-$45','$50-$80','$4,000-$6,250'],
          ['Elastomerico 3 capas','3-5 anos','$45-$75','$80-$130','$6,250-$10,250'],
          ['Membrana asfaltica monocapa','5-8 anos','$90-$140','$140-$220','$11,500-$18,000'],
          ['Bicapa asfaltica completa','10-15 anos','$140-$200','$210-$330','$17,500-$26,500']],
         [52,24,36,36,46],'Tabla 1. Precios de impermeabilizacion por sistema (Mexico 2025)'],
        None),
    ],
    checklist=['Verificar pendientes hacia desagues (minimo 2%)',
               'Secar la azotea minimo 48 horas antes de aplicar',
               'Sellar todas las grietas con poliuretano o mortero',
               'Limpiar coladeras y verificar que drenen correctamente',
               'Aplicar impermeabilizante en temporada seca (noviembre-abril)',
               'Respetar tiempos de curado entre capas (6-24 horas segun producto)',
               'Programar revision y mantenimiento cada 12 meses']),
16: dict(
    sections=[
        (1,'Comparativa de costos: block vs. tabique',None,None,None,
        [('Concepto','Block de concreto 15x20x40','Tabique rojo recocido','Ganador'),
         [['Precio unitario 2025','$15-$22/pza','$4.50-$7.50/pza','Tabique (por pza)'],
          ['Pzas por m2 de muro','12.5','50-55','Block (menos pzas)'],
          ['Costo material/m2','$190-$275','$225-$413','Block (en volumen)'],
          ['Mortero de junta (kg/m2)','8-10 kg','18-22 kg','Block (menos mortero)'],
          ['Velocidad de construccion','Alta (pza grande)','Media (pza pequeña)','Block'],
          ['Aislamiento termico','Bueno (celda de aire)','Regular','Block'],
          ['Resistencia sismica','Buena con refuerzo','Buena con refuerzo','Empate'],
          ['Precio muro terminado/m2','$320-$480','$280-$420','Tabique (marginal)']],
         [58,44,44,28],'Tabla 1. Comparativa completa block de concreto vs. tabique rojo'],
        None),
        (2,'Recomendacion por zona y clima en Mexico',None,[
            'Norte de Mexico (Sonora, Chihuahua, Nuevo Leon): block de concreto por mejor aislamiento termico.',
            'Centro (CDMX, Hidalgo, Puebla): ambos validos; el tabique rojo tiene larga tradicion y buenos acabados.',
            'Sur y Sureste (Oaxaca, Chiapas, Yucatan): block de concreto resiste mejor la humedad ambiental alta.',
            'Zona sismica alta (D): ambos funcionan con el refuerzo vertical correcto segun RCDF.',
        ],'El refuerzo vertical con varilla #3 cada 1.2 m es obligatorio para ambos tipos de muro '
        'en construcciones de mas de un piso o en zona sismica D (CDMX, Guerrero, Oaxaca).',None,None),
    ],
    checklist=['Verificar la resistencia del block o tabique (pedir certificado del lote)',
               'Calcular el numero exacto de piezas necesarias + 5% de merma',
               'Preparar el mortero en proporcion correcta (1 cemento : 3 arena)',
               'Asegurar juntas de 1.0-1.5 cm uniformes en todos los tendeles',
               'Colocar refuerzo vertical en esquinas y cada 1.2 m en muros largos',
               'Rellenar celdas con refuerzo con concreto fluido o lechada',
               'Impermeabilizar muros exteriores antes de aplicar acabados']),
}


# ═══════════════════════════════════════════════════════════════════════
#  BUILD ALL GUIDES
# ═══════════════════════════════════════════════════════════════════════
def build_all():
    all_guides = GUIDES[:]

    # Build remaining with generic builder
    for rid in REMAINING:
        d = REMAINING_DATA[rid]
        rc = REMAINING_CONTENT[rid]
        all_guides.append({
            'id': rid,
            'slug': d['slug'],
            'cat': d['cat'],
            'title': d['title'],
            'subtitle': d['subtitle'],
            'stats': {'pages': 8, 'tables': 3, 'checklist': True},
            'chapters': [s[1] for s in rc['sections']] + ['Checklist profesional'],
            'build': None,  # use generic
            '_sections': rc['sections'],
            '_checklist': rc['checklist'],
        })

    all_guides.sort(key=lambda g: g['id'])

    for g in all_guides:
        pdf = PDF(g)
        if g.get('build') and callable(g.get('build')):
            g['build'](pdf)
        else:
            _build_generic(
                pdf, g['cat'], g['subtitle'],
                g['_sections'], g.get('_checklist', [])
            )

        path = f"{OUTPUT_DIR}/{g['id']:02d}-{g['slug']}.pdf"
        # Strip the slug prefix from the slug field if it includes the id
        slug = g['slug']
        if not slug.startswith(str(g['id']).zfill(2) + '-'):
            slug = f"{g['id']:02d}-{slug}"
        path = f"{OUTPUT_DIR}/{slug}.pdf"
        pdf.output(path)
        print(f"  OK  {path}")

    print(f"\nGenerated {len(all_guides)} PDF guides in '{OUTPUT_DIR}/'")


if __name__ == '__main__':
    build_all()
