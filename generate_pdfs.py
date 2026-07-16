#!/usr/bin/env python3
import re
import os
from fpdf import FPDF
from fpdf.enums import XPos, YPos

OUTPUT_DIR = "guias"
os.makedirs(OUTPUT_DIR, exist_ok=True)

BRAND_BLUE  = (0, 90, 255)
BRAND_DARK  = (15, 23, 42)
BRAND_GRAY  = (100, 116, 139)
BRAND_LIGHT = (245, 247, 250)
BRAND_ACCENT = (255, 127, 0)

def strip_tags(html):
    return re.sub(r'<[^>]+>', '', html)

def parse_content(html):
    """Parse HTML guide content into structured blocks."""
    blocks = []
    parts = re.split(r'(<h2>[^<]*</h2>|<ul>.*?</ul>|<p>[^<]*(?:<strong>[^<]*</strong>[^<]*)*</p>)', html, flags=re.DOTALL)
    for part in parts:
        part = part.strip()
        if not part:
            continue
        if re.match(r'<h2>', part):
            text = re.sub(r'<[^>]+>', '', part).strip()
            blocks.append(('h2', text))
        elif re.match(r'<ul>', part):
            items = re.findall(r'<li>(.*?)</li>', part, re.DOTALL)
            for item in items:
                clean = re.sub(r'<strong>(.*?)</strong>', r'\1', item)
                clean = re.sub(r'<[^>]+>', '', clean).strip()
                blocks.append(('li', clean))
        elif re.match(r'<p>', part):
            text = re.sub(r'<strong>(.*?)</strong>', r'\1', part)
            text = re.sub(r'<[^>]+>', '', text).strip()
            if text:
                blocks.append(('p', text))
        else:
            text = re.sub(r'<[^>]+>', '', part).strip()
            if text:
                blocks.append(('p', text))
    return blocks


