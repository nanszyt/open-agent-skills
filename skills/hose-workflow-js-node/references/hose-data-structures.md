# 合思工作流 JS 节点常见数据结构速查

本文档记录在合思（Hose / 易快报）工作流节点调试报文与需求规范中验证过的典型数据形态（字段 ID 与业务名称均已脱敏为示例值），编写取数与清洗逻辑时请优先对照排查。

---

## 1. 关联业务对象 / 明细数据源 (`json` / `dataLinkForm`)

工作流传入的业务对象列表（例如通过变量 `json` 注入）通常为数组；外层若被序列化或包裹，需兼容 JSON 字符串。

### 典型条目结构

```json
[
  {
    "dataLinkId": "ID01DEMO_ROW_001",
    "dataLinkTemplateId": "ID01DEMO_TPL_001",
    "dataLinkForm": {
      "E_demo_entity_src_001_name": "示例单据或合同标题",
      "E_demo_entity_src_001_合同编号": "HT-2026-00001",
      "E_demo_entity_src_001_关联合同": {
        "data": {
          "plans": [],
          "ledger": {},
          "planned": {},
          "dataLink": {
            "id": "ID01DEMO_TARGET_001",
            "active": true,
            "entityId": "demo_entity_tgt_001",
            "E_demo_entity_tgt_001_code": "HT-2026-00001",
            "E_demo_entity_tgt_001_name": "示例主合同",
            "E_demo_entity_tgt_001_合同金额": {
              "standard": "100000.00",
              "standardUnit": "元",
              "standardScale": 2,
              "standardSymbol": "¥",
              "standardNumCode": "156",
              "standardStrCode": "CNY"
            }
          }
        },
        "path": {},
        "template": {}
      }
    }
  }
]
```

### 字段键名规律

- 业务对象字段通常遵循 `E_<entityId>_<字段名称>` 命名规则（例如 `E_demo_entity_src_001_关联合同`）。
- 关联对象展开后的内部属性会带有**目标实体的** `entityId` 前缀（例如外层实体为 `demo_entity_src_001`，内部 `dataLink` 实体变为 `demo_entity_tgt_001`）。

---

## 2. 关联引用字段的多种形态（高频踩坑点）

同一关联业务对象字段在不同节点、不同单据状态或版本下，可能出现以下 4 种取值结构，取 ID 时务必做多态兼容：

| 形态 | 典型结构 | 取值路径 | 备注 |
| :--- | :--- | :--- | :--- |
| **新版完整展开对象** | `{ data: { dataLink: { id: "ID01..." }, ledger: ..., planned: ... } }` | `fieldVal.data.dataLink.id` | 最常见漏层坑：容易误写成 `fieldVal.dataLink.id` |
| **中间简化对象** | `{ dataLink: { id: "ID01..." } }` 或 `{ id: "ID01..." }` | `fieldVal.dataLink.id` / `fieldVal.id` | 部分接口或精简配置返回 |
| **老版纯字符串 ID** | `"ID01DEMO_TARGET_001"` | `fieldVal.trim()` | 注意过滤空字符串 |
| **多选 / 列表关联** | `[ { data: { dataLink: { id: "..." } } } ]` 或 `[null]` | 遍历数组并**过滤 `null` / `undefined`** | 真实报文中常见 `[null]` 占位数组（如 `关联主合同: [null]`），直接读属性必报错 |

---

## 3. 常见基础字段类型

### 3.1 金额对象 (Money)

```json
{
  "standard": "100000.00",
  "standardUnit": "元",
  "standardScale": 2,
  "standardSymbol": "¥",
  "standardNumCode": "156",
  "standardStrCode": "CNY"
}
```

- **陷阱**：`standard` 字段是**字符串**（`"100000.00"`），不是 `number`；直接用 `+` 拼接会变成字符串连接。
- 必须通过 `Number(val.standard)` 转换后再参与数值或分单位整数计算。

### 3.2 维度 / 档案引用对象 (Dimension Ref)

```json
{
  "id": "ID01DEMO_DIM_001",
  "code": "1",
  "name": "付款",
  "active": true,
  "dimensionId": "ID01DEMO_CORP:资金流向"
}
```

- 常用取值字段为 `id`、`code`、`name`（例如判断“是否”档案：`name === "是"` 或 `code === "0"`）。

### 3.3 附件列表 (Attachment List)

```json
[
  {
    "id": "",
    "key": "demo-contract.pdf",
    "url": "https://example.com/demo-contract.pdf",
    "fileId": "ID01DEMO_FILE_001",
    "fileName": "demo-contract.pdf"
  }
]
```

### 3.4 日期字段 (13 位毫秒时间戳)

- 如 `1799078400000` 或规范中的 `u创建时间`、`u首期时间`。
- **时区陷阱**：合思业务日期多按 **北京时间（UTC+8）** 零点存储。若沙盒服务器运行在 UTC 时区，直接用 `new Date(ts).getMonth()` 会回退到前一天 16:00，导致跨月/跨日错位。计算年月/期数时应统一加 8 小时偏移并用 `getUTCFullYear()` / `getUTCMonth()` 提取（见 [code-patterns.md](./code-patterns.md)）。
