"""
Hosea PPT Generator Script (合思标准模版 PPT 自动化构建脚本)
Based on Hosea Design System & Standard Template.
"""

import os
import sys
import json
import argparse
from typing import List, Dict, Any, Optional

from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

current_script_dir = os.path.dirname(os.path.abspath(__file__))
if current_script_dir not in sys.path:
    sys.path.insert(0, current_script_dir)

try:
    from icon_service import generate_icon_badge
except Exception as e:
    generate_icon_badge = None

# ==============================================================================
# Brand Tokens & Theme Definitions (合思视觉设计规范)
# ==============================================================================
COLOR_PRIMARY_BLUE = RGBColor(0x24, 0x55, 0xFF)   # #2455FF 电光科技蓝 (主色)
COLOR_ACCENT_GREEN = RGBColor(0x34, 0xDE, 0x4C)   # #34DE4C 荧光生机绿 (点缀色/标点/状态)
COLOR_ACCENT_CYAN  = RGBColor(0x05, 0xC9, 0xE5)   # #05C9E5 浅青蓝
COLOR_ACCENT_AMBER = RGBColor(0xFF, 0xC5, 0x40)   # #FFC540 活力暖黄 (高亮/警示)
COLOR_TEXT_DARK    = RGBColor(0x30, 0x3B, 0x47)   # #303B47 沉稳深灰蓝 (主标题/正文)
COLOR_TEXT_MUTED   = RGBColor(0x71, 0x80, 0x96)   # #718096 辅助灰 (次要说明/副标)
COLOR_BG_LIGHT     = RGBColor(0xF7, 0xF7, 0xF7)   # #F7F7F7 浅底背景色
COLOR_WHITE        = RGBColor(0xFF, 0xFF, 0xFF)   # #FFFFFF 纯白 (卡片底色)
COLOR_BORDER_LIGHT = RGBColor(0xEA, 0xEE, 0xF5)   # #EAEEF5 卡片精致微边框
COLOR_BORDER_BLUE  = RGBColor(0xD0, 0xDD, 0xFF)   # #D0DDFF 聚焦卡片边框

FONT_MAJOR = "微软雅黑"
FONT_MINOR = "微软雅黑"
FONT_FALLBACK = "微软雅黑"

TEMPLATE_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'resources', 'template.pptx')

# ==============================================================================
# Helper Functions
# ==============================================================================
def apply_font_to_run(run, font_name="微软雅黑", size=None, bold=None, color=None):
    """Enforces 微软雅黑 across Latin and East Asian characters in OOXML."""
    if font_name:
        run.font.name = font_name
    if size is not None:
        run.font.size = Pt(size)
    if bold is not None:
        run.font.bold = bold
    if color is not None:
        run.font.color.rgb = color
    try:
        rPr = run._r.get_or_add_rPr()
        ea = rPr.find('{http://schemas.openxmlformats.org/drawingml/2006/main}ea')
        if ea is None:
            ea = rPr.makeelement('{http://schemas.openxmlformats.org/drawingml/2006/main}ea', {'typeface': font_name or '微软雅黑'})
            rPr.append(ea)
        else:
            ea.set('typeface', font_name or '微软雅黑')
    except Exception:
        pass
def create_number_badge(slide, x, y, num_str: str, font_size=28):
    """Creates the signature Hosea '01.' badge: Blue number with Green dot."""
    tb = slide.shapes.add_textbox(x, y, Inches(1.5), Inches(0.6))
    tf = tb.text_frame
    tf.word_wrap = False
    tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
    p = tf.paragraphs[0]
    
    r1 = p.add_run()
    r1.text = num_str
    apply_font_to_run(r1, font_name=FONT_MAJOR, size=font_size, bold=True, color=COLOR_PRIMARY_BLUE)
    
    r2 = p.add_run()
    r2.text = "."
    apply_font_to_run(r2, font_name=FONT_MAJOR, size=font_size, bold=True, color=COLOR_ACCENT_GREEN)
    return tb

def apply_card_style(shape, highlighted=False):
    """Applies clean white card styling with subtle border."""
    shape.fill.solid()
    shape.fill.fore_color.rgb = COLOR_WHITE
    shape.line.width = Pt(1.5 if highlighted else 1)
    shape.line.color.rgb = COLOR_BORDER_BLUE if highlighted else COLOR_BORDER_LIGHT

def set_slide_title(slide, title_text: str):
    """Sets standard slide title for Layout 4 ('标题与内容')."""
    if slide.shapes.title:
        slide.shapes.title.text = title_text
        p = slide.shapes.title.text_frame.paragraphs[0]
        p.alignment = PP_ALIGN.CENTER
        for r in p.runs:
            apply_font_to_run(r, font_name=FONT_MAJOR, size=22, bold=True, color=COLOR_TEXT_DARK)

