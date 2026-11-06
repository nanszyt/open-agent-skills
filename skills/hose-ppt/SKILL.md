---
name: hose-ppt
description: "Use this skill whenever creating, editing, updating, or formatting presentations, pitch decks, client proposals, financial transformation solutions, or slide decks using the official Hosea (合思) corporate template style. Trigger whenever the user mentions '合思', '合思PPT', '合思模板', '做个合思风格的PPT', '制作合思方案', '合思汇报', 'hose-ppt', 'hose ppt', 'hosea', 'hosea deck', or asks to generate B2B financial SaaS presentations in this design system."
---

# 合思 (Hosea) 标准演示文稿制作技能

本 Skill 封装了合思官方标准母版资产、设计规范及全自动化 PPT 构建工作流。通过本 Skill，可一键生成具备合思官方高品质视觉（矢量 Logo、科技封底、全国研发中心与直营网络图、标志性蓝绿配饰与白底卡片流）的 PPT。

---

## 资产与工具索引

- **官方标准母版**：[template.pptx](./resources/template.pptx)（16:9 宽屏，内含封面、目录、篇章过渡、空白、标题与内容、官方封底共 6 套 Layout）
- **核心构建脚本**：[build_deck.py](./scripts/build_deck.py)（基于母版直接生成标准化演示文稿的 Python 引擎）
- **矢量图标与简笔画服务**：[icon_service.py](./scripts/icon_service.py)（企业级线性图标库、在线自动拉取、品牌色注入及高清栅格化）
- **布局与间距质检工具**：[layout_qa.py](./scripts/layout_qa.py)（检测卡片内容填充率、空白率、边距对称性及呼吸感）
- **视觉规范手册**：[design_system.md](./references/design_system.md)（色彩、字体、卡片、间距与组件参数）
- **输入范例结构**：[sample_outline.json](./resources/sample_outline.json)（开箱即用的多页结构数据模型）

---

## 视觉标准速查 (Design System Tokens)

- **画布尺寸**：16:9 宽屏（`13.33" × 7.50"` / `33.87cm × 19.05cm`）
- **主品牌色 (Primary Blue)**：`#2455FF`（用于大标题强调、卡片标志性数字、按钮、关键图标）
- **活力点缀色 (Accent Green)**：`#34DE4C`（用于标志性序号点 `01.`、绿色箭头、合规/增长状态）
- **深灰主文本 (Dark Slate)**：`#303B47`（用于内页标题、卡片主标题、一级正文）
- **辅助低调灰 (Muted Gray)**：`#718096`（用于次级说明、副标题、数据单位）
- **背景与卡片底色**：
  - 页面浅灰底：`#F7F7F7`
  - 浮层卡片白：`#FFFFFF`（圆角矩形，边框 `1pt #EAEEF5`）
- **统一标准字体**：**微软雅黑 (Microsoft YaHei)** 全局统一应用

---

## 标准制作工作流 (Standard Workflow)

当用户提出需要制作合思风格的 PPT（如“为某客户做一份合思费控报销解决方案”、“梳理合思产品规划汇报”等）时，严格遵循以下 4 步执行：

### 第 1 步：大纲结构化梳理 (Structure & Architecture)

将用户输入的需求、文档或方案整理为清晰的页面结构：
1. **封面 (Cover)**：主标题、副标题/Slogan（“未来财务用合思 · 让有限更有效”）、版权信息。
2. **目录 (Agenda)**：3 至 5 个核心章节。
3. **篇章过渡 (Transition)**：每个章节开始前的标志性转场页（`01.` + 章节名）。
4. **正文页 (Content Slides)**：
   - **痛点/方案页 (Cards Layout)**：2列、3列或4列白底卡片，每张卡片含标志性数字徽标（`01.`）、卡片主标、详细说明、核心要点清单。
   - **成效/指标页 (KPI Layout)**：3至4个巨型数字（44pt `#2455FF`），下配指标标签与说明，底部配备“💡 核心成效”大宽幅总结栏。
5. **官方封底 (Closing)**：自动附带官方封底（中国服务网点、400服务电话、官网、公众号二维码）。

---

### 第 2 步：选择构建方式 (Build Engine)

推荐使用已配置好的自动化构建脚本，稳定、零格式错位、完全符合母版：

#### 方式 A：编写 JSON 大纲并调用 `build_deck.py`（推荐首选）

1. 在当前任务目录下输出结构化 JSON 文件（参考 `sample_outline.json`）：
   ```json
   {
     "cover": {
       "title": "项目汇报标题",
       "subtitle": "副标题说明",
       "copyright": "© 2026 合思信息 版权所有"
     },
     "agenda": ["章节一名称", "章节二名称", "章节三名称"],
     "slides": [
       {
         "type": "transition",
         "number": "01",
         "title": "章节一名称"
       },
       {
         "type": "cards",
         "title": "页面核心标题",
         "cards": [
           {
             "num": "01",
             "title": "卡片标题",
             "desc": "卡片说明正文",
             "bullets": ["要点一", "要点二"]
           }
         ]
       },
       {
         "type": "kpi",
         "title": "核心成效与数据",
         "metrics": [
           { "value": "85%", "label": "指标名称", "desc": "指标细节说明" }
         ],
         "summary": "一句话成效总结"
       }
     ],
     "include_closing": true
   }
   ```
2. 运行构建脚本生成目标 PPT：
   ```bash
   python "C:\Users\朱益涛\.gemini\config\skills\hose-ppt\scripts\build_deck.py" --input outline.json --output "合思汇报方案.pptx"
   ```

#### 方式 B：直接用 Python / `python-pptx` 灵活扩充

如果需要构建复杂表格、对比柱状图、架构图等特殊页面：
1. 载入模板母版：
   ```python
   from pptx import Presentation
   prs = Presentation(r"C:\Users\朱益涛\.gemini\config\skills\hose-ppt\resources\template.pptx")
   # 使用 Layout 4 (标题与内容)
   slide = prs.slides.add_slide(prs.slide_layouts[4])
   ```
2. 设置标题与白底容器，使用规范定义的品牌色与字体。

---

### 第 3 步：运行布局与间距自动质检 (Layout & Spacing QA)

运行质检脚本检测卡片高度、空白率与边距对称性：
```bash
python "C:\Users\朱益涛\.gemini\config\skills\hose-ppt\scripts\layout_qa.py" "输出文稿.pptx"
```
质检重点指标：
- [ ] **卡片内容填充率 (Content Fill Ratio)**：内容跨度须占卡片高度的 **70%~90%**，杜绝卡片下半截过度留白。
- [ ] **间距对称性 (Margin Symmetry)**：左右边距差值不超过 0.2"，垂直方向居中呼吸感良好。
- [ ] **视觉锚点 (Visual Anchors)**：卡片顶部配备品牌色矢量图标徽章（48×48）与 `01.` 序号，底部配备胶囊场景标签（Tag Pill）。
- [ ] **字体一致性**：全篇 100% 统一为微软雅黑。
- [ ] **封底完整性**：封底必须展示合思官方服务网络与联系渠道。

---

## 示例触发场景

- **用户**：“帮我根据这篇客户访谈，做一个合思风格的费控立项方案 PPT”
  - **响应**：提取客户背景、核心痛点、合思敏捷费控解决方案、预期 ROI，生成合思母版标准 PPT。
- **用户**：“我需要一份向高管汇报的财务数字化月度成果 PPT”
  - **响应**：调用 KPI 模块与 3 卡片布局，突出核心成效大数字与业务亮点。
