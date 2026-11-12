// 费用均摊分期与当期摊销计算示例（纯 ES6 + 分单位整数运算 + UTC+8 时区校准）
function toCents(raw) {
  let numVal = 0;
  if (raw && typeof raw === "object" && raw.standard !== undefined) {
    numVal = Number(raw.standard);
  } else {
    numVal = Number(raw);
  }
  if (!Number.isFinite(numVal)) return 0;
  return Math.round(numVal * 100);
}

function toYuan(cents) {
  return Number((cents / 100).toFixed(2));
}

function getYearMonthUTC8(tsMs) {
  const ts = Number(tsMs);
  if (!Number.isFinite(ts)) return null;
  const d = new Date(ts + 8 * 3600 * 1000);
  return {
    year: d.getUTCFullYear(),
    month: d.getUTCMonth() + 1
  };
}

function calcPeriodIndex(curTs, firstTs) {
  const cur = getYearMonthUTC8(curTs);
  const first = getYearMonthUTC8(firstTs);
  if (!cur || !first) return 0;
  const diff = (cur.year - first.year) * 12 + (cur.month - first.month);
  return diff < 0 ? 0 : diff + 1;
}

const totalCents = toCents(totalAmount);
const unamortizedCents = toCents(unamortizedAmount);
const periods = Math.max(0, parseInt(totalPeriods, 10) || 0);

// 1. 生成每期分摊数组，除不尽的尾差平均向前面月份摊
const schedule = [];
if (periods > 0) {
  const sign = totalCents < 0 ? -1 : 1;
  const absTotal = Math.abs(totalCents);
  const base = Math.floor(absTotal / periods);
  const rem = absTotal % periods;

  for (let i = 0; i < periods; i++) {
    const cents = (i < rem ? base + 1 : base) * sign;
    schedule.push({
      period: i + 1,
      amount: toYuan(cents)
    });
  }
}

// 2. 历史摊销 = 应摊销金额 - 未摊销金额
const historyCents = totalCents - unamortizedCents;
const historyAmortization = {
  amount: toYuan(historyCents),
  remark: "历史的数据的单据，不发送到 NC"
};

// 3. 计算截至当前创建月份（含）应累计摊销金额，减去历史金额得到当期金额
const rawIndex = calcPeriodIndex(u创建时间, u首期时间);
const effectiveIndex = Math.min(rawIndex, schedule.length);
let cumulativeCents = 0;
for (let i = 0; i < effectiveIndex; i++) {
  cumulativeCents += Math.round(schedule[i].amount * 100);
}

const currentPeriodCents = cumulativeCents - historyCents;
const remainingUnamortizedCents = unamortizedCents - currentPeriodCents;

const output = {
  historyAmortization,
  currentPeriodAmount: toYuan(currentPeriodCents),
  remainingUnamortizedAmount: toYuan(remainingUnamortizedCents)
};

if (isLogInfo) {
  output.currentPeriodIndex = rawIndex;
  output.schedule = schedule;
}

return output;
