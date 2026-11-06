---
name: hose-ppt
description: "Use this skill whenever creating, editing, updating, or formatting presentations, pitch decks, client proposals, financial transformation solutions, or slide decks. Dual-mode support: 1) Official Hosea (合思) corporate master template style, and 2) Universal high-end executive presentations based on the Anthropic PPTX design standard (8 slide archetypes, topic-informed palettes, strict avoid list). Trigger whenever the user mentions '合思', '合思PPT', '合思模板', '做个合思风格的PPT', '制作合思方案', '合思汇报', 'hose-ppt', 'hose ppt', 'hosea', 'hosea deck', or asks to create/refine professional B2B SaaS and executive presentation decks."
---

# 高端演示文稿与合思 (Hosea) 标准设计技能

本 Skill 深度融合**合思官方企业母版**与**全球顶级 AI 演示文稿设计规范（参考 Anthropic PPTX Standard 及业内顶流设计系统）**。兼顾合思官方品牌资产与通用高管汇报设计内容，彻底告别枯燥的纯文字列表与廉价的 AI 模板感。

---

## 🎨 顶级演示文稿核心设计原则 (Design Philosophy)

### 1. 绝不制作枯燥的幻灯片 (Don't Create Boring Slides)
- **每一页必须包含视觉锚点 (Visual Anchor)**：严禁全篇清一色的白底纯文字与 Bullet Points；每一页必须通过**矢量图标徽章**、**数据大字看板**、**横向流程流转**、**双栏现状方案对比**或**分层架构图**组织内容。
- **杜绝版式重复 (Layout Variety)**：整份文稿严禁连续出现同一种版式（如连续多页 3 列卡片）。必须根据叙事逻辑，在 8 大经典版式原型之间交替演进。
- **主次分明而非绝对均等 (Dominance Over Equality)**：主色占据 60%~70% 的核心视觉重量，1~2 个辅助色，1 个高对比度点睛色。

### 2. 严格的避坑清单与排版铁律 (The Strict Avoid List)
- ❌ **严禁在标题下方使用强调下划线 (NEVER use accent lines under titles)**：这是 AI 劣质幻灯片的典型标志，必须通过留白与层级建立秩序。
- ❌ **严禁添加无意义的装饰色彩条或边缘条 (NEVER add decorative color bars or stripes)**：如卡片单边彩线、四周随意彩条等，均属于低质 AI 填充物。
- ❌ **正文与列表严禁居中对齐 (Left-align body text)**：标题与数据大字可居中，正文、描述、清单项必须一律左对齐。
- ❌ **严禁文字溢出或卡片下半截过度留白**：严格遵循内容填充率黄金律（75%~90%），如果文字较少必须自适应收缩卡片并垂直居中。

### 3. 字号极差与排版层级 (Extreme Size Contrast)
- **封面主标**：`36 - 44 pt` Bold
- **内页主标**：`20 - 24 pt` Bold（统一居中或居左）
- **篇章过渡**：`44 - 48 pt` Bold（标志性 `01.`）
- **数据大字**：`46 - 60 pt` Bold（巨幅数字形成视觉锤）
- **卡片标题**：`16 - 18 pt` Bold
- **正文说明**：`12 - 14 pt` Regular
- **清单要点**：`11 - 12 pt` Regular（前缀 `✔ ` 或 `• `）
- **场景胶囊**：`9.5 - 10.5 pt` Bold
- **统一字体**：中文 100% 统一为 **微软雅黑 (Microsoft YaHei)**。

---

## 🏛️ 8 大高级版式原型库 (The 8 Slide Archetypes)

本技能的构建引擎已原生封装了 8 种最具表达力的高级版式，可直接在 JSON 大纲中通过 `type` 字段调用：

| 版式类型 (`type`) | 典型应用场景 | 核心视觉组件与结构 |
|---|---|---|
| **`cards`** | 核心支柱、核心能力、三大痛点、四大特性 | 2/3/4 列圆角白卡，顶部左侧 48×48 图标徽章 + 右侧 `01.` 序号，中部主标与摘要，下部 `✔ ` 清单，底部业务场景胶囊标签。 |
| **`compare`** | 现状痛点 vs 创新方案、Before vs After | 左右双栏鲜明对比卡（宽 5.6"），中间悬浮 `VS 升级` 胶囊；左侧浅红底 `⚠️ 传统痛点` 配 `✕ ` 列表，右侧浅蓝底 `✨ 敏捷方案` 配 `✔ ` 列表。 |
| **`process`** | 项目实施四步法、业务流转全景、演进路径 | 3~5 步横向流转卡片，顶部 `PHASE 01` 实色胶囊，卡片间带有 `➔` 绿色连接箭头，底部带有 `📦 交付物` 标签。 |
| **`kpi`** | 核心成效、业务看板、量化 ROI 亮点 | 3~4 个独立大数字看板（`46-60pt` 粗体），下方配指标名称与增长说明，底部配备全宽 `💡 核心成效` 综合总结栏。 |
| **`stack`** | 技术架构全景、业务分层全景、数智中台 | 4 层纵向堆叠架构：左侧实色层级标牌（如 `04. 智慧展现与决策层`），右侧白底卡片内平铺 4~5 个能力组件胶囊。 |
| **`split`** | 左右非对称叙事、战略洞见 + 落地动作 | 左侧 40% 宽度高对比度英雄卡（战略定位引言与核心洞见），右侧 60% 宽度 2~3 个横向落地的动作细分卡片。 |
| **`case`** | 标杆客户证言、权威背书、实践验证 | 顶部大型引用框（大双引号 `“ ”` + CFO/高管权威引言），底部 3 个量化收益微卡片（如 `月结关账提前 3 天`）。 |
| **`transition`** | 篇章章节过渡转场 | 极简微光卡片，居中巨幅 `01.` 标志性序号徽标 + 章节主标题。 |

