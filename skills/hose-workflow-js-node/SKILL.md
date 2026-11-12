---
name: hose-workflow-js-node
description: "Write, debug, validate, and test JavaScript code nodes for Hose (合思费控 / 易快报) workflows. Use whenever the user asks to write, fix, refactor, or debug Hose workflow JS node scripts (合思、合思费控、工作流代码节点、JS 节点、dataLinkForm、debug_json、关联合同、摊销计算, or Hose node input/output variable mappings), or needs to verify code.js locally before pasting into the cloud workflow."
---

# 合思费控工作流 JS 代码节点开发指南

本 Skill 用于规范**合思费控（Hose / 易快报）工作流 JS 代码节点**的业务脚本编写、数据结构解析、ES6 沙盒合规校验与本地仿真测试。

> **与 `hose-workflow-node-runtime` 的关系**：若项目中使用了 `hose-workflow-node-runtime`（Bun + TypeScript 本地调试脚手架 `runner/index.ts`、`*.node.ts`），二者可协同使用；本 Skill 自包含零依赖 Node.js 校验与运行脚本，专注规范**云端 `code.js` 业务代码写法、合思字段提取、金额/日期处理与 ES6 沙盒契约验证**。

---

## 资产与工具索引

- **数据结构速查**：[hose-data-structures.md](./references/hose-data-structures.md)（`dataLinkForm`、关联对象 `data.dataLink.id`、金额对象、维度引用、13 位时间戳）
- **ES6 安全代码模板**：[code-patterns.md](./references/code-patterns.md)（安全取值 `safeGet`、数组标准化、ID 提取去重、分单位金额拆分、UTC+8 期数计算）
- **需求对齐与提示词模板**：[prompt-template.md](./references/prompt-template.md)
- **静态合规校验脚本**：[check_node.mjs](./scripts/check_node.mjs)（检查函数体语法、禁止模块导出、顶层 `return`、严格 ES6 语法预警、入参变量名合法性）
- **本地沙盒仿真脚本**：[run_node.mjs](./scripts/run_node.mjs)（模拟合思 `__inj` 变量注入并验证返回对象契约）
- **可运行示例**：
  - 关联合同 ID 提取：[examples/contract-id-extract/](./examples/contract-id-extract/code.js)
  - 均摊分期与当期计算：[examples/amortization-schedule/](./examples/amortization-schedule/code.js)

---

## 标准执行工作流 (Standard Workflow)

### 第 1 步：对齐入参、出参与真实报文

在动手写代码前，先确认以下 4 项（缺项可参考 [prompt-template.md](./references/prompt-template.md) 向用户收集）：

1. **注入变量清单**：精确变量名、类型、示例值。
   - **关键核查**：合思会按 `const <varName> = __inj["<varName>"];` 注入变量。**禁止变量名包含空格、连字符或以数字开头**（例如 `u 首期时间` 含空格会导致语法错误，必须提醒用户改为 `u首期时间` 或 `firstPeriodTime`）。
2. **真实样本数据**：若有历史 `debug_json` 或表单报文，先逐层核对路径（对照 [hose-data-structures.md](./references/hose-data-structures.md)），切忌凭记忆猜测层级。
3. **沙盒语法目标**：默认按**纯 ES6 (ES2015)** 编写（最稳妥）；仅在用户明确仅用于支持 ES2020 的「JS 节点（新）」且无旧节点复用需求时，才考虑 `?.` / `??`。
4. **出参对象结构**：明确 `return { ... };` 必须返回的字段名和值类型。

---

### 第 2 步：按沙盒运行契约编写 `code.js`

合思工作流代码节点底层将代码包裹在如下函数体中执行：

```js
"use strict";
return (function(__inj) {
  const json = __inj["json"];
  // 你的代码节点逻辑写在这里
});
```

因此必须严格遵守以下 **6 条铁律**：

1. **只写函数体，禁止外层包装与模块化语法**：
   - ❌ 禁止写 `function main() { ... }` 包裹整个脚本（除非自己定义后立即调用）
   - ❌ 禁止写 `export`、`export default`、`module.exports`、`import`、`async` / `await`
   - ✅ 末尾必须有顶层 `return { key: value };`，且返回值必须是**普通 JS 对象（Map）**，不能返回数组、字符串或 `undefined`。
2. **优先纯 ES6 防御性取值**：
   - 优先使用 [code-patterns.md](./references/code-patterns.md) 中的 `safeGet(obj, ['data', 'dataLink', 'id'], '')` 或 `&&` 链式判空，避免老版本 ES6 沙盒不识别 `?.` / `??`。
3. **多态兼容关联对象与脏数据**：
   - 合思关联业务对象同时存在 `fieldVal.data.dataLink.id`（新版展开结构）、`fieldVal.dataLink.id`、`fieldVal.id`、纯字符串 ID 以及数组形态。
   - 遍历列表字段（如 `关联主合同`、`相对方名称`）时，必须过滤 `[null]` 或 `undefined` 元素，防止空指针异常。
4. **金额计算一律转“分”整数**：
   - 合思金额字段 `{ standard: "501805.36" }` 的 `standard` 是字符串。先解析为分（`Math.round(Number(val) * 100)`）完成加减乘除与尾差分配，最后再转回两位小数元。
5. **13 位时间戳按东八区 (UTC+8) 算年月**：
   - 使用 `new Date(ts + 8 * 3600 * 1000)` 配合 `getUTCFullYear()` / `getUTCMonth()`，防止服务器在 UTC 时区导致零点时间戳跨月偏移。
6. **不修改原始入参**：
   - 对注入的数组/对象只做读取与派生构造，不就地 `push` / `splice` / 改写原属性。

---

### 第 3 步：静态检查与本地沙盒验证

编写完成后，必须先在本机用零依赖 Node.js 工具链完成静检与试跑：

```bash
# 1. 静态语法、沙盒契约与严格 ES6 检查
node scripts/check_node.mjs <path/to/code.js> --strict-es6 --vars <path/to/vars.json>

# 2. 本地模拟合思 __inj 注入执行，并校验返回 Map 对象
node scripts/run_node.mjs --code <path/to/code.js> --vars <path/to/vars.json>
```

> 若目标项目同时使用了 `hose-workflow-node-runtime` 且系统已安装 `bun`，也可执行 `bun <scenario>/<scenario>.node.ts` 进行验证。

---

### 第 4 步：交付云端可用代码

向用户输出时：
1. 提供**可直接全选复制粘贴进合思 JS 代码节点**的完整代码块（不要夹带本地调试的 `defineNode`、`vars.json` 读取代码）。
2. 明确列出**入参变量要求**与**出参字段映射表**（例如 `zht` -> 逗号拼接的合同 ID 字符串）。
3. 若是从排障修复而来，简要说明原报文真实层级与改动点，以及本地仿真测试的实际输出结果。

---

## 质量验收清单 (QA Checklist)

- [ ] 无 `export` / `import` / `module.exports` / `async` / `await` / 外层多余函数包裹
- [ ] `check_node.mjs --strict-es6` 通过（若刻意使用 `?.` 需确认目标为新版节点）
- [ ] 所有注入变量名均为合法 JS 标识符（无空格、无连字符）
- [ ] 关联字段兼容 `data.dataLink.id`、`dataLink.id`、字符串与 `[null]` 数组兜底
- [ ] `run_node.mjs` 本地实跑通过，返回值确定为普通对象（非数组 / 非 `null`）且字段值符合预期