# ==============================================================================
# Slide Builder Engine
# ==============================================================================
class HoseaDeckBuilder:
    def __init__(self, template_path: Optional[str] = None):
        self.tpl_path = template_path or TEMPLATE_PATH
        if not os.path.exists(self.tpl_path):
            raise FileNotFoundError(f"Template not found at: {self.tpl_path}")
        self.prs = Presentation(self.tpl_path)
        
        # Identify template slide layouts
        # Layout [0]: 封面
        # Layout [1]: 目录
        # Layout [2]: 篇章过度页
        # Layout [3]: 空白
        # Layout [4]: 标题与内容
        # Layout [5]: 封底
        self.layout_cover = self.prs.slide_layouts[0]
        self.layout_agenda = self.prs.slide_layouts[1]
        self.layout_transition = self.prs.slide_layouts[2]
        self.layout_blank = self.prs.slide_layouts[3]
        self.layout_content = self.prs.slide_layouts[4]
        self.layout_closing = self.prs.slide_layouts[5]

        # Template comes with 4 initial sample slides, we can clear them or manage them
        self._clear_initial_slides()

    def _clear_initial_slides(self):
        """Clears default slides from the template cleanly."""
        while len(self.prs.slides) > 0:
            rId = self.prs.slides._sldIdLst[0].rId
            self.prs.part.drop_rel(rId)
            del self.prs.slides._sldIdLst[0]

    def add_cover(self, title: str, subtitle: str = "让有限更有效", copyright_text: str = "© 2026 合思信息 版权所有"):
        """Adds a standard Hosea cover slide."""
        slide = self.prs.slides.add_slide(self.layout_cover)
        
        # Main Title & Subtitle
        tb = slide.shapes.add_textbox(Inches(0.68), Inches(2.2), Inches(10.0), Inches(2.8))
        tf = tb.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
        
        # Slogan / Super Header
        p0 = tf.paragraphs[0]
        r0 = p0.add_run()
        r0.text = "未来财务用合思"
        r0.font.name = FONT_MAJOR
        r0.font.size = Pt(20)
        r0.font.bold = True
        r0.font.color.rgb = COLOR_PRIMARY_BLUE
        p0.space_after = Pt(12)

        # Big Title
        p1 = tf.add_paragraph()
        r1 = p1.add_run()
        r1.text = title
        r1.font.name = FONT_MAJOR
        r1.font.size = Pt(40)
        r1.font.bold = True
        r1.font.color.rgb = COLOR_TEXT_DARK
        p1.space_after = Pt(16)

        # Subtitle
        if subtitle:
            p2 = tf.add_paragraph()
            r2 = p2.add_run()
            r2.text = subtitle
            r2.font.name = FONT_MAJOR
            r2.font.size = Pt(22)
            r2.font.color.rgb = COLOR_TEXT_MUTED

        # Bottom Copyright
        tb_cp = slide.shapes.add_textbox(Inches(0.72), Inches(6.9), Inches(8.0), Inches(0.4))
        tf_cp = tb_cp.text_frame
        p_cp = tf_cp.paragraphs[0]
        r_cp = p_cp.add_run()
        r_cp.text = copyright_text
        r_cp.font.name = FONT_MINOR
        r_cp.font.size = Pt(9)
        r_cp.font.color.rgb = COLOR_TEXT_MUTED
        return slide

    def add_agenda(self, items: List[str]):
        """Adds a Table of Contents slide with Hosea agenda styling."""
        slide = self.prs.slides.add_slide(self.layout_blank)
        
        # Left sidebar
        sidebar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(3.5), Inches(7.5))
        sidebar.fill.solid()
        sidebar.fill.fore_color.rgb = COLOR_BG_LIGHT
        sidebar.line.fill.background()

        # Accent vertical bar
        bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(3.35), Inches(0.8), Inches(0.15), Inches(5.9))
        bar.fill.solid()
        bar.fill.fore_color.rgb = COLOR_PRIMARY_BLUE
        bar.line.fill.background()

        # "目录" and "Contents"
        tb_m = slide.shapes.add_textbox(Inches(1.8), Inches(0.8), Inches(1.3), Inches(1.5))
        tf_m = tb_m.text_frame
        p_m = tf_m.paragraphs[0]
        r_m = p_m.add_run()
        r_m.text = "目录"
        r_m.font.name = FONT_MAJOR
        r_m.font.size = Pt(36)
        r_m.font.bold = True
        r_m.font.color.rgb = COLOR_TEXT_DARK
        
        p_c = tf_m.add_paragraph()
        r_c = p_c.add_run()
        r_c.text = "Contents"
        r_c.font.name = FONT_MAJOR
        r_c.font.size = Pt(14)
        r_c.font.bold = True
        r_c.font.color.rgb = COLOR_ACCENT_GREEN

        # Agenda items
        start_y = Inches(1.8)
        card_w = Inches(8.5)
        card_h = Inches(0.75)
        gap = Inches(0.4)
        
        for idx, text in enumerate(items[:5]):
            y = start_y + idx * (card_h + gap)
            # Card
            card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(3.8), y, card_w, card_h)
            apply_card_style(card)
            
            # Badge 01.
            create_number_badge(slide, Inches(4.1), y + Inches(0.12), f"{idx+1:02d}", font_size=26)
            
            # Text
            tb_txt = slide.shapes.add_textbox(Inches(5.0), y + Inches(0.16), Inches(7.0), Inches(0.5))
            tf_txt = tb_txt.text_frame
            tf_txt.word_wrap = True
            p_txt = tf_txt.paragraphs[0]
            r_txt = p_txt.add_run()
            r_txt.text = text
            r_txt.font.name = FONT_MAJOR
            r_txt.font.size = Pt(18)
            r_txt.font.bold = True
            r_txt.font.color.rgb = COLOR_TEXT_DARK
        return slide

    def add_transition(self, chapter_num: str, chapter_title: str):
        """Adds a Chapter Transition slide."""
        slide = self.prs.slides.add_slide(self.layout_transition)
        # Background card
        card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.5), Inches(2.2), Inches(10.33), Inches(3.1))
        apply_card_style(card)
        
        # Chapter Number Badge (Large)
        create_number_badge(slide, Inches(6.0), Inches(2.6), chapter_num, font_size=48)
        
        # Chapter Title
        tb = slide.shapes.add_textbox(Inches(2.0), Inches(3.8), Inches(9.33), Inches(1.0))
        tf = tb.text_frame
        p = tf.paragraphs[0]
        p.alignment = PP_ALIGN.CENTER
        r = p.add_run()
        r.text = chapter_title
        r.font.name = FONT_MAJOR
        r.font.size = Pt(28)
        r.font.bold = True
        r.font.color.rgb = COLOR_TEXT_DARK
        return slide

    def add_cards_slide(self, title: str, cards: List[Dict[str, Any]]):
        """Adds a multi-column card slide (2, 3, or 4 columns) with icons and balanced spacing."""
        slide = self.prs.slides.add_slide(self.layout_content)
        set_slide_title(slide, title)
        
        n = len(cards)
        n = max(1, min(4, n))
        
        # Check if cards have tags or extra content
        has_any_tag = any(bool(c.get("tag") or c.get("kpi_tag") or c.get("scenario")) for c in cards)
        
        # Adaptive card height and vertical centering
        card_h = Inches(4.75) if has_any_tag else Inches(4.35)
        # Vertically center between y=1.35" and y=7.0"
        card_y = Inches(1.35) + (Inches(5.65) - card_h) / 2
        
        total_w = Inches(12.0)
        spacing = Inches(0.35)
        card_w = (total_w - spacing * (n - 1)) / n
        start_x = Inches(0.66) + (Inches(12.0) - (card_w * n + spacing * (n - 1))) / 2

        for i, card_info in enumerate(cards[:4]):
            x = start_x + i * (card_w + spacing)
            
            # 1. Main Card Container
            shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, card_y, card_w, card_h)
            apply_card_style(shape, highlighted=card_info.get("highlighted", False))
            
            # 2. Top Header Row: Icon Badge (Left) & Number Badge (Right)
            icon_name = card_info.get("icon", "")
            if not icon_name:
                t_lower = card_info.get("title", "")
                if "报销" in t_lower or "费控" in t_lower: icon_name = "receipt"
                elif "凭证" in t_lower or "会计" in t_lower or "核算" in t_lower: icon_name = "cpu"
                elif "看板" in t_lower or "经营" in t_lower or "分析" in t_lower: icon_name = "bar-chart"
                elif "风控" in t_lower or "合规" in t_lower: icon_name = "shield-check"
                elif "痛点" in t_lower or "瓶颈" in t_lower or "体验" in t_lower: icon_name = "alert-triangle"
                elif "盲" in t_lower or "视线" in t_lower: icon_name = "layers"
                else: icon_name = "sparkles"
                
            if generate_icon_badge:
                icon_png_path = generate_icon_badge(icon_name, "2455FF", bg_style="rounded_pill", size_px=128)
                if os.path.exists(icon_png_path):
                    slide.shapes.add_picture(icon_png_path, x + Inches(0.25), card_y + Inches(0.25), Inches(0.55), Inches(0.55))
            
            num_str = card_info.get("num", f"{i+1:02d}")
            create_number_badge(slide, x + card_w - Inches(0.95), card_y + Inches(0.22), num_str, font_size=24)
            
            # 3. Card Title
            tb_title = slide.shapes.add_textbox(x + Inches(0.25), card_y + Inches(0.95), card_w - Inches(0.5), Inches(0.55))
            tf_title = tb_title.text_frame
            tf_title.word_wrap = True
            tf_title.margin_left = tf_title.margin_top = tf_title.margin_right = tf_title.margin_bottom = 0
            p_title = tf_title.paragraphs[0]
            r_title = p_title.add_run()
            r_title.text = card_info.get("title", "")
            apply_font_to_run(r_title, font_name=FONT_MAJOR, size=16.5, bold=True, color=COLOR_TEXT_DARK)
            
            # 4. Content / Description & Bullets
            tb = slide.shapes.add_textbox(x + Inches(0.25), card_y + Inches(1.55), card_w - Inches(0.5), card_h - Inches(2.2))
            tf = tb.text_frame
            tf.word_wrap = True
            tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
            
            desc = card_info.get("desc", "")
            if desc:
                p_desc = tf.paragraphs[0]
                r_desc = p_desc.add_run()
                r_desc.text = desc
                apply_font_to_run(r_desc, font_name=FONT_MINOR, size=11.5, color=COLOR_TEXT_MUTED)
                p_desc.space_after = Pt(10)

            # Bullet points
            bullets = card_info.get("bullets", [])
            for b_idx, b_text in enumerate(bullets):
                p_b = tf.add_paragraph() if (desc or b_idx > 0) else tf.paragraphs[0]
                p_b.space_before = Pt(5)
                
                # Checkmark
                r_icon = p_b.add_run()
                r_icon.text = "✔ "
                apply_font_to_run(r_icon, font_name=FONT_MAJOR, size=10, bold=True, color=COLOR_PRIMARY_BLUE)
                
                r_b = p_b.add_run()
                r_b.text = b_text
                apply_font_to_run(r_b, font_name=FONT_MINOR, size=11, color=COLOR_TEXT_DARK)

            # 5. Bottom Anchor Tag / Pill (if provided, or inferred scenario)
            tag_text = card_info.get("tag") or card_info.get("kpi_tag") or card_info.get("scenario")
            if not tag_text and has_any_tag:
                tag_text = f"合思最佳实践 · {num_str}"
                
            if tag_text:
                tag_box = slide.shapes.add_shape(
                    MSO_SHAPE.ROUNDED_RECTANGLE,
                    x + Inches(0.22),
                    card_y + card_h - Inches(0.55),
                    card_w - Inches(0.44),
                    Inches(0.36)
                )
                tag_box.fill.solid()
                tag_box.fill.fore_color.rgb = RGBColor(0xF0, 0xF4, 0xFF)
                tag_box.line.color.rgb = RGBColor(0xD5, 0xE2, 0xFF)
                tag_box.line.width = Pt(1)
                
                tf_tag = tag_box.text_frame
                tf_tag.word_wrap = False
                p_tag = tf_tag.paragraphs[0]
                p_tag.alignment = PP_ALIGN.CENTER
                r_tag = p_tag.add_run()
                r_tag.text = tag_text
                apply_font_to_run(r_tag, font_name=FONT_MAJOR, size=10, bold=True, color=COLOR_PRIMARY_BLUE)
                
        return slide

    def add_kpi_slide(self, title: str, metrics: List[Dict[str, str]], summary: str = ""):
        """Adds a KPI / Highlights metrics slide with balanced vertical spacing."""
        slide = self.prs.slides.add_slide(self.layout_content)
        set_slide_title(slide, title)
        
        n = min(4, len(metrics))
        total_w = Inches(12.0)
        spacing = Inches(0.35)
        card_w = (total_w - spacing * (n - 1)) / n
        start_x = Inches(0.66) + (Inches(12.0) - (card_w * n + spacing * (n - 1))) / 2
        card_h = Inches(3.2)
        card_y = Inches(1.85)

        for i, item in enumerate(metrics[:n]):
            x = start_x + i * (card_w + spacing)
            
            # Container
            shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, card_y, card_w, card_h)
            apply_card_style(shape)
            
            tb = slide.shapes.add_textbox(x + Inches(0.15), card_y + Inches(0.35), card_w - Inches(0.3), card_h - Inches(0.7))
            tf = tb.text_frame
            tf.word_wrap = True
            
            # Big Metric Number
            p_val = tf.paragraphs[0]
            p_val.alignment = PP_ALIGN.CENTER
            r_val = p_val.add_run()
            r_val.text = item.get("value", "")
            apply_font_to_run(r_val, font_name=FONT_MAJOR, size=42, bold=True, color=COLOR_PRIMARY_BLUE)
            
            # Metric Label
            p_lbl = tf.add_paragraph()
            p_lbl.alignment = PP_ALIGN.CENTER
            p_lbl.space_before = Pt(8)
            r_lbl = p_lbl.add_run()
            r_lbl.text = item.get("label", "")
            apply_font_to_run(r_lbl, font_name=FONT_MAJOR, size=15, bold=True, color=COLOR_TEXT_DARK)
            
            # Metric Description
            desc = item.get("desc", "")
            if desc:
                p_desc = tf.add_paragraph()
                p_desc.alignment = PP_ALIGN.CENTER
                p_desc.space_before = Pt(8)
                r_desc = p_desc.add_run()
                r_desc.text = desc
                apply_font_to_run(r_desc, font_name=FONT_MINOR, size=11, color=COLOR_TEXT_MUTED)

        if summary:
            # Summary bottom card
            sum_card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.66), Inches(5.35), Inches(12.0), Inches(1.3))
            sum_card.fill.solid()
            sum_card.fill.fore_color.rgb = COLOR_WHITE
            sum_card.line.color.rgb = COLOR_BORDER_LIGHT
            
            tb_s = slide.shapes.add_textbox(Inches(0.9), Inches(5.5), Inches(11.5), Inches(1.0))
            tf_s = tb_s.text_frame
            tf_s.word_wrap = True
            p_s = tf_s.paragraphs[0]
            
            r_tag = p_s.add_run()
            r_tag.text = "💡 核心成效： "
            apply_font_to_run(r_tag, font_name=FONT_MAJOR, size=13, bold=True, color=COLOR_PRIMARY_BLUE)
            
            r_txt = p_s.add_run()
            r_txt.text = summary
            apply_font_to_run(r_txt, font_name=FONT_MINOR, size=12, color=COLOR_TEXT_DARK)
        return slide

    def add_closing(self):
        """Appends the standard Hosea back cover with China map and contact info."""
        slide = self.prs.slides.add_slide(self.layout_closing)
        return slide

    def save(self, output_path: str):
        """Enforces 微软雅黑 across all runs and saves the presentation."""
        for slide in self.prs.slides:
            for shape in slide.shapes:
                if shape.has_text_frame:
                    for paragraph in shape.text_frame.paragraphs:
                        for run in paragraph.runs:
                            apply_font_to_run(run, font_name="微软雅黑")
        self.prs.save(output_path)
        print(f"Presentation saved successfully to: {output_path}")

