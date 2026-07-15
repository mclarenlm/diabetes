<script setup>
import { ref, computed, onMounted, watch, nextTick } from 'vue'
import * as api from '@/api'
import { formatDate, glucoseBadge, todayStr } from '@/utils/format'

const records = ref([])
const editingId = ref(null)
const today = todayStr()

// 表单
const form = ref({ date: today, time: '', type: '', value: '', note: '' })

// 图表
const chartFilter = ref('全部')
const chartRange = ref('30')
let chartInstance = null

const isDark = computed(() => document.body.classList.contains('dark'))

const chartData = computed(() => {
  let d = [...records.value]
  if (chartFilter.value !== '全部') d = d.filter(r => r.type === chartFilter.value)
  if (chartRange.value !== 'all') {
    const cutoff = new Date()
    cutoff.setDate(cutoff.getDate() - parseInt(chartRange.value))
    d = d.filter(r => r.date >= cutoff.toISOString().split('T')[0])
  }
  return d.sort((a, b) => a.date.localeCompare(b.date) || (a.time||'').localeCompare(b.time||''))
})

function renderChart() {
  const dom = document.getElementById('gluChart')
  if (!dom || dom.offsetParent === null) return
  if (!chartInstance) chartInstance = echarts.init(dom)
  const data = chartData.value
  const types = ['空腹', '餐后1h', '餐后2h', '睡前', '运动前', '运动后', '随机']
  const colors = ['#3182ce', '#e53e3e', '#dd6b20', '#805ad5', '#38a169', '#d69e2e', '#718096']
  const markers = ['circle', 'diamond', 'rect', 'triangle', 'arrow', 'pin', 'roundRect']
  const series = []

  if (chartFilter.value === '全部') {
    types.forEach((tp, idx) => {
      const pts = data.filter(r => r.type === tp).map(r => [r.date + (r.time ? ' ' + r.time : ''), parseFloat(r.value)])
      if (pts.length) series.push({ name: tp, type: 'line', data: pts, symbol: markers[idx], symbolSize: 6, lineStyle: { width: 1.5 }, itemStyle: { color: colors[idx] } })
    })
  } else {
    const pts = data.map(r => [r.date + (r.time ? ' ' + r.time : ''), parseFloat(r.value)])
    if (pts.length) series.push({
      name: chartFilter.value, type: 'line', data: pts, symbol: 'circle', symbolSize: 7, smooth: true,
      areaStyle: { opacity: 0.08 }, lineStyle: { width: 2.5, color: '#3182ce' }, itemStyle: { color: '#3182ce' },
      markLine: { silent: true, data: [
        { yAxis: 7.8, label: { formatter: '餐后目标 7.8' }, lineStyle: { color: '#e53e3e', type: 'dashed' } },
        { yAxis: 5.6, label: { formatter: '空腹目标 5.6' }, lineStyle: { color: '#38a169', type: 'dashed' } }
      ]}
    })
  }

  chartInstance.setOption({
    backgroundColor: isDark.value ? '#1e252e' : '#fff',
    tooltip: { trigger: 'axis', formatter: ps => { let s = ps[0].axisValue + '<br/>'; ps.forEach(p => s += p.marker + ' ' + p.seriesName + ': <b>' + p.value[1] + '</b> mmol/L<br/>'); return s } },
    legend: { type: 'scroll', bottom: 0, textStyle: { fontSize: 11, color: isDark.value ? '#aaa' : '#666' } },
    grid: { left: 48, right: 16, top: 16, bottom: 36 },
    xAxis: { type: 'category', boundaryGap: false, axisLabel: { fontSize: 10, color: isDark.value ? '#8b9eb0' : '#718096', rotate: data.length > 20 ? 30 : 0 } },
    yAxis: { type: 'value', name: 'mmol/L', min: 2, axisLabel: { fontSize: 10, color: isDark.value ? '#8b9eb0' : '#718096' }, splitLine: { lineStyle: { color: isDark.value ? '#313d4a' : '#e2e8f0' } } },
    series: series.length ? series : [{ type: 'line', data: [] }],
    dataZoom: data.length > 30 ? [{ type: 'inside' }, { type: 'slider', bottom: 30, height: 16 }] : []
  }, true)
}

async function loadData() {
  records.value = await api.listGlucose()
  await nextTick()
  renderChart()
}

async function submitForm() {
  if (!form.value.type || !form.value.value) { alert('请填写类型和血糖值'); return }
  if (editingId.value) {
    await api.updateGlucose(editingId.value, form.value)
  } else {
    await api.addGlucose(form.value)
  }
  cancelEdit()
  await loadData()
}

function startEdit(r) {
  editingId.value = r.id
  form.value = { date: r.date, time: r.time || '', type: r.type, value: String(r.value), note: r.note || '' }
}

function cancelEdit() {
  editingId.value = null
  form.value = { date: today, time: '', type: '', value: '', note: '' }
}

