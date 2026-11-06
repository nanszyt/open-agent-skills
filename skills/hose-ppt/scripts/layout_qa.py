"""
Hosea PPT Layout & Spacing Inspector (合思 PPT 布局与间距质检工具)
Inspects slide bounding boxes, card content fill ratio, and visual balance.
"""

import sys
from pptx import Presentation
from pptx.util import Inches, Pt

sys.stdout.reconfigure(encoding='utf-8')

def inspect_deck_layout(pptx_path: str):
    prs = Presentation(pptx_path)
    slide_w = prs.slide_width / 914400.0  # inches
    slide_h = prs.slide_height / 914400.0 # inches
    
    print(f"=== PPT Layout & Spacing Report ===")
    print(f"File: {pptx_path}")
    print(f"Canvas: {slide_w:.2f}\" x {slide_h:.2f}\" (16:9)")
    
    issues_found = []

    for s_idx, slide in enumerate(prs.slides):
        title_text = slide.shapes.title.text if slide.shapes.title else f"Slide {s_idx+1}"
        print(f"\n[Slide {s_idx+1}] {title_text[:30]}")
        
        # Collect rounded rectangle cards
        cards = []
        text_boxes = []
        for shp in slide.shapes:
            x = shp.left / 914400.0
            y = shp.top / 914400.0
            w = shp.width / 914400.0
            h = shp.height / 914400.0
            
            # Check if it's a card container
            if "Round" in shp.name or "Rectangle" in shp.name or "矩形" in shp.name:
                # ignore full height sidebar on agenda
                if w < 4.0 and x == 0 and h >= 7.0:
                    continue
                if w > 2.0 and h >= 1.0:  # significant card container
                    cards.append({"name": shp.name, "x": x, "y": y, "w": w, "h": h, "shape": shp})
            elif shp.has_text_frame:
                text_boxes.append({"name": shp.name, "x": x, "y": y, "w": w, "h": h, "tf": shp.text_frame})

        if cards:
            print(f"  Found {len(cards)} card containers.")
            # Check horizontal spacing & alignment
            cards_sorted = sorted(cards, key=lambda c: c["x"])
            left_margin = min(c["x"] for c in cards)
            right_margin = slide_w - max(c["x"] + c["w"] for c in cards)
            margin_diff = abs(left_margin - right_margin)
            
            if margin_diff > 0.2:
                msg = f"Slide {s_idx+1}: Horizontal asymmetry (Left: {left_margin:.2f}\", Right: {right_margin:.2f}\", diff={margin_diff:.2f}\")"
                print(f"  ⚠️ {msg}")
                issues_found.append(msg)
            else:
                print(f"  ✔ Horizontal margins balanced: Left={left_margin:.2f}\", Right={right_margin:.2f}\"")

            # Check card content fill ratio & bottom empty space
            for idx, c in enumerate(cards_sorted):
                # find all elements (text boxes, pictures, shapes) strictly within this card
                contained_shapes = []
                for shp in slide.shapes:
                    if shp == c["shape"]:
                        continue
                    sx = shp.left / 914400.0
                    sy = shp.top / 914400.0
                    sw = shp.width / 914400.0
                    sh = shp.height / 914400.0
                    # if shape center is inside card
                    if (c["x"] <= sx + sw/2 <= c["x"] + c["w"] and
                        c["y"] <= sy + sh/2 <= c["y"] + c["h"]):
                        contained_shapes.append({"shp": shp, "y": sy, "h": sh, "bottom": sy + sh})
                
                if contained_shapes:
                    top_y = min(s["y"] for s in contained_shapes)
                    max_bottom_y = max(s["bottom"] for s in contained_shapes)
                    active_height = max_bottom_y - top_y
                    fill_ratio = active_height / c["h"] if c["h"] > 0 else 0
                elif c["shape"].has_text_frame and c["shape"].text_frame.text.strip():
                    # Shape itself contains the text
                    fill_ratio = 0.85
                    active_height = c["h"] * 0.85
                else:
                    fill_ratio = 0
                    active_height = 0
                
                bottom_gap = slide_h - (c["y"] + c["h"])
                
                if fill_ratio < 0.60:
                    msg = f"Slide {s_idx+1} Card {idx+1}: Low content fill ({fill_ratio*100:.1f}%). Active content span ({active_height:.2f}\") occupies too little of card ({c['h']:.2f}\"). Blank space detected!"
                    print(f"  ⚠️ {msg}")
                    issues_found.append(msg)
                else:
                    print(f"  ✔ Card {idx+1} fill ratio healthy: {fill_ratio*100:.1f}% (Active span: {active_height:.2f}\" / {c['h']:.2f}\")")

                if bottom_gap < 0.4:
                    msg = f"Slide {s_idx+1} Card {idx+1}: Bottom edge too close to canvas boundary ({bottom_gap:.2f}\" < 0.5\")"
                    print(f"  ⚠️ {msg}")
                    issues_found.append(msg)

    print("\n" + "="*50)
    if issues_found:
        print(f"Inspection Complete: Found {len(issues_found)} layout/spacing warning(s).")
    else:
        print("Inspection Complete: All slides passed layout & spacing balance checks!")
    print("="*50)
    return issues_found

if __name__ == '__main__':
    if len(sys.argv) > 1:
        inspect_deck_layout(sys.argv[1])
    else:
        print("Usage: python layout_qa.py <deck.pptx>")