# ==============================================================================
# CLI and JSON Driver
# ==============================================================================
def build_deck_from_json(json_path: str, output_path: str):
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    builder = HoseaDeckBuilder()
    
    # 1. Cover
    cover_data = data.get("cover", {})
    builder.add_cover(
        title=cover_data.get("title", "合思企业解决方案"),
        subtitle=cover_data.get("subtitle", "让有限更有效"),
        copyright_text=cover_data.get("copyright", "© 2026 合思信息 版权所有")
    )
    
    # 2. Agenda
    agenda_items = data.get("agenda", [])
    if agenda_items:
        builder.add_agenda(agenda_items)
        
    # 3. Slides
    for slide_data in data.get("slides", []):
        stype = slide_data.get("type", "cards")
        title = slide_data.get("title", "")
        
        if stype == "transition":
            builder.add_transition(slide_data.get("number", "01"), title)
        elif stype == "cards":
            builder.add_cards_slide(title, slide_data.get("cards", []))
        elif stype == "kpi":
            builder.add_kpi_slide(title, slide_data.get("metrics", []), slide_data.get("summary", ""))
            
    # 4. Closing
    if data.get("include_closing", True):
        builder.add_closing()
        
    builder.save(output_path)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Hosea PPT Generator")
    parser.add_argument("--input", "-i", type=str, help="Path to input JSON outline")
    parser.add_argument("--output", "-o", type=str, default="合思汇报演示.pptx", help="Path to output PPTX")
    args = parser.parse_args()
    
    if args.input:
        build_deck_from_json(args.input, args.output)
    else:
        print("Hosea PPT Generator ready. Use --input <outline.json> --output <deck.pptx>")
