<script setup>
import { ref, onMounted, nextTick } from 'vue'
import * as api from '@/api'
import { formatDate, todayStr } from '@/utils/format'

const followupRecords = ref([])
const goals = ref({ weight: '56', glucose: '7.8' })
const editingId = ref(null)
const today = todayStr()

const form = ref({ date: today, weight: '', waist: '', hba1c: '', note: '' })
const goalForm = ref({ weight: '56', glucose: '7.8' })
const showGoalEdit = ref(false)

let wtChart = null, hba1cChart = null

const isDark = () => document.body.classList.contains('dark')

const weightData = () => followupRecords.value.filter(r => r.weight && parseFloat(r.weight) > 0).sort((a, b) => a.date.localeCompare(b.date))
const hba1cData = () => followupRecords.value.filter(r => r.hba1c && parseFloat(r.hba1c) > 0).sort((a, b) => a.date.localeCompare(b.date))

function renderCharts() {
  // 体重图
  const wDom = document.getElementById('wtChart')
  if (wDom && wDom.offsetParent !== null) {
    if (!wtChart) wtChart = echarts.init(wDom)
    const pts = weightData().map(r => [r.date, parseFloat(r.weight)])
    const wTarget = parseFloat(goals.value.weight) || 56
    wtChart.setOption({
      backgroundColor: isDark() ? '#1e252e' : '#fff',
      tooltip: { trigger: 'axis', formatter: p => p[0].axisValue + '<br/>体重: <b>' + p[0].value[1] + '</b> kg' },
      grid: { left: 50, right: 20, top: 12, bottom: 30 },
      xAxis: { type: 'category', boundaryGap: false, axisLabel: { fontSize: 10, color: isDark() ? '#8b9eb0' : '#718096' } },
      yAxis: { type: 'value', name: 'kg', axisLabel: { fontSize: 10, color: isDark() ? '#8b9eb0' : '#718096' }, splitLine: { lineStyle: { color: isDark() ? '#313d4a' : '#e2e8f0' } } },
      series: [{ name: '体重', type: 'line', data: pts, symbol: 'circle', symbolSize: 7, smooth: true, areaStyle: { opacity: 0.1 }, lineStyle: { width: 2.5, color: '#3182ce' }, itemStyle: { color: '#3182ce' }, markLine: { silent: true, symbol: 'none', data: [{ yAxis: wTarget, label: { formatter: '目标 ' + wTarget + 'kg' }, lineStyle: { color: '#e53e3e', type: 'dashed' } }] } }]
    }, true)
  }
  // HbA1c 图
  const hDom = document.getElementById('hbChart')
  if (hDom && hDom.offsetParent !== null) {
    if (!hba1cChart) hba1cChart = echarts.init(hDom)
    const hbPts = hba1cData().map(r => [r.date, parseFloat(r.hba1c)])
    hba1cChart.setOption({
      backgroundColor: isDark() ? '#1e252e' : '#fff',
      tooltip: { trigger: 'axis', formatter: p => p[0].axisValue + '<br/>HbA1c: <b>' + p[0].value[1] + '</b>%' },
      grid: { left: 50, right: 20, top: 12, bottom: 30 },
      xAxis: { type: 'category', boundaryGap: false, axisLabel: { fontSize: 10, color: isDark() ? '#8b9eb0' : '#718096' } },
      yAxis: { type: 'value', name: '%', min: 4, axisLabel: { fontSize: 10, color: isDark() ? '#8b9eb0' : '#718096' }, splitLine: { lineStyle: { color: isDark() ? '#313d4a' : '#e2e8f0' } } },
      series: [{ name: 'HbA1c', type: 'line', data: hbPts, symbol: 'diamond', symbolSize: 8, smooth: true, areaStyle: { opacity: 0.12 }, lineStyle: { width: 2.5, color: '#805ad5' }, itemStyle: { color: '#805ad5' }, markLine: { silent: true, symbol: 'none', data: [{ yAxis: 7.0, label: { formatter: '控制目标 7.0%' }, lineStyle: { color: '#e53e3e', type: 'dashed' } }] } }]
    }, true)
  }
}

async function loadData() {
  followupRecords.value = await api.listFollowup()
  try { goals.value = await api.getGoals() } catch {}
  goalForm.value = { ...goals.value }
  await nextTick()
  setTimeout(renderCharts, 50)
}

async function submitForm() {
  if (editingId.value) await api.updateFollowup(editingId.value, form.value)
  else await api.addFollowup(form.value)
  cancelEdit()
  await loadData()
}

function startEdit(r) {
  editingId.value = r.id
  form.value = { date: r.date, weight: String(r.weight || ''), waist: String(r.waist || ''), hba1c: String(r.hba1c || ''), note: r.note || '' }
}

function cancelEdit() { editingId.value = null; form.value = { date: today, weight: '', waist: '', hba1c: '', note: '' } }

async function deleteRecord(id) { if (!confirm('确定删除？')) return; await api.deleteFollowup(id); await loadData() }