async function deleteRecord(id) {
  if (!confirm('确定删除？')) return
  await api.deleteGlucose(id)
  await loadData()
}

async function copyLast() {
  if (!records.value.length) { alert('暂无记录可复制'); return }
  const last = records.value[0]
  form.value = { date: today, time: last.time || '', type: last.type, value: '', note: '' }
}

watch([chartFilter, chartRange], () => nextTick(renderChart))

onMounted(() => {
  form.value.time = new Date().toTimeString().slice(0, 5)
  loadData()
})
</script>

<template>
  <!-- 编辑提示 -->
  <div v-if="editingId" class="edit-bar">
    📝 正在编辑 #{{ editingId }}
    <button class="btn btn-sm" @click="cancelEdit">取消</button>
  </div>

  <!-- 趋势图 -->
  <div class="card">
    <h2>📈 血糖趋势</h2>
    <div style="display:flex; gap:8px; margin-bottom:10px;">
      <select v-model="chartFilter"><option>全部</option><option>空腹</option><option>餐后2h</option><option>餐后1h</option></select>
      <select v-model="chartRange"><option value="7">7天</option><option value="14">14天</option><option value="30">30天</option><option value="90">90天</option><option value="all">全部</option></select>
    </div>
    <div id="gluChart" style="width:100%; height:320px;"></div>
  </div>

  <div class="dual-layout">
    <div class="dual-left">
      <!-- 表单 -->
      <div class="card">
        <h2>📝 添加血糖记录</h2>
        <form @submit.prevent="submitForm">
          <div class="form-row">
            <div class="form-group"><label>日期</label><input type="date" v-model="form.date" required></div>
            <div class="form-group"><label>时间</label><input type="text" v-model="form.time" placeholder="如 07:30" pattern="\d{1,2}:\d{2}" required></div>
          </div>
          <div class="form-group"><label>测量类型</label>
            <select v-model="form.type" required>
              <option value="">请选择</option>
              <option value="空腹">空腹（目标 4.4-5.6）</option>
              <option value="餐后1h">餐后 1 小时（目标 <10.0）</option>
              <option value="餐后2h">餐后 2 小时（目标 <7.8）⭐</option>
              <option value="睡前">睡前（目标 5.6-7.0）</option>
              <option value="运动前">运动前（目标 >5.6）</option>
              <option value="运动后">运动后</option>
              <option value="随机">随机</option>
            </select>
          </div>
          <div class="form-group"><label>血糖值 (mmol/L)</label><input type="number" v-model="form.value" step="0.1" min="0" max="30" required></div>
          <div class="form-group"><label>备注</label><input type="text" v-model="form.note" placeholder="可选"></div>
          <div style="display:flex; gap:8px;">
            <button type="submit" class="btn btn-primary">{{ editingId ? '💾 更新' : '➕ 添加' }}</button>
            <button type="button" class="btn btn-sm" @click="copyLast">📋 复制上一条</button>
          </div>
        </form>
      </div>
    </div>
    <div class="dual-right">
      <!-- 列表 -->
      <div class="card">
        <h2>📋 血糖记录</h2>
        <div class="table-wrap">
          <table><thead><tr><th>日期</th><th>时间</th><th>类型</th><th>血糖</th><th>备注</th><th>操作</th></tr></thead>
          <tbody>
            <tr v-for="r in records" :key="r.id">
              <td>{{ formatDate(r.date) }}</td><td>{{ r.time }}</td><td>{{ r.type }}</td>
              <td :style="{ color: parseFloat(r.value) > 7.8 ? 'var(--danger)' : 'var(--success)' }">{{ r.value }}</td>
              <td>{{ r.note || '—' }}</td>
              <td><button class="btn btn-sm" @click="startEdit(r)">编辑</button> <button class="btn btn-sm" style="background:var(--danger);color:white" @click="deleteRecord(r.id)">删</button></td>
            </tr>
            <tr v-if="!records.length"><td colspan="6" class="empty-state">暂无记录</td></tr>
          </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.edit-bar { background: var(--warning); color: white; padding: 8px 16px; border-radius: 8px; margin-bottom: 12px; display: flex; justify-content: space-between; align-items: center; }
.dual-layout { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
@media (max-width: 1024px) { .dual-layout { grid-template-columns: 1fr; } }
.form-row { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 14px; margin-bottom: 12px; }
.form-group { margin-bottom: 10px; }
.form-group label { display: block; font-size: 0.82rem; color: var(--text-light); margin-bottom: 4px; }
.form-group input, .form-group select { width: 100%; padding: 10px; border: 1px solid var(--border); border-radius: 8px; background: var(--input-bg); color: var(--text); font-size: 0.9rem; box-sizing: border-box; }
.table-wrap { overflow-x: auto; }
table { width: 100%; border-collapse: collapse; font-size: 0.85rem; }
th, td { padding: 8px 10px; text-align: left; border-bottom: 1px solid var(--border); white-space: nowrap; }
th { color: var(--text-light); font-weight: 600; }
</style>
