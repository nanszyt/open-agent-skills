// 从合思关联合同字段提取合同 ID 并以英文逗号拼接（纯 ES6 兼容写法）
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

const dataList = toArray(json);
const idList = [];
const seen = {};

dataList.forEach(item => {
  const fieldVal = safeGet(item, ["dataLinkForm", "E_demo_entity_src_001_关联合同"], null);
  if (!fieldVal) return;

  const entries = Array.isArray(fieldVal) ? fieldVal : [fieldVal];
  entries.forEach(entry => {
    if (!entry) return;
    let relateId = "";
    // 场景1：字符串 ID 老结构
    if (typeof entry === "string" && entry.trim()) {
      relateId = entry.trim();
    }
    // 场景2：新版完整对象（data.dataLink.id）及简化对象兜底
    else if (typeof entry === "object") {
      relateId =
        safeGet(entry, ["data", "dataLink", "id"], "") ||
        safeGet(entry, ["dataLink", "id"], "") ||
        safeGet(entry, ["id"], "");
      if (typeof relateId === "string") {
        relateId = relateId.trim();
      }
    }

    if (relateId && !seen[relateId]) {
      seen[relateId] = true;
      idList.push(relateId);
    }
  });
});

return {
  zht: idList.join(",")
};