class GuidePDF(FPDF):
    def __init__(self, guide):
        super().__init__()
        self.guide = guide
        self.set_auto_page_break(auto=True, margin=20)
        self.set_margins(18, 18, 18)

    def header(self):
        # Blue top bar
        self.set_fill_color(*BRAND_BLUE)
        self.rect(0, 0, 210, 10, 'F')
        # Logo text
        self.set_xy(18, 12)
        self.set_font('Helvetica', 'B', 9)
        self.set_text_color(*BRAND_BLUE)
        self.cell(30, 6, 'Build', border=0, new_x=XPos.RIGHT, new_y=YPos.TOP)
        self.set_text_color(*BRAND_DARK)
        self.cell(20, 6, 'Smart', border=0, new_x=XPos.RIGHT, new_y=YPos.TOP)
        # Right side: category pill
        cat_label = self.guide.get('catLabel', '')
        self.set_font('Helvetica', 'B', 7)
        self.set_text_color(*BRAND_BLUE)
        self.set_xy(210 - 18 - len(cat_label)*2.5 - 6, 12)
        self.cell(len(cat_label)*2.5 + 6, 6, cat_label.upper(), border=0, align='R')
        self.ln(2)
        # Divider
        self.set_draw_color(*BRAND_BLUE)
        self.set_line_width(0.3)
        self.line(18, 22, 192, 22)

    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', '', 7)
        self.set_text_color(*BRAND_GRAY)
        self.cell(0, 6, f'BuildSmart Mexico  |  buildsmart.replit.app  |  Pagina {self.page_no()}', align='C')
        # Bottom blue bar
        self.set_fill_color(*BRAND_BLUE)
        self.rect(0, 297 - 5, 210, 5, 'F')

    def draw_hero(self):
        """Draw the hero section on first page."""
        # Hero background
        self.set_fill_color(*BRAND_DARK)
        self.rect(0, 0, 210, 72, 'F')
        # Top accent bar
        self.set_fill_color(*BRAND_BLUE)
        self.rect(0, 0, 210, 10, 'F')
        # Category label
        self.set_xy(18, 30)
        self.set_font('Helvetica', 'B', 8)
        self.set_text_color(*BRAND_BLUE)
        cat_label = self.guide.get('catLabel', 'Guia').upper()
        self.cell(0, 6, cat_label, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        # Title
        self.set_x(18)
        self.set_font('Helvetica', 'B', 18)
        self.set_text_color(255, 255, 255)
        title = self.guide['title']
        self.multi_cell(174, 9, title, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        # URL reference
        self.set_x(18)
        self.set_font('Helvetica', '', 8)
        self.set_text_color(160, 185, 220)
        self.cell(0, 6, 'buildsmart.replit.app  |  Guia de Construccion Mexico')
        self.set_y(78)

    def draw_excerpt_box(self):
        """Draw the excerpt/summary highlighted box."""
        excerpt = self.guide.get('excerpt', '')
        y = self.get_y() + 2
        # Box background
        self.set_fill_color(*BRAND_LIGHT)
        self.set_draw_color(*BRAND_BLUE)
        self.set_line_width(0.5)
        box_h = 18 + (len(excerpt) // 80) * 5
        self.rect(18, y, 174, box_h, 'DF')
        # Blue left accent stripe
        self.set_fill_color(*BRAND_BLUE)
        self.rect(18, y, 3, box_h, 'F')
        # Label
        self.set_xy(24, y + 4)
        self.set_font('Helvetica', 'B', 8)
        self.set_text_color(*BRAND_BLUE)
        self.cell(0, 5, 'RESUMEN:', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_x(24)
        self.set_font('Helvetica', '', 9)
        self.set_text_color(*BRAND_DARK)
        self.multi_cell(162, 5, excerpt, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(6)

    def draw_cta_box(self):
        """Draw call-to-action box linking to calculator."""
        self.ln(4)
        y = self.get_y()
        if y > 250:
            self.add_page()
            y = self.get_y()
        # Box
        self.set_fill_color(*BRAND_BLUE)
        self.rect(18, y, 174, 26, 'F')
        self.set_xy(24, y + 5)
        self.set_font('Helvetica', 'B', 11)
        self.set_text_color(255, 255, 255)
        self.cell(0, 6, 'Calcula el presupuesto de tu proyecto', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_x(24)
        self.set_font('Helvetica', '', 8)
        self.set_text_color(200, 220, 255)
        self.cell(0, 5, 'Usa la calculadora gratuita en buildsmart.replit.app >> Calculadora')
        self.ln(12)

    def draw_disclaimer(self):
        self.ln(4)
        y = self.get_y()
        self.set_fill_color(255, 250, 230)
        self.set_draw_color(255, 180, 0)
        self.set_line_width(0.3)
        self.rect(18, y, 174, 16, 'DF')
        self.set_xy(22, y + 3)
        self.set_font('Helvetica', 'B', 7)
        self.set_text_color(120, 80, 0)
        self.cell(0, 4, 'NOTA:', new_x=XPos.RIGHT, new_y=YPos.TOP)
        self.set_x(32)
        self.set_font('Helvetica', '', 7)
        self.set_text_color(100, 70, 0)
        self.multi_cell(155, 4, 'Los precios son de referencia y pueden variar segun region, proveedor y temporada. Siempre solicita cotizaciones locales antes de iniciar cualquier obra.')

    def build(self):
        self.add_page()
        # Hero overwrites header on first page
        self.draw_hero()
        self.draw_excerpt_box()

        blocks = parse_content(self.guide.get('content', ''))

        for kind, text in blocks:
            if kind == 'h2':
                self.ln(4)
                y = self.get_y()
                # Section heading with blue underline
                self.set_x(18)
                self.set_font('Helvetica', 'B', 12)
                self.set_text_color(*BRAND_DARK)
                self.cell(0, 7, text, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                self.set_draw_color(*BRAND_BLUE)
                self.set_line_width(0.6)
                self.line(18, self.get_y(), 192, self.get_y())
                self.ln(3)

            elif kind == 'p':
                self.set_x(18)
                self.set_font('Helvetica', '', 9.5)
                self.set_text_color(*BRAND_DARK)
                self.multi_cell(174, 5.5, text, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                self.ln(2)

            elif kind == 'li':
                self.set_x(22)
                self.set_font('Helvetica', '', 9)
                self.set_text_color(*BRAND_GRAY)
                # Bullet
                self.set_fill_color(*BRAND_BLUE)
                bx = self.get_x() - 4
                by = self.get_y() + 2
                self.ellipse(bx, by, 1.5, 1.5, 'F')
                self.multi_cell(166, 5, text, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                self.ln(1)

        self.draw_cta_box()
        self.draw_disclaimer()


GUIDES = [
    {
        'id': 1, 'slug': 'fundamentos-del-concreto',
        'cat': 'basics', 'catLabel': 'Fundamentos',
        'title': 'Fundamentos del Concreto',
        'excerpt': 'Aprende a preparar y verter mezclas de concreto con resistencia optima para cimentaciones, pisos y estructuras de carga.',
        'content': '<h2>Introduccion al Concreto</h2><p>El concreto es la piedra angular de la construccion moderna. Una mezcla correcta garantiza durabilidad, resistencia y ahorro a largo plazo.</p><h2>Proporciones de la Mezcla</h2><p>La mezcla estandar para cimentaciones residenciales es 1:2:4 (cemento:arena:grava). Para pisos se usa 1:2:3. La relacion agua-cemento no debe exceder 0.5 para obtener buena resistencia.</p><ul><li><strong>Cemento:</strong> Actua como aglutinante; usa cemento tipo I o II para usos generales</li><li><strong>Arena:</strong> Debe estar limpia, sin arcillas ni sales; tamano maximo 4.75 mm</li><li><strong>Grava:</strong> Tamano maximo de 19 mm para losas y 38 mm para masivos</li><li><strong>Agua:</strong> Potable, libre de aceites y acidos; temperatura ideal 15-25 C</li></ul><h2>Proceso de Vaciado</h2><p>Prepara la cimbra antes de mezclar. Vierte el concreto en capas de 20-30 cm y compacta con vibrador para eliminar cangrejeras. El curado debe durar minimo 7 dias manteniendolo humedo.</p>'
    },
    {
        'id': 2, 'slug': 'instalacion-tuberia-pvc',
        'cat': 'plumbing', 'catLabel': 'Plomeria',
        'title': 'Instalacion de Tuberia PVC',
        'excerpt': 'Guia completa sobre dimensionamiento, corte, pegado y prueba de redes hidraulicas y sanitarias en PVC.',
        'content': '<h2>Tipos de Tuberia PVC</h2><p>Existen dos clasificaciones principales: hidraulica (presion) y sanitaria (drenaje). La hidraulica soporta presiones de trabajo de 6 a 16 kg/cm2, mientras la sanitaria trabaja por gravedad.</p><h2>Proceso de Instalacion</h2><p>Usa cortapipas para cortes limpios y lija el extremo para eliminar rebabas. Aplica primer y cemento solvente en ambas superficies, ensambla girando 1/4 de vuelta y manten presion 30 segundos.</p><h2>Dimensionamiento</h2><ul><li><strong>Bajada de aguas negras:</strong> Minimo 4 pulgadas (100 mm) de diametro</li><li><strong>Ramal de WC:</strong> 4 pulgadas, pendiente minima 2%</li><li><strong>Ramal de lavabo y regadera:</strong> 2 pulgadas (50 mm)</li><li><strong>Red hidraulica general:</strong> 3/4 pulgada para alimentacion principal</li></ul><h2>Prueba Hidrostatica</h2><p>Antes de tapar cualquier instalacion hidraulica, realiza una prueba de presion a 1.5 veces la presion de trabajo durante 30 minutos. Si hay caida de presion, revisa cada union.</p>'
    },
    {
        'id': 3, 'slug': 'instalaciones-electricas-residenciales',
        'cat': 'electrical', 'catLabel': 'Electrico',
        'title': 'Instalaciones Electricas Residenciales',
        'excerpt': 'Entiende el diseno de circuitos, calibres de conductor, protecciones y normativa NOM para instalaciones seguras.',
        'content': '<h2>Conceptos Basicos</h2><p>La instalacion electrica residencial se divide en circuitos de iluminacion (calibre 12 AWG) y contactos (calibre 10 AWG). Cada circuito debe protegerse con un interruptor termomagntico del calibre adecuado.</p><h2>Circuitos Recomendados</h2><ul><li><strong>Iluminacion general:</strong> Calibre 12 AWG, interruptor 15 A</li><li><strong>Contactos generales:</strong> Calibre 10 AWG, interruptor 20 A</li><li><strong>Aire acondicionado o lavadora:</strong> Circuito dedicado calibre 10 AWG</li><li><strong>Cocina (estufa, horno):</strong> Circuito dedicado 240 V, calibre 8 AWG</li></ul><h2>Normativa NOM-001-SEDE</h2><p>Toda instalacion debe cumplir la NOM-001-SEDE vigente: conduit EMT o PVC para canalizar cables, cajas de registro en cada cambio de direccion, tablero con tierra fisica y neutro separados, y proteccion GFCI en banos y cocinas.</p><h2>Seguridad</h2><p>Desconecta siempre el interruptor general antes de trabajar. Usa multimetro para verificar ausencia de voltaje. Nunca empalmes cables fuera de cajas de registro cerradas.</p>'
    },
    {
        'id': 4, 'slug': 'estructuras-acero-concreto',
        'cat': 'advanced', 'catLabel': 'Avanzado',
        'title': 'Estructuras de Acero y Concreto',
        'excerpt': 'Aprende sobre sistemas estructurales combinados, conexiones y consideraciones sismicas para construcciones robustas.',
        'content': '<h2>Sistemas Estructurales</h2><p>La combinacion de acero y concreto aprovecha la alta resistencia a tension del acero y la resistencia a compresion del concreto. Los marcos rigidos de acero con losas de concreto son sistemas eficientes y economicos.</p><h2>Tipos de Conexiones</h2><ul><li><strong>Soldadura:</strong> Maxima rigidez, requiere soldador certificado, ideal para zonas sismicas</li><li><strong>Pernos de alta resistencia:</strong> Instalacion rapida, buena resistencia a cortante</li><li><strong>Conexiones articuladas:</strong> Solo transmiten carga vertical, mas economicas</li></ul><h2>Consideraciones Sismicas en Mexico</h2><p>Mexico esta en zona sismica alta. Las estructuras deben disenarse conforme al Reglamento de Construcciones local y la NTC-Sismica. Las conexiones rigidas en marcos de acero son obligatorias para edificios de mas de dos pisos en zonas de alta sismicidad (zona D).</p><h2>Losas Colaborantes</h2><p>Las losas de concreto sobre perfil de acero (deck) reducen el tiempo de construccion 40% respecto a la cimbra tradicional. El espesor minimo es 12 cm con malla electrosoldada 6x6-10/10.</p>'
    },
    {
        'id': 5, 'slug': 'mamposteria-muros-block',
        'cat': 'basics', 'catLabel': 'Fundamentos',
        'title': 'Mamposteria y Muros de Block',
        'excerpt': 'Domina las tecnicas de construccion con block de concreto: mezclas, tendeles, plomeo y refuerzo vertical.',
        'content': '<h2>Tipos de Block</h2><p>El block de concreto estandar mide 20x20x40 cm y soporta cargas de compresion. Para muros exteriores usa block macizo; para interiores el block hueco es suficiente y mas economico.</p><h2>Mezcla de Mortero</h2><ul><li><strong>Proporcion:</strong> 1 parte cemento : 3 partes arena (en volumen)</li><li><strong>Espesor de junta:</strong> 1.0 a 1.5 cm uniformes</li><li><strong>Trabajabilidad:</strong> La mezcla debe permanecer trabajable 2 horas</li></ul><h2>Proceso de Construccion</h2><p>Traza la planta con hilos y niveles antes de colocar el primer tendel. Coloca el block en hiladas trabadas (juntas verticales descalzadas 20 cm). Plomea cada 3 hiladas con nivel de burbuja. El refuerzo vertical (varilla # 3) debe ir en cada celda de las esquinas y a cada 1.2 m en muros largos.</p><h2>Impermeabilizacion</h2><p>El block de concreto es poroso. Aplica dos manos de impermeabilizante cristalizante en muros de sotano o en contacto con el suelo. En muros exteriores, el aplanado con mortero o el recubrimiento con pintura elastomerica es suficiente.</p>'
    },
    {
        'id': 6, 'slug': 'impermeabilizacion-azoteas',
        'cat': 'advanced', 'catLabel': 'Avanzado',
        'title': 'Impermeabilizacion de Azoteas',
        'excerpt': 'Tecnicas profesionales de impermeabilizacion: sistemas bicapa, membranas y mantenimiento preventivo.',
        'content': '<h2>Sistemas de Impermeabilizacion</h2><p>El sistema bicapa con membranas asfalticas es el mas durable (vida util 10-15 anos). Requiere superficie limpia, seca y con pendiente minima del 2% para el drenaje de agua pluvial.</p><h2>Tipos de Sistemas</h2><ul><li><strong>Pintura acrilica (1-2 anos):</strong> Solucion economica para mantenimiento, 2-3 manos</li><li><strong>Elastomerico multicapa (3-5 anos):</strong> Buena flexibilidad, cubre fisuras hasta 3 mm</li><li><strong>Membrana asfaltica monocapa (5-8 anos):</strong> Resistente a trafico peatonal</li><li><strong>Bicapa asfaltica (10-15 anos):</strong> Mayor durabilidad, ideal para zonas de alta lluvia</li></ul><h2>Preparacion de la Superficie</h2><p>Limpia la azotea retirando polvo, grasa y vegetacion. Sella todas las fisuras con mortero o sellador poliuretanico. Verifica que la pendiente sea minimo 2% hacia los registros pluviales. La superficie debe estar completamente seca; espera 48 horas despues de lluvias.</p><h2>Mantenimiento Preventivo</h2><p>Revisa la azotea cada 6 meses: limpia desagues, sella fisuras nuevas y aplica una mano de recubrimiento de mantenimiento cada 2 anos para prolongar la vida del sistema principal.</p>'
    },
    {
        'id': 7, 'slug': 'cuanto-cuesta-construir-casa-mexico',
        'cat': 'costos', 'catLabel': 'Costos MX',
        'title': 'Cuanto cuesta construir una casa en Mexico en 2025',
        'excerpt': 'Precios reales por metro cuadrado de construccion en Mexico, desde obra negra hasta acabados de lujo. Factores que encarecen o abaratan tu proyecto.',
        'content': '<h2>Costo de Construccion por m2 en Mexico (2025)</h2><p>El precio de construir una casa en Mexico varia ampliamente segun la calidad de los acabados, la zona del pais y si contratas mano de obra directa o empresa constructora.</p><ul><li><strong>Obra negra (sin acabados):</strong> $6,500 - $9,500 MXN/m2</li><li><strong>Construccion economica (acabados basicos):</strong> $9,500 - $14,000 MXN/m2</li><li><strong>Construccion media (acabados estandar):</strong> $14,000 - $20,000 MXN/m2</li><li><strong>Construccion premium (acabados de lujo):</strong> $20,000 - $35,000+ MXN/m2</li></ul><h2>Factores que Afectan el Precio</h2><p>La ubicacion es clave: en CDMX, Monterrey y Guadalajara los costos de mano de obra son 20-35% mas altos que en ciudades medianas. El tipo de suelo, el acceso al terreno y el acarreo de materiales tambien impactan el presupuesto.</p><h2>Desglose Tipico de Costos</h2><ul><li><strong>Cimentacion y estructura:</strong> 25-30% del total</li><li><strong>Muros y techos:</strong> 20-25%</li><li><strong>Instalaciones (hidraulica, sanitaria, electrica):</strong> 15-20%</li><li><strong>Acabados (pisos, azulejo, pintura):</strong> 20-25%</li><li><strong>Puertas, ventanas y herreria:</strong> 10-15%</li></ul><h2>Consejo</h2><p>Haz una estimacion detallada de materiales antes de arrancar. Un presupuesto preciso puede ahorrarte hasta el 15% al evitar compras de emergencia a sobreprecio.</p>'
    },
    {
        'id': 8, 'slug': 'precio-materiales-construccion-mexico',
        'cat': 'costos', 'catLabel': 'Costos MX',
        'title': 'Precio de Materiales de Construccion en Mexico 2025',
        'excerpt': 'Lista actualizada de precios de cemento, varilla, block, arena y grava en Mexico. Como comparar y comprar mejor.',
        'content': '<h2>Precios de Referencia (2025)</h2><p>Los precios de materiales de construccion en Mexico varian segun region, temporada y volumen de compra. Precios de referencia para compras al menudeo en CDMX y zona metropolitana:</p><ul><li><strong>Cemento Portland 50 kg:</strong> $180 - $210 MXN/bolsa</li><li><strong>Block de concreto 15x20x40 cm:</strong> $15 - $22 MXN/pieza</li><li><strong>Varilla corrugada #3 (3/8") 6 m:</strong> $90 - $115 MXN/pieza</li><li><strong>Arena de construccion:</strong> $500 - $750 MXN/m3</li><li><strong>Grava 3/4":</strong> $550 - $800 MXN/m3</li><li><strong>Tabique rojo recocido:</strong> $4.50 - $7.00 MXN/pieza</li><li><strong>Impermeabilizante elastomerico 19 L:</strong> $450 - $650 MXN</li></ul><h2>Como Ahorrar en Materiales</h2><p>Comprar por volumen puede darte descuentos del 10-20%. Compara precios entre ferreterias locales y distribuidoras directas. En temporada baja (enero-marzo) los precios suelen ser mas bajos.</p><h2>Impacto del Dolar</h2><p>Materiales como acero, cementos especiales y herramientas importadas estan indexados al dolar. Cuando el tipo de cambio sube, estos materiales se encarecen en 2-4 semanas. Planifica compras grandes cuando el peso este fuerte.</p>'
    },
    {
        'id': 9, 'slug': 'calcular-cemento-para-losa',
        'cat': 'basics', 'catLabel': 'Fundamentos',
        'title': 'Como Calcular Cuanto Cemento Necesito para una Losa',
        'excerpt': 'Formula paso a paso para calcular bolsas de cemento, arena y grava para cualquier losa en Mexico. Con ejemplos reales.',
        'content': '<h2>La Formula Basica</h2><p>Para una losa de concreto fc=150 kg/cm2 (uso residencial), la proporcion estandar en volumen es 1:2:3 (1 parte cemento : 2 partes arena : 3 partes grava). Por cada m3 de concreto necesitas aproximadamente:</p><ul><li><strong>Cemento:</strong> 7 bolsas de 50 kg</li><li><strong>Arena:</strong> 0.56 m3 (~840 kg)</li><li><strong>Grava:</strong> 0.84 m3 (~1,260 kg)</li><li><strong>Agua:</strong> 175-200 litros</li></ul><h2>Ejemplo Practico</h2><p>Quieres colar una losa de 6m x 5m x 12 cm de espesor: Volumen = 6 x 5 x 0.12 = 3.6 m3 de concreto. Cemento = 3.6 x 7 = 25.2 bolsas, compra 28 bolsas (10% extra). Arena = 3.6 x 0.56 = 2.0 m3. Grava = 3.6 x 0.84 = 3.0 m3.</p><h2>Espesores Recomendados en Mexico</h2><ul><li><strong>Losa de techo residencial:</strong> 10-12 cm</li><li><strong>Losa de piso en planta baja:</strong> 8-10 cm</li><li><strong>Losa de entrepisos (con trabes):</strong> 12-15 cm</li></ul><h2>Recomendacion Final</h2><p>Anade siempre un 10% de material extra por merma, derrames y ajustes. Para losas de mas de 25 m2, considera contratar concreto premezclado: la calidad es mas uniforme y el precio final suele ser competitivo.</p>'
    },
    {
        'id': 10, 'slug': 'costo-remodelar-bano-mexico',
        'cat': 'costos', 'catLabel': 'Costos MX',
        'title': 'Cuanto Cuesta Remodelar un Bano Completo en Mexico',
        'excerpt': 'Presupuesto real para remodelacion de bano en Mexico en 2025: materiales, mano de obra y tiempos. Desde $15,000 hasta $80,000 MXN.',
        'content': '<h2>Rangos de Precio por Tipo de Remodelacion</h2><p>El costo de remodelar un bano en Mexico depende del tamano (tipicamente 3-6 m2), la calidad de los materiales y si cambias la distribucion de la plomeria:</p><ul><li><strong>Remodelacion economica (solo acabados):</strong> $15,000 - $25,000 MXN</li><li><strong>Remodelacion media (materiales estandar + plomeria):</strong> $25,000 - $45,000 MXN</li><li><strong>Remodelacion completa premium:</strong> $45,000 - $80,000+ MXN</li></ul><h2>Desglose de Costos (Bano Estandar 4 m2)</h2><ul><li><strong>Azulejo y piso ceramico (incluyendo junta y adhesivo):</strong> $4,500 - $12,000 MXN</li><li><strong>WC, lavabo y regadera:</strong> $4,000 - $18,000 MXN segun marca</li><li><strong>Accesorios (toallero, jabonera, espejo):</strong> $1,200 - $4,000 MXN</li><li><strong>Mano de obra plomeria y albanileria:</strong> $6,000 - $12,000 MXN</li><li><strong>Instalacion electrica (extractor, foco):</strong> $1,500 - $3,000 MXN</li></ul><h2>Cuanto Tiempo Tarda</h2><p>Una remodelacion estandar sin cambiar distribucion tarda 5-8 dias habiles con dos albaniles. Si mueves la plomeria, suma 3-5 dias mas. Planifica un bano provisional si tienes un solo bano en casa.</p><h2>Lo Que Mas Encarece el Proyecto</h2><ul><li><strong>Cambiar la ubicacion del WC o regadera</strong> (requiere picar losa o piso)</li><li><strong>Impermeabilizacion deficiente</strong> que genera humedad y repeticion de trabajo</li><li><strong>Materiales de importacion</strong> (herrajes europeos, sanitarios de diseno)</li></ul>'
    },
    {
        'id': 11, 'slug': 'costo-pintar-casa-mexico',
        'cat': 'costos', 'catLabel': 'Costos MX',
        'title': 'Costo de Pintar una Casa en Mexico: Precio por m2',
        'excerpt': 'Cuanto cobran por pintar una casa en Mexico. Precios por m2 de mano de obra, tipos de pintura y consejos para ahorrar en tu presupuesto.',
        'content': '<h2>Precio de Mano de Obra para Pintura en Mexico</h2><p>En 2025, los pintores en Mexico cobran entre $35 - $75 MXN por m2 de superficie pintada (dos manos), dependiendo de la ciudad y la complejidad del trabajo:</p><ul><li><strong>Ciudades del interior:</strong> $35 - $50 MXN/m2</li><li><strong>CDMX, Guadalajara, Monterrey:</strong> $55 - $75 MXN/m2</li><li><strong>Trabajo con textura o estucado:</strong> $90 - $140 MXN/m2</li></ul><h2>Costo de Materiales por Tipo de Pintura</h2><ul><li><strong>Pintura vinilica economica (nacional):</strong> $60 - $85 MXN/litro</li><li><strong>Pintura vinilica calidad media (Comex, Vipsa):</strong> $85 - $130 MXN/litro</li><li><strong>Pintura acrilica premium:</strong> $130 - $200 MXN/litro</li><li><strong>Pintura epoxica para pisos:</strong> $180 - $280 MXN/litro</li></ul><h2>Rendimiento y Calculo</h2><p>Una pintura de buena calidad rinde ~12 m2 por litro en paredes lisas y ~9 m2 en superficies con textura. Para una casa de 100 m2 de muros, necesitaras aproximadamente 18-22 litros para dos manos sobre sellador.</p><h2>Consejo de Ahorro</h2><p>Aplica un fijador/sellador antes de la pintura. Duplica la vida util del acabado y reduce el consumo de pintura hasta un 20%. En fachadas, usa pintura elastomerica para proteger contra humedad y fisuras.</p>'
    },
    {
        'id': 12, 'slug': 'instalacion-electrica-precios-nom-mexico',
        'cat': 'electrical', 'catLabel': 'Electrico',
        'title': 'Instalacion Electrica en Casa: Precios y Normativa NOM en Mexico',
        'excerpt': 'Cuanto cuesta la instalacion electrica residencial en Mexico, que dice la norma NOM-001-SEDE y como evitar instalaciones peligrosas.',
        'content': '<h2>Precios de Instalacion Electrica Residencial (2025)</h2><p>El costo de instalacion electrica en Mexico depende del numero de circuitos, la superficie y si es obra nueva o remodelacion:</p><ul><li><strong>Instalacion basica por punto electrico (contacto o apagador):</strong> $350 - $600 MXN</li><li><strong>Instalacion completa casa 80-120 m2:</strong> $18,000 - $35,000 MXN</li><li><strong>Cambio de panel o tablero electrico:</strong> $4,500 - $9,000 MXN</li><li><strong>Circuito dedicado para A/C, estufa u horno:</strong> $1,800 - $3,500 MXN</li></ul><h2>Norma NOM-001-SEDE: Lo que Debes Saber</h2><p>La NOM-001-SEDE-2012 (actualizada 2020) establece los requisitos minimos de seguridad para instalaciones electricas en Mexico:</p><ul><li><strong>Toda instalacion nueva debe ser en tubo conduit</strong> (no se permite cable a la vista)</li><li><strong>Contactos en banos y cocinas</strong> deben tener proteccion GFCI contra tierra</li><li><strong>El tablero debe tener interruptores termomagnticos</strong> por circuito</li><li><strong>Calibre minimo para iluminacion:</strong> #12 AWG (2.05 mm)</li><li><strong>Circuitos de contactos:</strong> calibre #10 AWG (2.59 mm)</li></ul><h2>Senales de Instalacion Peligrosa</h2><ul><li><strong>Cables pelados o empalmes con cinta</strong> fuera de caja de registro</li><li><strong>Un solo circuito para toda la casa</strong></li><li><strong>Sin tierra fisica en contactos</strong></li><li><strong>Tablero con fusibles de cuchillo</strong> en vez de interruptores termomagnticos</li></ul>'
    },
    {
        'id': 13, 'slug': 'porcelanato-vs-ceramica-mexico',
        'cat': 'advanced', 'catLabel': 'Avanzado',
        'title': 'Porcelanato vs Ceramica: Cual Conviene y Cuanto Cuesta en Mexico',
        'excerpt': 'Comparativa completa entre piso porcelanato y ceramica para Mexico: durabilidad, precio por m2, instalacion y cuando usar cada uno.',
        'content': '<h2>Diferencias Clave</h2><p>La ceramica y el porcelanato son los pisos mas populares en Mexico, pero tienen caracteristicas muy distintas:</p><ul><li><strong>Ceramica:</strong> Absorcion de agua 3-6%, apta solo para interiores secos, precio $150-$350 MXN/m2</li><li><strong>Porcelanato tecnico:</strong> Absorcion menor al 0.5%, apto para interiores y exteriores, precio $280-$800+ MXN/m2</li><li><strong>Porcelanato esmaltado:</strong> Balance entre precio y desempeno, precio $200-$500 MXN/m2</li></ul><h2>Cuando Usar Cada Uno</h2><ul><li><strong>Ceramica:</strong> Ideal para banos interiores, recamaras y areas de bajo trafico. Mas facil de cortar y pegar.</li><li><strong>Porcelanato:</strong> Sala, cocina, terrazas cubiertas, comercios y zonas de alto trafico o humedad.</li></ul><h2>Costo Total de Instalacion por m2</h2><ul><li><strong>Ceramica colocada:</strong> $350 - $550 MXN/m2 (incluye adhesivo, junta y mano de obra)</li><li><strong>Porcelanato colocado:</strong> $500 - $950 MXN/m2</li></ul><h2>Error Comun en Mexico</h2><p>Usar ceramica en terrazas expuestas a la lluvia. Al tener alta absorcion de agua, se fractura con los cambios de temperatura. Para exteriores siempre usa porcelanato antiderrapante con clasificacion R10 o R11.</p>'
    },
    {
        'id': 14, 'slug': 'presupuesto-cocina-pequena-mexico',
        'cat': 'costos', 'catLabel': 'Costos MX',
        'title': 'Presupuesto para Cocina Pequena en Mexico: Guia Paso a Paso',
        'excerpt': 'Como hacer una cocina funcional y bonita en Mexico con presupuesto de $30,000 a $60,000 MXN. Materiales, muebles y mano de obra.',
        'content': '<h2>Presupuesto para Cocina Pequena (6-10 m2)</h2><p>Una cocina funcional en Mexico puede quedar lista entre $30,000 y $60,000 MXN dependiendo de los materiales y acabados que elijas:</p><ul><li><strong>Muebles de cocina modulares (nacionales):</strong> $12,000 - $22,000 MXN</li><li><strong>Cubierta de granito o quarzo (por ml):</strong> $900 - $2,500 MXN/ml</li><li><strong>Tarja de acero inoxidable:</strong> $1,800 - $4,500 MXN</li><li><strong>Salpicadero (azulejo o pintura epoxica):</strong> $1,500 - $6,000 MXN</li><li><strong>Instalacion electrica (circuito dedicado):</strong> $2,500 - $4,500 MXN</li><li><strong>Instalacion de plomeria:</strong> $2,000 - $4,000 MXN</li><li><strong>Mano de obra instalacion de muebles:</strong> $3,500 - $6,000 MXN</li></ul><h2>Opciones para Reducir el Presupuesto</h2><ul><li><strong>Elige muebles prefabricados</strong> nacionales en vez de diseno a medida</li><li><strong>Usa pintura epoxica en el salpicadero</strong> en lugar de azulejo importado</li><li><strong>Conserva la ubicacion actual de la tarja</strong> para no mover plomeria</li><li><strong>Elige cubierta de laminado</strong> en vez de granito o quarzo</li></ul><h2>Lo Que No Debes Escatimar</h2><p>La plomeria y la instalacion electrica: una fuga o corto circuito en cocina puede costar 3 veces mas en reparacion. Contrata siempre profesionales certificados para estas instalaciones.</p>'
    },
    {
        'id': 15, 'slug': 'impermeabilizacion-azotea-costos-mexico',
        'cat': 'advanced', 'catLabel': 'Avanzado',
        'title': 'Impermeabilizacion de Azotea en Mexico: Tipos y Costo por m2',
        'excerpt': 'Cuanto cuesta impermeabilizar una azotea en Mexico. Precios por m2, tipos de sistemas y cada cuanto debes renovarlo para evitar filtraciones.',
        'content': '<h2>Precios de Impermeabilizacion en Mexico (2025)</h2><p>El costo de impermeabilizar una azotea en Mexico varia segun el sistema y la condicion de la superficie:</p><ul><li><strong>Impermeabilizante acrilico (2 manos):</strong> $80 - $130 MXN/m2</li><li><strong>Sistema elastomerico (3-4 capas):</strong> $120 - $200 MXN/m2</li><li><strong>Membrana asfaltica monocapa:</strong> $200 - $320 MXN/m2</li><li><strong>Sistema bicapa (membrana + capa protectora):</strong> $280 - $450 MXN/m2</li></ul><h2>Cuanto Dura Cada Sistema</h2><ul><li><strong>Pintura acrilica:</strong> 1-2 anos (mantenimiento minimo)</li><li><strong>Elastomerico multicapa:</strong> 3-5 anos</li><li><strong>Membrana monocapa:</strong> 5-8 anos</li><li><strong>Bicapa asfaltica:</strong> 10-15 anos</li></ul><h2>Preparacion de la Superficie</h2><p>El 80% de los fallos de impermeabilizacion en Mexico se deben a mala preparacion. La azotea debe estar limpia, seca, con pendiente minima del 2% y sin grietas sin sellar. Sella todas las grietas con mortero o poliuretano antes de impermeabilizar.</p><h2>Temporada Optima en Mexico</h2><p>Impermeabiliza en temporada seca (noviembre-abril). La impermeabilizacion aplicada sobre superficies humedas o durante lluvias pierde hasta el 60% de su efectividad.</p>'
    },
    {
        'id': 16, 'slug': 'block-cemento-vs-ladrillo-mexico',
        'cat': 'basics', 'catLabel': 'Fundamentos',
        'title': 'Block de Cemento vs Ladrillo Rojo: Comparativa de Costos en Mexico',
        'excerpt': 'Cual es mas barato construir en Mexico, con block de concreto o tabique rojo. Comparamos precio, resistencia, velocidad y consumo de materiales.',
        'content': '<h2>Precio por m2 de Muro Construido</h2><p>Esta es la comparativa mas importante: el costo final del muro terminado, no solo del material:</p><ul><li><strong>Block de concreto 15x20x40 cm (colocado):</strong> $320 - $480 MXN/m2</li><li><strong>Tabique rojo recocido (colocado):</strong> $280 - $420 MXN/m2</li></ul><h2>Block de Concreto: Ventajas y Desventajas</h2><ul><li><strong>Ventajas:</strong> Avance mas rapido, mejor aislamiento termico en climas calidos, mas preciso en dimensiones, excelente para zona sismica con refuerzo vertical</li><li><strong>Desventajas:</strong> Mas pesado, absorbe mas humedad sin impermeabilizar, requiere grua para pisos altos</li></ul><h2>Tabique Rojo: Ventajas y Desventajas</h2><ul><li><strong>Ventajas:</strong> Mayor resistencia a compresion por cm2, mejor agarre de acabados, amplia disponibilidad en todo Mexico</li><li><strong>Desventajas:</strong> Mayor tiempo de construccion, mas mortero de junta, peor aislamiento termico en climas calidos</li></ul><h2>Recomendacion por Zona</h2><p>En el Bajio y Norte de Mexico (climas extremos) el block de concreto ofrece mejor aislamiento. En el Centro y Sur (zona sismica alta) el tabique bien reforzado da mayor seguridad. En ambos casos, el refuerzo vertical con varilla es obligatorio segun el Reglamento de Construcciones local.</p>'
    },
]

if __name__ == '__main__':
    for g in GUIDES:
        pdf = GuidePDF(g)
        pdf.build()
        filename = f"{OUTPUT_DIR}/{g['id']:02d}-{g['slug']}.pdf"
        pdf.output(filename)
        print(f"Generated: {filename}")
    print(f"\nDone! {len(GUIDES)} PDFs in '{OUTPUT_DIR}/'")
