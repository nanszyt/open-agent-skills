# 合思工作流 JS 节点常用代码模板 (ES6 安全版)

所有模板均严格遵循 **ES6 (ES2015)** 语法规范（不使用 `?.`、`??` 等 ES2020+ 特性，同时兼容“JS 节点（新）”与严格 ES6 沙盒），可直接复制到代码节点函数体中使用。

---

## 1. 安全路径取值 (`safeGet`)

替代 ES2020 可选链 `?.`，避免任何深层属性报 `Cannot read properties of undefined/null`：

```js
function safeGet(obj, path, defaultValue) {
  let curr = obj;
  for (let i = 0; i < path.length; i++) {
    if (curr === null || curr === undefined || typeof curr !== "object") {
      return defaultValue;
    }
    curr = curr[path[i]];
  }
  return curr === undefined || curr === null ? defaultValue : curr;
}
```

---

## 2. 数组入参标准化 (`toArray`)

兼容直接传入数组、JSON 字符串、或外层包裹 `{ data / list / records }`，并自动过滤 `null` / `undefined`：

```js
function toArray(raw) {
  let val = raw;
  if (typeof val === "string") {
    const trimmed = val.trim();
    if (!trimmed) return [];
    try {
      val = JSON.parse(trimmed);
    } catch (e) {
      return [];
    }
  }
  if (!Array.isArray(val) && val && typeof val === "object") {
    val = val.data || val.list || val.records || [];
  }
  if (!Array.isArray(val)) return [];
  return val.filter(item => item !== null && item !== undefined);
}
```

---

## 3. 从 `dataLinkForm` 关联字段提取 ID 列表（支持单选/多选/新老结构/去重）

```js
function extractLinkIds(val) {
  if (!val) return [];
  const list = Array.isArray(val) ? val : [val];
  const ids = [];

  list.forEach(entry => {
    if (!entry) return;
    let id = "";
    if (typeof entry === "string") {
      id = entry.trim();
    } else if (typeof entry === "object") {
      id =
        safeGet(entry, ["data", "dataLink", "id"], "") ||
        safeGet(entry, ["dataLink", "id"], "") ||
        safeGet(entry, ["id"], "");
      if (typeof id === "string") id = id.trim();
    }
    if (id) ids.push(id);
  });

  return ids;
}

function uniqueArray(arr) {
  const seen = {};
  const out = [];
  arr.forEach(item => {
    const key = String(item);
    if (!seen[key]) {
      seen[key] = true;
      out.push(item);
    }
  });
  return out;
}
```

---

## 4. 财务金额精确计算（转“分”整数运算，杜绝浮点误差）

### 4.1 金额解析与格式化

```js
// 兼容纯数字、数字字符串、合思金额对象 { standard: "501805.36" }
function parseMoneyToCents(raw) {
  let numVal = 0;
  if (raw && typeof raw === "object" && raw.standard !== undefined) {
    numVal = Number(raw.standard);
  } else {
    numVal = Number(raw);
  }
  if (!Number.isFinite(numVal)) return 0;
  return Math.round(numVal * 100);
}

function centsToYuanNumber(cents) {
  return Number((cents / 100).toFixed(2));
}
```

### 4.2 均摊尾差分配（两位精度，尾差均摊到前面各期）

```js
/**
 * 将 totalCents（分）拆分为 periods 期：
 * 每期精确到分，余数（尾差）从第 1 期起每期 +1 分（负金额按符号处理）。
 */
function splitCentsFrontTail(totalCents, periods) {
  if (!Number.isInteger(periods) || periods <= 0) return [];
  const sign = totalCents < 0 ? -1 : 1;
  const absTotal = Math.abs(totalCents);
  const base = Math.floor(absTotal / periods);
  const rem = absTotal % periods;

  const result = [];
  for (let i = 0; i < periods; i++) {
    const cents = (i < rem ? base + 1 : base) * sign;
    result.push({
      period: i + 1,
      cents,
      amount: centsToYuanNumber(cents)
    });
  }
  return result;
}
```

---

## 5. 北京时间 (UTC+8) 13 位时间戳年月与期数差计算

```js
function getYearMonthUTC8(timestampMs) {
  const ts = Number(timestampMs);
  if (!Number.isFinite(ts)) return null;
  const d = new Date(ts + 8 * 3600 * 1000);
  return {
    year: d.getUTCFullYear(),
    month: d.getUTCMonth() + 1
  };
}

/**
 * 计算 currentTs 相对 firstPeriodTs 处于第几期（首期为第 1 期）。
 * 若 currentTs 早于首期月份，返回 0。
 */
function calcCurrentPeriodIndex(currentTs, firstPeriodTs) {
  const cur = getYearMonthUTC8(currentTs);
  const first = getYearMonthUTC8(firstPeriodTs);
  if (!cur || !first) return 0;
  const diffMonths = (cur.year - first.year) * 12 + (cur.month - first.month);
  return diffMonths < 0 ? 0 : diffMonths + 1;
}
```