---

## 🎨 双模式与精选主题调色盘 (Dual Mode & Themes)

通过 `--theme` 参数或 JSON 内 `"theme"` 字段自由切换：

1. **`hosea` (合思官方企业模式 · 默认首选)**：
   - 载入官方母版 `template.pptx`，带合思官方矢量 Logo 与中国服务网络封底；
   - 主色：`#2455FF`（电光科技蓝）+ 点睛：`#34DE4C`（荧光生机绿）+ 沉稳文本：`#303B47` + 浅底：`#F7F7F7`。
2. **`midnight` (午夜深蓝 · 高管述职与战略规划)**：
   - 主色：`#1E2761`（海军蓝）+ 点缀：`#4F9DDE`（冰蓝）+ 底色：`#F8FAFC`。
3. **`emerald` (翡翠生机 · ESG/供应链/绿色增长)**：
   - 主色：`#107C41`（深绿）+ 点缀：`#34D399`（薄荷绿）+ 底色：`#F9FAF8`。
4. **`purple` (前沿紫光 · AI大模型/算法前沿/数字创新)**：
   - 主色：`#6D28D9`（科技紫）+ 点缀：`#A78BFA`（浅紫）+ 底色：`#FAF5FF`。

---

## 🛠️ 工具链与全自动执行工作流

### 第 1 步：大纲结构化编写 (Outline Construction)
在当前工作区输出结构化 JSON 文件（例如 `outline.json`），合理组合 8 大版式：

```json
{
  "theme": "hosea",
  "cover": {
    "title": "新一代敏捷业财一体化方案",
    "subtitle": "重构企业支出管理 · 让有限更有效",
    "copyright": "© 2026 合思信息 版权所有"
  },
  "agenda": ["企业痛点与现状对比", "全场景方案与架构全景", "实施路径与客户成效"],
  "slides": [
    {
      "type": "transition",
      "number": "01",
      "title": "企业痛点与现状对比"
    },
    {
      "type": "compare",
      "title": "传统费控报销模式 vs 合思敏捷业财模式",
      "before": {
        "title": "传统模式 / 现存痛点 (Before)",
        "points": ["员工出差需频繁自行垫资，报销周期长达 14 天", "财务逐张人工验真贴票，月结关账超 5 天"]
      },
      "after": {
        "title": "合思敏捷新模式 (After)",
        "points": ["全场景因公消费对公结算，员工全流程免垫资免开票", "凭证全自动化率达 95% 以上，关账缩短至 24 小时"]
      }
    },
    {
      "type": "cards",
      "title": "合思敏捷费控核心能力三大支柱",
      "cards": [
        {
          "num": "01",
          "icon": "receipt",
          "title": "敏捷费控 · 全场景集采",
          "desc": "打通企业商旅、用餐与用车，集中对公结算。",
          "bullets": ["聚合主流商旅平台", "消费事前智能管控"],
          "tag": "应用场景 · 因公商旅与对公集采"
        }
      ]
    },
    {
      "type": "process",
      "title": "敏捷业财标准化实施四步法",
      "steps": [
        { "title": "调研与蓝图", "bullets": ["组织与科目梳理", "审批流确认"], "output": "蓝图规划方案" },
        { "title": "集成联调", "bullets": ["ERP 对接", "银企直联"], "output": "联调测试报告" }
      ]
    },
    {
      "type": "kpi",
      "title": "某大型制造龙头集团上线实测成效",
      "metrics": [
        { "value": "85%", "label": "报销周期缩短", "desc": "压缩至24小时内" },
        { "value": "95%+", "label": "凭证自动化率", "desc": "业务驱动自动入账" }
      ],
      "summary": "全面告别手工贴票报销时代，年均节约直接资金与协同工时成本数千万元。"
    }
  ],
  "include_closing": true
}
```

---

### 第 2 步：一键执行构建 (Generate Deck)
```bash
python "C:\Users\朱益涛\.gemini\config\skills\hose-ppt\scripts\build_deck.py" --input outline.json --output "合思汇报方案.pptx" --theme hosea
```

---

### 第 3 步：运行多维质量检验 (QA Verification)

1. **布局与间距自动质检**：
   ```bash
   python "C:\Users\朱益涛\.gemini\config\skills\hose-ppt\scripts\layout_qa.py" "合思汇报方案.pptx"
   ```
   - 验证卡片内容填充率（`75% ~ 90%`）；
   - 验证左右外边距水平对称性；
   - 验证无大面积空洞留白。
2. **高清多页视图质检**：
   ```bash
   python "C:\Users\朱益涛\.gemini\config\skills\hose-ppt\scripts\export_slides.py" "合思汇报方案.pptx" "slides_preview"
   ```
   - 通过 `read_file` 直接查看导出的单页 PNG，验证排版对齐、字体渲染与视觉质感。
