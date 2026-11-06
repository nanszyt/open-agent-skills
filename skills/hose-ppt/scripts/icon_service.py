"""
Hosea PPT Icon Service (合思 PPT 矢量图标与简笔画服务)
Provides enterprise vector icons, custom brand color styling, and high-res rasterization via PyMuPDF.
"""

import os
import sys
import re
import urllib.request
import urllib.parse
from typing import Optional, Tuple
import pymupdf

# Brand Colors
COLOR_BLUE  = "2455FF"   # #2455FF 电光科技蓝
COLOR_GREEN = "34DE4C"   # #34DE4C 荧光生机绿
COLOR_DARK  = "303B47"   # #303B47 沉稳深灰蓝
COLOR_CYAN  = "05C9E5"   # #05C9E5 浅青蓝

ICONS_CACHE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'resources', 'icons')
os.makedirs(ICONS_CACHE_DIR, exist_ok=True)

# Curated High-Frequency Enterprise SaaS & Finance Vector Icons (Lucide Clean Line-art)
BUILTIN_SVGS = {
    "receipt": '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 2v20l2-1 2 1 2-1 2 1 2-1 2 1 2-1 2 1V2l-2 1-2-1-2 1-2-1-2 1-2-1-2 1Z"/><path d="M16 8h-6a2 2 0 1 0 0 4h4a2 2 0 1 1 0 4H8"/><path d="M12 17.5v-11"/></svg>''',
    "credit-card": '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="20" height="14" x="2" y="5" rx="2"/><line x1="2" x2="22" y1="10" y2="10"/></svg>''',
    "wallet": '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M19 7V4a1 1 0 0 0-1-1H5a2 2 0 0 0 0 4h15a1 1 0 0 1 1 1v4h-3a2 2 0 0 0 0 4h3a1 1 0 0 0 1-1v-2a1 1 0 0 0-1-1"/><path d="M3 5v14a2 2 0 0 0 2 2h15a1 1 0 0 0 1-1v-4"/></svg>''',
    "file-text": '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7Z"/><path d="M14 2v4a2 2 0 0 0 2 2h4"/><path d="M10 9H8"/><path d="M16 13H8"/><path d="M16 17H8"/></svg>''',
    "bar-chart": '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="12" x2="12" y1="20" y2="10"/><line x1="18" x2="18" y1="20" y2="4"/><line x1="6" x2="6" y1="20" y2="16"/></svg>''',
    "pie-chart": '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21.21 15.89A10 10 0 1 1 8 2.83"/><path d="M22 12A10 10 0 0 0 12 2v10z"/></svg>''',
    "trending-up": '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="22 7 13.5 15.5 8.5 10.5 2 17"/><polyline points="16 7 22 7 22 13"/></svg>''',
    "shield-check": '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 13c0 5-3.5 7.5-7.66 8.95a1 1 0 0 1-.67-.01C7.5 20.5 4 18 4 13V6a1 1 0 0 1 1-1c2 0 4.5-1.2 6.24-2.72a1.17 1.17 0 0 1 1.52 0C14.51 3.81 17 5 19 5a1 1 0 0 1 1 1z"/><path d="m9 12 2 2 4-4"/></svg>''',
    "cpu": '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="16" height="16" x="4" y="4" rx="2"/><rect width="6" height="6" x="9" y="9" rx="1"/><path d="M15 2v2"/><path d="M15 20v2"/><path d="M2 15h2"/><path d="M2 9h2"/><path d="M20 15h2"/><path d="M20 9h2"/><path d="M9 2v2"/><path d="M9 20v2"/></svg>''',
    "zap": '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>''',
    "layers": '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m12.83 2.18a2 2 0 0 0-1.66 0L2.6 6.08a1 1 0 0 0 0 1.83l8.58 3.91a2 2 0 0 0 1.66 0l8.58-3.9a1 1 0 0 0 0-1.83Z"/><path d="m22 17.65-9.17 4.16a2 2 0 0 1-1.66 0L2 17.65"/><path d="m22 12.65-9.17 4.16a2 2 0 0 1-1.66 0L2 12.65"/></svg>''',
    "database": '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M3 5V19A9 3 0 0 0 21 19V5"/><path d="M3 12A9 3 0 0 0 21 12"/></svg>''',
    "users": '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>''',
    "check-circle": '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><path d="m9 11 3 3L22 4"/></svg>''',
    "clock": '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>''',
    "cloud": '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17.5 19H9a7 7 0 1 1 6.71-9h1.79a4.5 4.5 0 1 1 0 9Z"/></svg>''',
    "sparkles": '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m12 3-1.912 5.813a2 2 0 0 1-1.275 1.275L3 12l5.813 1.912a2 2 0 0 1 1.275 1.275L12 21l1.912-5.813a2 2 0 0 1 1.275-1.275L21 12l-5.813-1.912a2 2 0 0 1-1.275-1.275L12 3Z"/><path d="M5 3v4"/><path d="M19 17v4"/><path d="M3 5h4"/><path d="M17 19h4"/></svg>''',
    "alert-triangle": '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"/><line x1="12" x2="12" y1="9" y2="13"/><line x1="12" x2="12.01" y1="17" y2="17"/></svg>'''
}