async function saveGoals() { await api.updateGoals(goalForm.value); goals.value = { ...goalForm.value }; showGoalEdit.value = false }

async function copyLast() {
  if (!followupRecords.value.length) { alert('暂无记录可复制'); return }
  const last = followupRecords.value[0]
  form.value = { date: today, weight: String(last.weight || ''), waist: String(last.waist || ''), hba1c: String(last.hba1c || ''), note: '' }
}

onMounted(loadData)
</script>

<template>
  <div v-if="editingId" class="edit-bar">📝 正在编辑 #{{ editingId }} <button class="btn btn-sm" @click="cancelEdit">取消</button></div>

  <!-- 目标卡 -->
  <div class="card">
    <div style="display:flex; justify-content:space-between; align-items:center;">
      <h2 style="margin:0;">🎯 控制目标</h2>
      <button class="btn btn-sm" @click="showGoalEdit=!showGoalEdit">{{ showGoalEdit ? '取消' : '编辑目标' }}</button>
    </div>
    <div class="stats-grid" style="margin-top:10px;">
      <div style="background:var(--primary-light); border-radius:8px; padding:10px; text-align:center;">
        <div style="font-size:0.72rem; color:var(--text-light);">体重目标</div>
        <div style="font-size:1.3rem; font-weight:700;">{{ goals.weight }} kg</div>
      </div>
      <div style="background:var(--primary-light); border-radius:8px; padding:10px; text-align:center;">
        <div style="font-size:0.72rem; color:var(--text-light);">血糖目标</div>
        <div style="font-size:1.3rem; font-weight:700;">&lt; {{ goals.glucose }} mmol/L</div>
      </div>
    </div>
    <div v-if="showGoalEdit" style="display:flex; gap:10px; margin-top:10px;">
      <input type="number" v-model="goalForm.weight" placeholder="体重目标" step="0.1" style="flex:1; padding:8px; border:1px solid var(--border); border-radius:6px;">
      <input type="number" v-model="goalForm.glucose" placeholder="血糖目标" step="0.1" style="flex:1; padding:8px; border:1px solid var(--border); border-radius:6px;">
      <button class="btn btn-primary" @click="saveGoals">保存</button>
    </div>
  </div>

  <!-- 趋势图 -->
  <div class="card"><h2>📈 体重变化趋势</h2><div id="wtChart" style="width:100%; height:260px;"></div></div>
  <div class="card"><h2>📊 HbA1c 趋势</h2><div id="hbChart" style="width:100%; height:260px;"></div></div>

  <div class="dual-layout">
    <div class="dual-left">
      <div class="card">
        <h2>📝 添加随访记录</h2>
        <form @submit.prevent="submitForm">
          <div class="form-row">
            <div class="form-group"><label>日期</label><input type="date" v-model="form.date" required></div>
            <div class="form-group"><label>体重 (kg)</label><input type="number" v-model="form.weight" step="0.1"></div>
            <div class="form-group"><label>腰围 (cm)</label><input type="number" v-model="form.waist" step="0.1"></div>
            <div class="form-group"><label>HbA1c (%)</label><input type="number" v-model="form.hba1c" step="0.1" min="0" max="20"></div>
          </div>
          <div class="form-group"><label>备注</label><input type="text" v-model="form.note"></div>
          <div style="display:flex; gap:8px;">
            <button type="submit" class="btn btn-primary">{{ editingId ? '💾 更新' : '➕ 添加' }}</button>
            <button type="button" class="btn btn-sm" @click="copyLast">📋 复制上一条</button>
          </div>
        </form>
      </div>
    </div>
    <div class="dual-right">
      <div class="card">
        <h2>📋 随访记录</h2>
        <div class="table-wrap">
          <table><thead><tr><th>日期</th><th>体重</th><th>腰围</th><th>HbA1c</th><th>备注</th><th>操作</th></tr></thead>
          <tbody>
            <tr v-for="r in followupRecords" :key="r.id">
              <td>{{ formatDate(r.date) }}</td><td>{{ r.weight || '—' }}</td><td>{{ r.waist || '—' }}</td><td>{{ r.hba1c || '—' }}</td><td>{{ r.note || '—' }}</td>
              <td><button class="btn btn-sm" @click="startEdit(r)">编辑</button> <button class="btn btn-sm" style="background:var(--danger);color:white" @click="deleteRecord(r.id)">删</button></td>
            </tr>
            <tr v-if="!followupRecords.length"><td colspan="6" class="empty-state">暂无记录</td></tr>
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
.form-group input { width: 100%; padding: 10px; border: 1px solid var(--border); border-radius: 8px; background: var(--input-bg); color: var(--text); font-size: 0.9rem; box-sizing: border-box; }
.table-wrap { overflow-x: auto; }
table { width: 100%; border-collapse: collapse; font-size: 0.85rem; }
th, td { padding: 8px 10px; text-align: left; border-bottom: 1px solid var(--border); white-space: nowrap; }
th { color: var(--text-light); font-weight: 600; }
</style>
