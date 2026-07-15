export function formatDate(d) {
  if (!d) return '-'
  const parts = d.split('-')
  return parts.length === 3 ? `${parseInt(parts[1])}/${parseInt(parts[2])}` : d
}

export function glucoseBadge(val, type) {
  const v = parseFloat(val)
  if (isNaN(v)) return ''
  const limits = {
    '空腹': [4.4, 5.6],
    '餐后1h': [0, 10],
    '餐后2h': [0, 7.8],
    '睡前': [5.6, 7.0],
    '运动前': [5.6, Infinity],
  }
  const [lo, hi] = limits[type] || [0, 7.8]
  if (v < lo) return '⚠️ 偏低'
  if (v > hi) return '🔴 偏高'
  return '✅ 正常'
}

export function todayStr() {
  return new Date().toISOString().split('T')[0]
}