def get_or_fetch_svg(icon_name: str, color_hex: str = COLOR_BLUE) -> str:
    """Returns SVG string for icon_name, styled with color_hex."""
    clean_name = icon_name.lower().strip()
    color_str = f"#{color_hex.lstrip('#')}"

    # 1. Built-in library match
    if clean_name in BUILTIN_SVGS:
        return BUILTIN_SVGS[clean_name].replace("{color}", color_str)
    
    # Keyword semantic mapping
    name_map = {
        "费控": "receipt", "报销": "wallet", "支付": "credit-card",
        "发票": "file-text", "凭证": "file-text", "看板": "bar-chart",
        "报表": "pie-chart", "合规": "shield-check", "风控": "shield-check",
        "智能": "cpu", "ai": "sparkles", "效率": "zap", "云": "cloud",
        "时间": "clock", "人员": "users", "团队": "users", "系统": "layers",
        "直联": "database", "痛点": "alert-triangle", "瓶颈": "alert-triangle"
    }
    for kw, target in name_map.items():
        if kw in clean_name:
            return BUILTIN_SVGS[target].replace("{color}", color_str)

    # 2. Online Fetch from Iconify API (Lucide collection)
    try:
        url = f"https://api.iconify.design/lucide/{clean_name}.svg?color={urllib.parse.quote(color_str)}"
        req = urllib.request.Request(url, headers={'User-Agent': 'HoseaPPT/1.0'})
        with urllib.request.urlopen(req, timeout=3) as resp:
            if resp.status == 200:
                return resp.read().decode('utf-8')
    except Exception:
        pass

    # Fallback default: receipt or spark
    return BUILTIN_SVGS["sparkles"].replace("{color}", color_str)

def generate_icon_badge(
    icon_name: str,
    color_hex: str = COLOR_BLUE,
    bg_style: str = "rounded_pill",  # "rounded_pill", "circle", "clean"
    size_px: int = 128
) -> str:
    """
    Renders a styled icon badge to a high-resolution transparent PNG.
    Returns the absolute path to the generated image file.
    """
    svg_raw = get_or_fetch_svg(icon_name, color_hex)
    
    # Extract inner elements of the SVG to compose a badge
    # Remove outer <svg ...> and </svg>
    inner_svg = re.sub(r'<\?xml[^>]*\?>', '', svg_raw)
    inner_svg = re.sub(r'<svg[^>]*>', '', inner_svg)
    inner_svg = inner_svg.replace('</svg>', '').strip()
    
    stroke_color = f"#{color_hex.lstrip('#')}"
    
    if bg_style == "rounded_pill":
        # Elegant 64x64 container with soft #F0F4FF fill and #D5E2FF subtle border
        composed_svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 64 64">
            <rect x="2" y="2" width="60" height="60" rx="16" fill="#F0F4FF" stroke="#D5E2FF" stroke-width="1.5"/>
            <g transform="translate(16, 16) scale(1.333)" fill="none" stroke="{stroke_color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                {inner_svg}
            </g>
        </svg>'''
    elif bg_style == "circle":
        composed_svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 64 64">
            <circle cx="32" cy="32" r="30" fill="#F0F4FF" stroke="#D5E2FF" stroke-width="1.5"/>
            <g transform="translate(16, 16) scale(1.333)" fill="none" stroke="{stroke_color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                {inner_svg}
            </g>
        </svg>'''
    else: # clean transparent
        composed_svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24">
            <g fill="none" stroke="{stroke_color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                {inner_svg}
            </g>
        </svg>'''
        
    out_filename = f"icon_{icon_name}_{color_hex}_{bg_style}_{size_px}.png"
    out_path = os.path.join(ICONS_CACHE_DIR, out_filename)
    
    if not os.path.exists(out_path):
        doc = pymupdf.open("svg", composed_svg.encode("utf-8"))
        page = doc[0]
        # render to desired pixel size
        zoom = size_px / 64.0
        mat = pymupdf.Matrix(zoom, zoom)
        pix = page.get_pixmap(matrix=mat, alpha=True)
        pix.save(out_path)
        
    return out_path

if __name__ == '__main__':
    print("Testing Icon Service...")
    path1 = generate_icon_badge("receipt", COLOR_BLUE, bg_style="rounded_pill")
    path2 = generate_icon_badge("cpu", COLOR_BLUE, bg_style="rounded_pill")
    path3 = generate_icon_badge("bar-chart", COLOR_BLUE, bg_style="rounded_pill")
    print(f"Generated: {path1}")
    print(f"Generated: {path2}")
    print(f"Generated: {path3}")
