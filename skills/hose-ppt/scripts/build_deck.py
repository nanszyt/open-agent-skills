"""
Hosea & Executive PPT Generator Script (合思与通用高端演示文稿自动化构建引擎)
Dual-Mode Engine:
  1. Hosea Corporate Master Mode (合思官方母版模式，深度对齐 template.pptx 与品牌规范)
  2. Universal High-End Executive Mode (通用高端演示设计模式，支持多主题与 8 大经典版式)

Supported 8 Major Slide Archetypes:
  1. cards: 多栏结构化卡片 (2/3/4 列，含图标徽章、序号、Checklist、场景标签)
  2. compare: 现状痛点 vs 创新方案 (Before vs After 对比页，中间 VS 引导胶囊)
  3. process: 横向阶段推进流程 (3~5 步流转卡片，带引导箭头与交付物标牌)
  4. kpi: 核心成效与数据看板 (大数字 48-60pt，增长标签，底部总结框)
  5. stack: 分层架构与能力全景 (4 层横向架构图，左侧标牌 + 右侧组件胶囊)
  6. split: 左右非对称叙事 (左侧 40% 核心洞见卡 + 右侧 60% 落地动作卡)
  7. timeline: 时间轴演进路线 (阶段节点、横向轨迹、里程碑目标)
  8. case: 标杆案例与客户证言 (大字引言 + 3 个量化收益微卡片)
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
except Exception:
    generate_icon_badge = None

# ==============================================================================
# Curated Palettes & Themes (兼顾合思官方与通用高管汇报)
# ==============================================================================
THEMES = {
    "hosea": {
        "name": "合思科技蓝 (Hosea Official)",
        "primary": RGBColor(0x24, 0x55, 0xFF),     # #2455FF 电光科技蓝
        "accent": RGBColor(0x34, 0xDE, 0x4C),      # #34DE4C 荧光生机绿
        "text_dark": RGBColor(0x30, 0x3B, 0x47),   # #303B47 沉稳灰蓝
        "text_muted": RGBColor(0x71, 0x80, 0x96),  # #718096 辅助灰
        "bg_light": RGBColor(0xF7, 0xF7, 0xF7),    # #F7F7F7 浅底背景
        "card_bg": RGBColor(0xFF, 0xFF, 0xFF),     # 纯白卡片
        "border_light": RGBColor(0xEA, 0xEE, 0xF5),# 微边框
        "pill_bg": RGBColor(0xF0, 0xF4, 0xFF),     # 标签胶囊浅蓝底
        "pill_border": RGBColor(0xD5, 0xE2, 0xFF), # 标签胶囊边框
        "warn_bg": RGBColor(0xFF, 0xF5, 0xF5),     # 痛点浅红底
        "warn_border": RGBColor(0xFE, 0xD7, 0xD7), # 痛点边框
        "warn_text": RGBColor(0xE5, 0x3E, 0x3E)    # 痛点红
    },
    "midnight": {
        "name": "午夜深蓝 (Midnight Executive)",
        "primary": RGBColor(0x1E, 0x27, 0x61),
        "accent": RGBColor(0x4F, 0x9D, 0xDE),
        "text_dark": RGBColor(0x0B, 0x13, 0x2B),
        "text_muted": RGBColor(0x64, 0x74, 0x8B),
        "bg_light": RGBColor(0xF8, 0xFA, 0xFC),
        "card_bg": RGBColor(0xFF, 0xFF, 0xFF),
        "border_light": RGBColor(0xE2, 0xE8, 0xF0),
        "pill_bg": RGBColor(0xED, 0xF4, 0xFC),
        "pill_border": RGBColor(0xCB, 0xDE, 0xF8),
        "warn_bg": RGBColor(0xFF, 0xF5, 0xF5),
        "warn_border": RGBColor(0xFE, 0xD7, 0xD7),
        "warn_text": RGBColor(0xDC, 0x26, 0x26)
    },
    "emerald": {
        "name": "翡翠生机 (Emerald Growth)",
        "primary": RGBColor(0x10, 0x7C, 0x41),
        "accent": RGBColor(0x34, 0xD3, 0x99),
        "text_dark": RGBColor(0x1C, 0x2D, 0x27),
        "text_muted": RGBColor(0x4B, 0x55, 0x63),
        "bg_light": RGBColor(0xF9, 0xFA, 0xF8),
        "card_bg": RGBColor(0xFF, 0xFF, 0xFF),
        "border_light": RGBColor(0xE5, 0xE7, 0xEB),
        "pill_bg": RGBColor(0xEC, 0xFD, 0xF5),
        "pill_border": RGBColor(0xA7, 0xF3, 0xD0),
        "warn_bg": RGBColor(0xFF, 0xF5, 0xF5),
        "warn_border": RGBColor(0xFE, 0xD7, 0xD7),
        "warn_text": RGBColor(0xDC, 0x26, 0x26)
    },
    "purple": {
        "name": "前沿紫光 (Deep Purple AI)",
        "primary": RGBColor(0x6D, 0x28, 0xD9),
        "accent": RGBColor(0xA7, 0x8B, 0xFA),
        "text_dark": RGBColor(0x1E, 0x1B, 0x4B),
        "text_muted": RGBColor(0x6B, 0x72, 0x80),
        "bg_light": RGBColor(0xFA, 0xF5, 0xFF),
        "card_bg": RGBColor(0xFF, 0xFF, 0xFF),
        "border_light": RGBColor(0xF3, 0xE8, 0xFF),
        "pill_bg": RGBColor(0xF3, 0xE8, 0xFF),
        "pill_border": RGBColor(0xD8, 0xB4, 0xFE),
        "warn_bg": RGBColor(0xFF, 0xF5, 0xF5),
        "warn_border": RGBColor(0xFE, 0xD7, 0xD7),
        "warn_text": RGBColor(0xDC, 0x26, 0x26)
    }
}

DEFAULT_TEMPLATE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'resources', 'template.pptx')
FONT_NAME = "微软雅黑"

# ==============================================================================
# Formatting & Styling Helpers
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

def create_number_badge(slide, x, y, num_str: str, font_size=28, primary_color=None, accent_color=None):
    """Creates the signature Hosea '01.' badge: Blue number with Green dot."""
    tb = slide.shapes.add_textbox(x, y, Inches(1.5), Inches(0.6))
    tf = tb.text_frame
    tf.word_wrap = False
    tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
    p = tf.paragraphs[0]
    
    r1 = p.add_run()
    r1.text = num_str
    apply_font_to_run(r1, font_name=FONT_NAME, size=font_size, bold=True, color=primary_color or THEMES["hosea"]["primary"])
    
    r2 = p.add_run()
    r2.text = "."
    apply_font_to_run(r2, font_name=FONT_NAME, size=font_size, bold=True, color=accent_color or THEMES["hosea"]["accent"])
    return tb

def apply_card_style(shape, bg_color=None, border_color=None, border_width_pt=1):
    """Applies clean card styling with subtle rounded outline."""
    shape.fill.solid()
    shape.fill.fore_color.rgb = bg_color or RGBColor(0xFF, 0xFF, 0xFF)
    shape.line.width = Pt(border_width_pt)
    shape.line.color.rgb = border_color or THEMES["hosea"]["border_light"]

# ==============================================================================
# Deck Builder Engine
# ==============================================================================
class HoseaDeckBuilder:
    def __init__(self, template_path: Optional[str] = None, theme_key: str = "hosea"):
        self.theme_key = theme_key if theme_key in THEMES else "hosea"
        self.theme = THEMES[self.theme_key]
        
        self.tpl_path = template_path or (DEFAULT_TEMPLATE if os.path.exists(DEFAULT_TEMPLATE) else None)
        if self.tpl_path and os.path.exists(self.tpl_path):
            self.prs = Presentation(self.tpl_path)
            self.has_template = True
            self.layout_cover = self.prs.slide_layouts[0]
            self.layout_agenda = self.prs.slide_layouts[1]
            self.layout_transition = self.prs.slide_layouts[2]
            self.layout_blank = self.prs.slide_layouts[3]
            self.layout_content = self.prs.slide_layouts[4]
            self.layout_closing = self.prs.slide_layouts[5]
            self._clear_initial_slides()
        else:
            self.prs = Presentation()
            self.prs.slide_width = Inches(13.33)
            self.prs.slide_height = Inches(7.50)
            self.has_template = False
            self.layout_cover = self.prs.slide_layouts[0]
            self.layout_agenda = self.prs.slide_layouts[6]
            self.layout_transition = self.prs.slide_layouts[6]
            self.layout_blank = self.prs.slide_layouts[6]
            self.layout_content = self.prs.slide_layouts[6]
            self.layout_closing = self.prs.slide_layouts[6]

    def _clear_initial_slides(self):
        while len(self.prs.slides) > 0:
            rId = self.prs.slides._sldIdLst[0].rId
            self.prs.part.drop_rel(rId)
            del self.prs.slides._sldIdLst[0]

    def _set_slide_title(self, slide, title_text: str):
        """Sets standard centered slide title."""
        if self.has_template and slide.shapes.title:
            slide.shapes.title.text = title_text
            p = slide.shapes.title.text_frame.paragraphs[0]
            p.alignment = PP_ALIGN.CENTER
            for r in p.runs:
                apply_font_to_run(r, font_name=FONT_NAME, size=22, bold=True, color=self.theme["text_dark"])
        else:
            tb = slide.shapes.add_textbox(Inches(0.66), Inches(0.48), Inches(12.0), Inches(0.8))
            tf = tb.text_frame
            tf.word_wrap = True
            p = tf.paragraphs[0]
            p.alignment = PP_ALIGN.CENTER
            r = p.add_run()
            r.text = title_text
            apply_font_to_run(r, font_name=FONT_NAME, size=24, bold=True, color=self.theme["text_dark"])

    # --------------------------------------------------------------------------
    # 0. Cover, Agenda, Transition, Closing
    # --------------------------------------------------------------------------
    def add_cover(self, title: str, subtitle: str = "让有限更有效", copyright_text: str = "© 2026 合思信息 版权所有"):
        slide = self.prs.slides.add_slide(self.layout_cover)
        tb = slide.shapes.add_textbox(Inches(0.68), Inches(2.2), Inches(10.0), Inches(2.8))
        tf = tb.text_frame
        tf.word_wrap = True
        
        # Slogan
        p0 = tf.paragraphs[0]
        r0 = p0.add_run()
        r0.text = "未来财务用合思" if self.theme_key == "hosea" else "EXECUTIVE PRESENTATION"
        apply_font_to_run(r0, font_name=FONT_NAME, size=18, bold=True, color=self.theme["primary"])
        p0.space_after = Pt(12)

        # Title
        p1 = tf.add_paragraph()
        r1 = p1.add_run()
        r1.text = title
        apply_font_to_run(r1, font_name=FONT_NAME, size=40, bold=True, color=self.theme["text_dark"])
        p1.space_after = Pt(16)

        # Subtitle
        if subtitle:
            p2 = tf.add_paragraph()
            r2 = p2.add_run()
            r2.text = subtitle
            apply_font_to_run(r2, font_name=FONT_NAME, size=20, color=self.theme["text_muted"])

        # Copyright
        tb_cp = slide.shapes.add_textbox(Inches(0.72), Inches(6.9), Inches(8.0), Inches(0.4))
        p_cp = tb_cp.text_frame.paragraphs[0]
        r_cp = p_cp.add_run()
        r_cp.text = copyright_text
        apply_font_to_run(r_cp, font_name=FONT_NAME, size=9, color=self.theme["text_muted"])
        return slide

    def add_agenda(self, items: List[str]):
        slide = self.prs.slides.add_slide(self.layout_blank)
        
        # Left sidebar
        sidebar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(3.5), Inches(7.5))
        sidebar.fill.solid()
        sidebar.fill.fore_color.rgb = self.theme["bg_light"]
        sidebar.line.fill.background()

        # Accent bar
        bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(3.35), Inches(0.8), Inches(0.15), Inches(5.9))
        bar.fill.solid()
        bar.fill.fore_color.rgb = self.theme["primary"]
        bar.line.fill.background()

        # Title
        tb_m = slide.shapes.add_textbox(Inches(1.8), Inches(0.8), Inches(1.3), Inches(1.5))
        tf_m = tb_m.text_frame
        p_m = tf_m.paragraphs[0]
        r_m = p_m.add_run()
        r_m.text = "目录"
        apply_font_to_run(r_m, font_name=FONT_NAME, size=36, bold=True, color=self.theme["text_dark"])
        
        p_c = tf_m.add_paragraph()
        r_c = p_c.add_run()
        r_c.text = "Contents"
        apply_font_to_run(r_c, font_name=FONT_NAME, size=14, bold=True, color=self.theme["accent"])

        # Items
        start_y = Inches(1.8)
        card_w = Inches(8.5)
        card_h = Inches(0.75)
        gap = Inches(0.4)
        
        for idx, text in enumerate(items[:5]):
            y = start_y + idx * (card_h + gap)
            card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(3.8), y, card_w, card_h)
            apply_card_style(card, border_color=self.theme["border_light"])
            create_number_badge(slide, Inches(4.1), y + Inches(0.12), f"{idx+1:02d}", font_size=26,
                                primary_color=self.theme["primary"], accent_color=self.theme["accent"])
            
            tb_txt = slide.shapes.add_textbox(Inches(5.0), y + Inches(0.16), Inches(7.0), Inches(0.5))
            p_txt = tb_txt.text_frame.paragraphs[0]
            r_txt = p_txt.add_run()
            r_txt.text = text
            apply_font_to_run(r_txt, font_name=FONT_NAME, size=18, bold=True, color=self.theme["text_dark"])
        return slide

    def add_transition(self, chapter_num: str, chapter_title: str):
        slide = self.prs.slides.add_slide(self.layout_transition)
        card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.5), Inches(2.2), Inches(10.33), Inches(3.1))
        apply_card_style(card, border_color=self.theme["border_light"])
        
        create_number_badge(slide, Inches(6.0), Inches(2.6), chapter_num, font_size=48,
                            primary_color=self.theme["primary"], accent_color=self.theme["accent"])
        
        tb = slide.shapes.add_textbox(Inches(2.0), Inches(3.8), Inches(9.33), Inches(1.0))
        p = tb.text_frame.paragraphs[0]
        p.alignment = PP_ALIGN.CENTER
        r = p.add_run()
        r.text = chapter_title
        apply_font_to_run(r, font_name=FONT_NAME, size=28, bold=True, color=self.theme["text_dark"])
        return slide

    # --------------------------------------------------------------------------
    # 1. Archetype: cards (多栏结构化卡片 2/3/4 列)
    # --------------------------------------------------------------------------
    def add_cards_slide(self, title: str, cards: List[Dict[str, Any]]):
        slide = self.prs.slides.add_slide(self.layout_content)
        self._set_slide_title(slide, title)
        
        n = max(1, min(4, len(cards)))
        has_any_tag = any(bool(c.get("tag") or c.get("kpi_tag") or c.get("scenario")) for c in cards)
        card_h = Inches(4.75) if has_any_tag else Inches(4.35)
        card_y = Inches(1.35) + (Inches(5.65) - card_h) / 2
        
        total_w = Inches(12.0)
        spacing = Inches(0.35)
        card_w = (total_w - spacing * (n - 1)) / n
        start_x = Inches(0.66) + (Inches(12.0) - (card_w * n + spacing * (n - 1))) / 2

        for i, card_info in enumerate(cards[:4]):
            x = start_x + i * (card_w + spacing)
            shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, card_y, card_w, card_h)
            apply_card_style(shape, border_color=self.theme["primary"] if card_info.get("highlighted") else self.theme["border_light"])
            
            # Icon Badge
            icon_name = card_info.get("icon", "sparkles")
            if generate_icon_badge:
                color_hex = f"{self.theme['primary'][0]:02x}{self.theme['primary'][1]:02x}{self.theme['primary'][2]:02x}"
                icon_path = generate_icon_badge(icon_name, color_hex, bg_style="rounded_pill", size_px=128)
                if os.path.exists(icon_path):
                    slide.shapes.add_picture(icon_path, x + Inches(0.25), card_y + Inches(0.25), Inches(0.55), Inches(0.55))
            
            # Number badge
            num_str = card_info.get("num", f"{i+1:02d}")
            create_number_badge(slide, x + card_w - Inches(0.95), card_y + Inches(0.22), num_str, font_size=24,
                                primary_color=self.theme["primary"], accent_color=self.theme["accent"])
            
            # Title
            tb_title = slide.shapes.add_textbox(x + Inches(0.25), card_y + Inches(0.95), card_w - Inches(0.5), Inches(0.55))
            tf_title = tb_title.text_frame
            tf_title.word_wrap = True
            p_title = tf_title.paragraphs[0]
            r_title = p_title.add_run()
            r_title.text = card_info.get("title", "")
            apply_font_to_run(r_title, font_name=FONT_NAME, size=16.5, bold=True, color=self.theme["text_dark"])
            
            # Desc & Bullets
            tb = slide.shapes.add_textbox(x + Inches(0.25), card_y + Inches(1.55), card_w - Inches(0.5), card_h - Inches(2.2))
            tf = tb.text_frame
            tf.word_wrap = True
            
            desc = card_info.get("desc", "")
            if desc:
                p_desc = tf.paragraphs[0]
                r_desc = p_desc.add_run()
                r_desc.text = desc
                apply_font_to_run(r_desc, font_name=FONT_NAME, size=11.5, color=self.theme["text_muted"])
                p_desc.space_after = Pt(10)

            for b_idx, b_text in enumerate(card_info.get("bullets", [])):
                p_b = tf.add_paragraph() if (desc or b_idx > 0) else tf.paragraphs[0]
                p_b.space_before = Pt(5)
                r_icon = p_b.add_run()
                r_icon.text = "✔ "
                apply_font_to_run(r_icon, font_name=FONT_NAME, size=10, bold=True, color=self.theme["primary"])
                r_b = p_b.add_run()
                r_b.text = b_text
                apply_font_to_run(r_b, font_name=FONT_NAME, size=11, color=self.theme["text_dark"])

            # Tag Pill
            tag_text = card_info.get("tag") or card_info.get("kpi_tag") or card_info.get("scenario")
            if not tag_text and has_any_tag:
                tag_text = f"最佳实践 · {num_str}"
            if tag_text:
                tag_box = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x + Inches(0.22), card_y + card_h - Inches(0.55), card_w - Inches(0.44), Inches(0.36))
                apply_card_style(tag_box, bg_color=self.theme["pill_bg"], border_color=self.theme["pill_border"])
                p_tag = tag_box.text_frame.paragraphs[0]
                p_tag.alignment = PP_ALIGN.CENTER
                r_tag = p_tag.add_run()
                r_tag.text = tag_text
                apply_font_to_run(r_tag, font_name=FONT_NAME, size=10, bold=True, color=self.theme["primary"])
        return slide

    # --------------------------------------------------------------------------
    # 2. Archetype: compare (现状痛点 vs 创新方案 / Before vs After)
    # --------------------------------------------------------------------------
    def add_compare_slide(self, title: str, before: Dict[str, Any], after: Dict[str, Any]):
        slide = self.prs.slides.add_slide(self.layout_content)
        self._set_slide_title(slide, title)
        
        card_w = Inches(5.6)
        card_h = Inches(4.7)
        card_y = Inches(1.8)
        left_x = Inches(0.76)
        right_x = Inches(6.96)
        
        # 1. Left Card: Before (痛点/传统模式)
        card_l = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left_x, card_y, card_w, card_h)
        apply_card_style(card_l, bg_color=self.theme["warn_bg"], border_color=self.theme["warn_border"], border_width_pt=1.5)
        
        # Top title badge
        tb_lt = slide.shapes.add_textbox(left_x + Inches(0.35), card_y + Inches(0.35), card_w - Inches(0.7), Inches(0.6))
        p_lt = tb_lt.text_frame.paragraphs[0]
        r_lt = p_lt.add_run()
        r_lt.text = f"⚠️ {before.get('title', '传统模式 / 业务痛点 (Before)')}"
        apply_font_to_run(r_lt, font_name=FONT_NAME, size=18, bold=True, color=self.theme["warn_text"])
        
        # Bullets
        tb_lc = slide.shapes.add_textbox(left_x + Inches(0.35), card_y + Inches(1.1), card_w - Inches(0.7), card_h - Inches(1.8))
        tf_lc = tb_lc.text_frame
        tf_lc.word_wrap = True
        desc_l = before.get("desc", "")
        if desc_l:
            p_dl = tf_lc.paragraphs[0]
            r_dl = p_dl.add_run()
            r_dl.text = desc_l
            apply_font_to_run(r_dl, font_name=FONT_NAME, size=12, color=self.theme["text_muted"])
            p_dl.space_after = Pt(12)
            
        for idx, item in enumerate(before.get("points", [])):
            p = tf_lc.add_paragraph() if (desc_l or idx > 0) else tf_lc.paragraphs[0]
            p.space_before = Pt(8)
            r_icon = p.add_run()
            r_icon.text = "✕  "
            apply_font_to_run(r_icon, font_name=FONT_NAME, size=12, bold=True, color=self.theme["warn_text"])
            r_txt = p.add_run()
            r_txt.text = item
            apply_font_to_run(r_txt, font_name=FONT_NAME, size=12.5, color=self.theme["text_dark"])
            
        # 2. Right Card: After (创新方案/目标成效)
        card_r = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, right_x, card_y, card_w, card_h)
        apply_card_style(card_r, bg_color=self.theme["pill_bg"], border_color=self.theme["primary"], border_width_pt=1.5)
        
        tb_rt = slide.shapes.add_textbox(right_x + Inches(0.35), card_y + Inches(0.35), card_w - Inches(0.7), Inches(0.6))
        p_rt = tb_rt.text_frame.paragraphs[0]
        r_rt = p_rt.add_run()
        r_rt.text = f"✨ {after.get('title', '合思敏捷新模式 (After)')}"
        apply_font_to_run(r_rt, font_name=FONT_NAME, size=18, bold=True, color=self.theme["primary"])
        
        tb_rc = slide.shapes.add_textbox(right_x + Inches(0.35), card_y + Inches(1.1), card_w - Inches(0.7), card_h - Inches(1.8))
        tf_rc = tb_rc.text_frame
        tf_rc.word_wrap = True
        desc_r = after.get("desc", "")
        if desc_r:
            p_dr = tf_rc.paragraphs[0]
            r_dr = p_dr.add_run()
            r_dr.text = desc_r
            apply_font_to_run(r_dr, font_name=FONT_NAME, size=12, color=self.theme["text_muted"])
            p_dr.space_after = Pt(12)
            
        for idx, item in enumerate(after.get("points", [])):
            p = tf_rc.add_paragraph() if (desc_r or idx > 0) else tf_rc.paragraphs[0]
            p.space_before = Pt(8)
            r_icon = p.add_run()
            r_icon.text = "✔  "
            apply_font_to_run(r_icon, font_name=FONT_NAME, size=12, bold=True, color=self.theme["primary"])
            r_txt = p.add_run()
            r_txt.text = item
            apply_font_to_run(r_txt, font_name=FONT_NAME, size=12.5, color=self.theme["text_dark"])
            
        # 3. Center VS Capsule Badge
        vs_badge = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.05), card_y + card_h/2 - Inches(0.3), Inches(1.22), Inches(0.6))
        apply_card_style(vs_badge, bg_color=self.theme["primary"], border_color=self.theme["primary"])
        p_vs = vs_badge.text_frame.paragraphs[0]
        p_vs.alignment = PP_ALIGN.CENTER
        r_vs = p_vs.add_run()
        r_vs.text = "VS 升级"
        apply_font_to_run(r_vs, font_name=FONT_NAME, size=11, bold=True, color=RGBColor(0xFF, 0xFF, 0xFF))
        return slide

    # --------------------------------------------------------------------------
    # 3. Archetype: process (横向阶段推进流程 3~5 步)
    # --------------------------------------------------------------------------
    def add_process_slide(self, title: str, steps: List[Dict[str, Any]]):
        slide = self.prs.slides.add_slide(self.layout_content)
        self._set_slide_title(slide, title)
        
        n = max(3, min(5, len(steps)))
        total_w = Inches(12.0)
        gap = Inches(0.4)
        card_w = (total_w - gap * (n - 1)) / n
        card_h = Inches(4.7)
        card_y = Inches(1.8)
        start_x = Inches(0.66)

        for i, step in enumerate(steps[:n]):
            x = start_x + i * (card_w + gap)
            card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, card_y, card_w, card_h)
            apply_card_style(card, border_color=self.theme["border_light"])
            
            # Step Capsule (e.g. STEP 01)
            pill = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x + Inches(0.2), card_y + Inches(0.25), card_w - Inches(0.4), Inches(0.38))
            apply_card_style(pill, bg_color=self.theme["primary"], border_color=self.theme["primary"])
            p_pill = pill.text_frame.paragraphs[0]
            p_pill.alignment = PP_ALIGN.CENTER
            r_pill = p_pill.add_run()
            r_pill.text = f"PHASE {i+1:02d}"
            apply_font_to_run(r_pill, font_name=FONT_NAME, size=10, bold=True, color=RGBColor(0xFF, 0xFF, 0xFF))
            
            # Step Title
            tb_t = slide.shapes.add_textbox(x + Inches(0.15), card_y + Inches(0.8), card_w - Inches(0.3), Inches(0.6))
            p_t = tb_t.text_frame.paragraphs[0]
            p_t.alignment = PP_ALIGN.CENTER
            r_t = p_t.add_run()
            r_t.text = step.get("title", "")
            apply_font_to_run(r_t, font_name=FONT_NAME, size=15, bold=True, color=self.theme["text_dark"])
            
            # Bullets
            tb_b = slide.shapes.add_textbox(x + Inches(0.18), card_y + Inches(1.5), card_w - Inches(0.36), card_h - Inches(2.2))
            tf_b = tb_b.text_frame
            tf_b.word_wrap = True
            for b_idx, bullet in enumerate(step.get("bullets", [])):
                p = tf_b.add_paragraph() if b_idx > 0 else tf_b.paragraphs[0]
                p.space_before = Pt(6)
                r_dot = p.add_run()
                r_dot.text = "• "
                apply_font_to_run(r_dot, font_name=FONT_NAME, size=11, bold=True, color=self.theme["primary"])
                r_txt = p.add_run()
                r_txt.text = bullet
                apply_font_to_run(r_txt, font_name=FONT_NAME, size=11, color=self.theme["text_dark"])
                
            # Bottom deliverable tag
            deliverable = step.get("output", "")
            if deliverable:
                d_box = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x + Inches(0.15), card_y + card_h - Inches(0.55), card_w - Inches(0.3), Inches(0.35))
                apply_card_style(d_box, bg_color=self.theme["pill_bg"], border_color=self.theme["pill_border"])
                p_d = d_box.text_frame.paragraphs[0]
                p_d.alignment = PP_ALIGN.CENTER
                r_d = p_d.add_run()
                r_d.text = f"📦 {deliverable}"
                apply_font_to_run(r_d, font_name=FONT_NAME, size=9.5, bold=True, color=self.theme["primary"])
                
            # Arrow indicator between cards
            if i < n - 1:
                arrow_x = x + card_w + Inches(0.08)
                tb_arr = slide.shapes.add_textbox(arrow_x, card_y + card_h/2 - Inches(0.3), Inches(0.25), Inches(0.5))
                p_arr = tb_arr.text_frame.paragraphs[0]
                r_arr = p_arr.add_run()
                r_arr.text = "➔"
                apply_font_to_run(r_arr, font_name=FONT_NAME, size=18, bold=True, color=self.theme["accent"])
        return slide

    # --------------------------------------------------------------------------
    # 4. Archetype: kpi (核心成效与大数字看板)
    # --------------------------------------------------------------------------
    def add_kpi_slide(self, title: str, metrics: List[Dict[str, str]], summary: str = ""):
        slide = self.prs.slides.add_slide(self.layout_content)
        self._set_slide_title(slide, title)
        
        n = min(4, len(metrics))
        total_w = Inches(12.0)
        spacing = Inches(0.35)
        card_w = (total_w - spacing * (n - 1)) / n
        start_x = Inches(0.66) + (Inches(12.0) - (card_w * n + spacing * (n - 1))) / 2
        card_h = Inches(3.2)
        card_y = Inches(1.85)

        for i, item in enumerate(metrics[:n]):
            x = start_x + i * (card_w + spacing)
            shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, card_y, card_w, card_h)
            apply_card_style(shape, border_color=self.theme["border_light"])
            
            tb = slide.shapes.add_textbox(x + Inches(0.15), card_y + Inches(0.35), card_w - Inches(0.3), card_h - Inches(0.7))
            tf = tb.text_frame
            tf.word_wrap = True
            
            # Big Metric
            p_val = tf.paragraphs[0]
            p_val.alignment = PP_ALIGN.CENTER
            r_val = p_val.add_run()
            r_val.text = item.get("value", "")
            apply_font_to_run(r_val, font_name=FONT_NAME, size=46, bold=True, color=self.theme["primary"])
            
            # Label
            p_lbl = tf.add_paragraph()
            p_lbl.alignment = PP_ALIGN.CENTER
            p_lbl.space_before = Pt(8)
            r_lbl = p_lbl.add_run()
            r_lbl.text = item.get("label", "")
            apply_font_to_run(r_lbl, font_name=FONT_NAME, size=15, bold=True, color=self.theme["text_dark"])
            
            # Desc
            desc = item.get("desc", "")
            if desc:
                p_desc = tf.add_paragraph()
                p_desc.alignment = PP_ALIGN.CENTER
                p_desc.space_before = Pt(8)
                r_desc = p_desc.add_run()
                r_desc.text = desc
                apply_font_to_run(r_desc, font_name=FONT_NAME, size=11, color=self.theme["text_muted"])

        if summary:
            sum_card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.66), Inches(5.35), Inches(12.0), Inches(1.3))
            apply_card_style(sum_card, bg_color=self.theme["card_bg"], border_color=self.theme["border_light"])
            
            tb_s = slide.shapes.add_textbox(Inches(0.9), Inches(5.5), Inches(11.5), Inches(1.0))
            tf_s = tb_s.text_frame
            tf_s.word_wrap = True
            p_s = tf_s.paragraphs[0]
            r_tag = p_s.add_run()
            r_tag.text = "💡 核心成效： "
            apply_font_to_run(r_tag, font_name=FONT_NAME, size=13, bold=True, color=self.theme["primary"])
            r_txt = p_s.add_run()
            r_txt.text = summary
            apply_font_to_run(r_txt, font_name=FONT_NAME, size=12, color=self.theme["text_dark"])
        return slide

    # --------------------------------------------------------------------------
    # 5. Archetype: stack (四层技术/业务分层架构全景)
    # --------------------------------------------------------------------------
    def add_stack_slide(self, title: str, layers: List[Dict[str, Any]]):
        slide = self.prs.slides.add_slide(self.layout_content)
        self._set_slide_title(slide, title)
        
        n = min(4, len(layers))
        layer_h = Inches(1.05)
        layer_gap = Inches(0.2)
        start_y = Inches(1.7)
        left_w = Inches(2.6)
        right_w = Inches(9.2)
        
        for i, layer in enumerate(layers[:n]):
            y = start_y + i * (layer_h + layer_gap)
            
            # Left layer banner
            left_card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.66), y, left_w, layer_h)
            apply_card_style(left_card, bg_color=self.theme["primary"], border_color=self.theme["primary"])
            p_l = left_card.text_frame.paragraphs[0]
            p_l.alignment = PP_ALIGN.CENTER
            r_l = p_l.add_run()
            r_l.text = layer.get("name", f"第 {n - i} 层")
            apply_font_to_run(r_l, font_name=FONT_NAME, size=13, bold=True, color=RGBColor(0xFF, 0xFF, 0xFF))
            
            # Right component container
            right_card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(3.46), y, right_w, layer_h)
            apply_card_style(right_card, border_color=self.theme["border_light"])
            
            # Inside pills
            items = layer.get("items", [])
            m = len(items)
            if m > 0:
                pill_gap = Inches(0.18)
                pill_w = (right_w - Inches(0.4) - pill_gap * (m - 1)) / m
                for j, item_text in enumerate(items):
                    px = Inches(3.66) + j * (pill_w + pill_gap)
                    py = y + Inches(0.25)
                    pill = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, px, py, pill_w, Inches(0.55))
                    apply_card_style(pill, bg_color=self.theme["pill_bg"], border_color=self.theme["pill_border"])
                    p_p = pill.text_frame.paragraphs[0]
                    p_p.alignment = PP_ALIGN.CENTER
                    r_p = p_p.add_run()
                    r_p.text = item_text
                    apply_font_to_run(r_p, font_name=FONT_NAME, size=11, bold=True, color=self.theme["primary"])
        return slide

    # --------------------------------------------------------------------------
    # 6. Archetype: split (左右非对称叙事: 40% 核心洞见 + 60% 落地动作)
    # --------------------------------------------------------------------------
    def add_split_slide(self, title: str, narrative: Dict[str, Any], initiatives: List[Dict[str, Any]]):
        slide = self.prs.slides.add_slide(self.layout_content)
        self._set_slide_title(slide, title)
        
        card_y = Inches(1.8)
        card_h = Inches(4.75)
        
        # Left Narrative Card (40%)
        left_w = Inches(4.6)
        card_l = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.66), card_y, left_w, card_h)
        apply_card_style(card_l, bg_color=self.theme["pill_bg"], border_color=self.theme["pill_border"])
        
        tb_l = slide.shapes.add_textbox(Inches(0.96), card_y + Inches(0.4), left_w - Inches(0.6), card_h - Inches(0.8))
        tf_l = tb_l.text_frame
        tf_l.word_wrap = True
        
        p_tag = tf_l.paragraphs[0]
        r_tag = p_tag.add_run()
        r_tag.text = narrative.get("tag", "STRATEGIC FOCUS")
        apply_font_to_run(r_tag, font_name=FONT_NAME, size=11, bold=True, color=self.theme["primary"])
        p_tag.space_after = Pt(12)
        
        p_head = tf_l.add_paragraph()
        r_head = p_head.add_run()
        r_head.text = narrative.get("headline", "")
        apply_font_to_run(r_head, font_name=FONT_NAME, size=20, bold=True, color=self.theme["text_dark"])
        p_head.space_after = Pt(14)
        
        p_body = tf_l.add_paragraph()
        r_body = p_body.add_run()
        r_body.text = narrative.get("desc", "")
        apply_font_to_run(r_body, font_name=FONT_NAME, size=12.5, color=self.theme["text_muted"])
        
        # Right Action Cards (60%)
        right_x = Inches(5.56)
        right_w = Inches(7.1)
        m = min(3, len(initiatives))
        row_h = (card_h - Inches(0.25) * (m - 1)) / m
        
        for k, init in enumerate(initiatives[:m]):
            ry = card_y + k * (row_h + Inches(0.25))
            rcard = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, right_x, ry, right_w, row_h)
            apply_card_style(rcard, border_color=self.theme["border_light"])
            
            # Number circle
            create_number_badge(slide, right_x + Inches(0.25), ry + Inches(0.2), f"{k+1:02d}", font_size=20,
                                primary_color=self.theme["primary"], accent_color=self.theme["accent"])
            
            tb_rc = slide.shapes.add_textbox(right_x + Inches(1.0), ry + Inches(0.18), right_w - Inches(1.2), row_h - Inches(0.36))
            tf_rc = tb_rc.text_frame
            tf_rc.word_wrap = True
            
            p_rt = tf_rc.paragraphs[0]
            r_rt = p_rt.add_run()
            r_rt.text = init.get("title", "")
            apply_font_to_run(r_rt, font_name=FONT_NAME, size=15, bold=True, color=self.theme["text_dark"])
            
            desc_rc = init.get("desc", "")
            if desc_rc:
                p_rd = tf_rc.add_paragraph()
                p_rd.space_before = Pt(4)
                r_rd = p_rd.add_run()
                r_rd.text = desc_rc
                apply_font_to_run(r_rd, font_name=FONT_NAME, size=11.5, color=self.theme["text_muted"])
        return slide

    # --------------------------------------------------------------------------
    # 7. Archetype: timeline (时间轴里程碑与演进路线)
    # --------------------------------------------------------------------------
    def add_timeline_slide(self, title: str, milestones: List[Dict[str, Any]]):
        slide = self.prs.slides.add_slide(self.layout_content)
        self._set_slide_title(slide, title)
        
        n = max(3, min(4, len(milestones)))
        total_w = Inches(12.0)
        gap = Inches(0.4)
        col_w = (total_w - gap * (n - 1)) / n
        start_x = Inches(0.66)
        axis_y = Inches(2.9)
        
        # Horizontal Connecting Line
        line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.9), axis_y, Inches(11.5), Inches(0.04))
        line.fill.solid()
        line.fill.fore_color.rgb = self.theme["primary"]
        line.line.fill.background()
        
        for i, m in enumerate(milestones[:n]):
            x = start_x + i * (col_w + gap)
            center_x = x + col_w / 2
            
            # Top Date / Phase Box (Above Axis)
            tb_d = slide.shapes.add_textbox(x, Inches(1.8), col_w, Inches(0.95))
            tf_d = tb_d.text_frame
            tf_d.word_wrap = True
            
            p_date = tf_d.paragraphs[0]
            p_date.alignment = PP_ALIGN.CENTER
            r_date = p_date.add_run()
            r_date.text = m.get("date", f"阶段 {i+1}")
            apply_font_to_run(r_date, font_name=FONT_NAME, size=18, bold=True, color=self.theme["primary"])
            
            p_goal = tf_d.add_paragraph()
            p_goal.alignment = PP_ALIGN.CENTER
            p_goal.space_before = Pt(3)
            r_goal = p_goal.add_run()
            r_goal.text = m.get("title", "")
            apply_font_to_run(r_goal, font_name=FONT_NAME, size=13, bold=True, color=self.theme["text_dark"])
            
            # Milestone Node Circle on Axis
            node = slide.shapes.add_shape(MSO_SHAPE.OVAL, center_x - Inches(0.18), axis_y - Inches(0.16), Inches(0.36), Inches(0.36))
            node.fill.solid()
            node.fill.fore_color.rgb = self.theme["primary"]
            node.line.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
            node.line.width = Pt(2.5)
            
            # Card Below Axis (y=3.3" to y=6.7", h=3.4")
            card_y = Inches(3.3)
            card_h = Inches(3.4)
            card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, card_y, col_w, card_h)
            apply_card_style(card, border_color=self.theme["border_light"])
            
            # Bullets inside Card
            tb_c = slide.shapes.add_textbox(x + Inches(0.2), card_y + Inches(0.25), col_w - Inches(0.4), card_h - Inches(0.8))
            tf_c = tb_c.text_frame
            tf_c.word_wrap = True
            
            for b_idx, bullet in enumerate(m.get("bullets", [])):
                p = tf_c.add_paragraph() if b_idx > 0 else tf_c.paragraphs[0]
                p.space_before = Pt(6)
                r_dot = p.add_run()
                r_dot.text = "✔ "
                apply_font_to_run(r_dot, font_name=FONT_NAME, size=10, bold=True, color=self.theme["primary"])
                r_txt = p.add_run()
                r_txt.text = bullet
                apply_font_to_run(r_txt, font_name=FONT_NAME, size=11, color=self.theme["text_dark"])
                
            # Bottom Status Tag
            status = m.get("status", "")
            if status:
                s_box = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x + Inches(0.2), card_y + card_h - Inches(0.52), col_w - Inches(0.4), Inches(0.34))
                apply_card_style(s_box, bg_color=self.theme["pill_bg"], border_color=self.theme["pill_border"])
                p_s = s_box.text_frame.paragraphs[0]
                p_s.alignment = PP_ALIGN.CENTER
                r_s = p_s.add_run()
                r_s.text = status
                apply_font_to_run(r_s, font_name=FONT_NAME, size=9.5, bold=True, color=self.theme["primary"])
        return slide

    # --------------------------------------------------------------------------
    # 8. Archetype: case (标杆案例与客户证言)
    # --------------------------------------------------------------------------
    def add_case_slide(self, title: str, quote: str, client: str, metrics: List[Dict[str, str]]):
        slide = self.prs.slides.add_slide(self.layout_content)
        self._set_slide_title(slide, title)
        
        # 1. Top Quote Box
        quote_card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.66), Inches(1.8), Inches(12.0), Inches(2.2))
        apply_card_style(quote_card, bg_color=self.theme["pill_bg"], border_color=self.theme["pill_border"])
        
        tb_q = slide.shapes.add_textbox(Inches(1.0), Inches(2.0), Inches(11.3), Inches(1.8))
        tf_q = tb_q.text_frame
        tf_q.word_wrap = True
        
        p_q = tf_q.paragraphs[0]
        r_q = p_q.add_run()
        r_q.text = f"“ {quote} ”"
        apply_font_to_run(r_q, font_name=FONT_NAME, size=17, bold=True, color=self.theme["text_dark"])
        p_q.space_after = Pt(10)
        
        p_c = tf_q.add_paragraph()
        r_c = p_c.add_run()
        r_c.text = f"— {client}"
        apply_font_to_run(r_c, font_name=FONT_NAME, size=13, color=self.theme["primary"], bold=True)
        
        # 2. Bottom 3 Metric Cards
        n = min(3, len(metrics))
        mw = (Inches(12.0) - Inches(0.4) * (n - 1)) / n
        my = Inches(4.3)
        mh = Inches(2.2)
        
        for idx, m in enumerate(metrics[:n]):
            mx = Inches(0.66) + idx * (mw + Inches(0.4))
            mcard = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, mx, my, mw, mh)
            apply_card_style(mcard, border_color=self.theme["border_light"])
            
            tb_m = slide.shapes.add_textbox(mx + Inches(0.2), my + Inches(0.25), mw - Inches(0.4), mh - Inches(0.5))
            tf_m = tb_m.text_frame
            tf_m.word_wrap = True
            
            p_mv = tf_m.paragraphs[0]
            p_mv.alignment = PP_ALIGN.CENTER
            r_mv = p_mv.add_run()
            r_mv.text = m.get("value", "")
            apply_font_to_run(r_mv, font_name=FONT_NAME, size=34, bold=True, color=self.theme["primary"])
            
            p_ml = tf_m.add_paragraph()
            p_ml.alignment = PP_ALIGN.CENTER
            p_ml.space_before = Pt(6)
            r_ml = p_ml.add_run()
            r_ml.text = m.get("label", "")
            apply_font_to_run(r_ml, font_name=FONT_NAME, size=13, bold=True, color=self.theme["text_dark"])
        return slide

    def add_closing(self):
        slide = self.prs.slides.add_slide(self.layout_closing)
        return slide

    def save(self, output_path: str):
        for slide in self.prs.slides:
            for shape in slide.shapes:
                if shape.has_text_frame:
                    for paragraph in shape.text_frame.paragraphs:
                        for run in paragraph.runs:
                            apply_font_to_run(run, font_name=FONT_NAME)
        self.prs.save(output_path)
        print(f"Presentation saved successfully to: {output_path}")

# ==============================================================================
# JSON Driver
# ==============================================================================
def build_deck_from_json(json_path: str, output_path: str, theme: str = "hosea"):
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    theme_choice = data.get("theme", theme)
    builder = HoseaDeckBuilder(theme_key=theme_choice)
    
    # 1. Cover
    cover_data = data.get("cover", {})
    cover_slide = builder.add_cover(
        title=cover_data.get("title", "合思企业解决方案"),
        subtitle=cover_data.get("subtitle", "让有限更有效"),
        copyright_text=cover_data.get("copyright", "© 2026 合思信息 版权所有")
    )
    cover_notes = cover_data.get("notes", "")
    if cover_notes and hasattr(cover_slide, "notes_slide"):
        try:
            tf_cn = cover_slide.notes_slide.notes_text_frame
            tf_cn.text = cover_notes
            for p in tf_cn.paragraphs:
                for r in p.runs:
                    apply_font_to_run(r, font_name=FONT_NAME, size=11, color=RGBColor(0x33, 0x33, 0x33))
        except Exception:
            pass

    # 2. Agenda
    agenda_items = data.get("agenda", [])
    if agenda_items:
        builder.add_agenda(agenda_items)
        
    # 3. Slides (Dispatches to the 8 Archetypes)
    for slide_data in data.get("slides", []):
        stype = slide_data.get("type", "cards")
        title = slide_data.get("title", "")
        slide = None
        
        if stype == "transition":
            slide = builder.add_transition(slide_data.get("number", "01"), title)
        elif stype == "cards":
            slide = builder.add_cards_slide(title, slide_data.get("cards", []))
        elif stype == "compare":
            slide = builder.add_compare_slide(title, slide_data.get("before", {}), slide_data.get("after", {}))
        elif stype == "process":
            slide = builder.add_process_slide(title, slide_data.get("steps", []))
        elif stype == "kpi":
            slide = builder.add_kpi_slide(title, slide_data.get("metrics", []), slide_data.get("summary", ""))
        elif stype == "stack":
            slide = builder.add_stack_slide(title, slide_data.get("layers", []))
        elif stype == "split":
            slide = builder.add_split_slide(title, slide_data.get("narrative", {}), slide_data.get("initiatives", []))
        elif stype == "timeline":
            slide = builder.add_timeline_slide(title, slide_data.get("milestones", []))
        elif stype == "case":
            slide = builder.add_case_slide(title, slide_data.get("quote", ""), slide_data.get("client", ""), slide_data.get("metrics", []))
            
        # Speaker Notes Support (Inspired by ppt-master)
        notes = slide_data.get("notes", "")
        if slide and notes and hasattr(slide, "notes_slide"):
            try:
                tf_n = slide.notes_slide.notes_text_frame
                tf_n.text = notes
                for p in tf_n.paragraphs:
                    for r in p.runs:
                        apply_font_to_run(r, font_name=FONT_NAME, size=11, color=RGBColor(0x33, 0x33, 0x33))
            except Exception:
                pass
            
    # 4. Closing
    if data.get("include_closing", True):
        builder.add_closing()
        
    builder.save(output_path)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Hosea & Universal Executive PPT Generator")
    parser.add_argument("--input", "-i", type=str, help="Path to input JSON outline")
    parser.add_argument("--output", "-o", type=str, default="演示文稿.pptx", help="Path to output PPTX")
    parser.add_argument("--theme", "-t", type=str, default="hosea", choices=list(THEMES.keys()), help="Theme palette")
    args = parser.parse_args()
    
    if args.input:
        build_deck_from_json(args.input, args.output, theme=args.theme)
    else:
        print("PPT Generator ready. Usage: python build_deck.py --input <outline.json> --output <deck.pptx> [--theme hosea|midnight|emerald|purple]")
