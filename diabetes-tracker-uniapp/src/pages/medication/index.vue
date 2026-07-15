<script setup>
import { ref, computed, onMounted } from 'vue'
import * as api from '@/api'
import { formatDate, todayStr } from '@/utils/format'

const records = ref([])
const customDrugs = ref([])
const editingId = ref(null)
const today = todayStr()
const form = ref({ date: today, timeDetail: '', name: '', dose: '', time: '晨起空腹', sideEffect: '无', note: '' })

const DRUG_DOSES = { '二甲双胍': '500mg', '阿卡波糖': '50mg', '格列美脲': '1mg', '胰岛素(短效)': '8U', '胰岛素(长效)': '12U' }

const allDrugs = computed(() => [...Object.keys(DRUG_DOSES), ...customDrugs.value.map(d => d.name)])

const summary = computed(() => {
  const byName = {}
  records.value.forEach(r => { byName[r.name] = (byName[r.name] || 0) + 1 })
  return Object.entries(byName).map(([name, count]) => ({ name, count }))
})

async function loadData() {
  records.value = await api.listMedication()
  customDrugs.value = await api.listCustomDrugs()
}

function quickAdd(name) {
  form.value.name = name
  form.value.dose = DRUG_DOSES[name] || (customDrugs.value.find(d => d.name === name) || {}).dose || ''
}

function onDrugChange() {
  form.value.dose = DRUG_DOSES[form.value.name] || (customDrugs.value.find(d => d.name === form.value.name) || {}).dose || ''
}

async function submitForm() {
  if (!form.value.name) { alert('请选择药品'); return }
  const data = { date: form.value.date, timeDetail: form.value.timeDetail, name: form.value.name, dose: form.value.dose, time: form.value.time, sideEffect: form.value.sideEffect, note: form.value.note }
  if (editingId.value) await api.updateMedication(editingId.value, data)
  else await api.addMedication(data)
  cancelEdit()
  await loadData()
}

function startEdit(r) {
  editingId.value = r.id
  form.value = { date: r.date, timeDetail: r.time_detail || '', name: r.name, dose: r.dose || '', time: r.time_period || '晨起空腹', sideEffect: r.side_effect || '无', note: r.note || '' }
}

function cancelEdit() {
  editingId.value = null
  form.value = { date: today, timeDetail: '', name: '', dose: '', time: '晨起空腹', sideEffect: '无', note: '' }
}

async function deleteRecord(id) {
  if (!confirm('确定删除？')) return
  await api.deleteMedication(id)
  await loadData()
}

async function copyLast() {
  if (!records.value.length) { alert('暂无记录可复制'); return }
  const last = records.value[0]
  form.value = { date: today, timeDetail: last.time_detail || '', name: last.name, dose: last.dose || '', time: last.time_period || '晨起空腹', sideEffect: '无', note: '' }
}

function exportCSV() {
  let csv = '日期,时间,药品,剂量,时机,不良反应,备注\n'
  records.value.forEach(r => {
    csv += `${r.date},${r.time_detail||''},${r.name},${r.dose||''},${r.time_period||''},${r.side_effect||''},${r.note||''}\n`
  })
  const blob = new Blob(['\ufeff' + csv], { type: 'text/csv' })
  const a = document.createElement('a')
  a.href = URL.createObjectURL(blob)
  a.download = `用药记录_${today}.csv`
  a.click()
}

onMounted(() => {
  form.value.timeDetail = new Date().toTimeString().slice(0, 5)
  loadData()
})
</script>

<template>
  <div v-if="editingId" class="edit-bar">📝 正在编辑 #{{ editingId }} <button class="btn btn-sm" @click="cancelEdit">取消</button></div>

  <!-- 快捷按钮 -->
  <div class="card">
    <h2>⚡ 快捷用药</h2>
    <div style="display:grid; grid-template-columns:repeat(auto-fit,minmax(160px,1fr)); gap:10px;">
      <button v-for="d in allDrugs" :key="d" class="quick-btn" @click="quickAdd(d)">{{ d }}</button>
    </div>
  </div>

  <div class="dual-layout">
    <div class="dual-left">
      <div class="card">
        <h2>📝 添加用药记录</h2>
        <form @submit.prevent="submitForm">
          <div class="form-row">
            <div class="form-group"><label>日期</label><input type="date" v-model="form.date" required></div>
            <div class="form-group"><label>时间</label><input type="text" v-model="form.timeDetail" placeholder="如 07:30"></div>
            <div class="form-group"><label>药品名称</label><select v-model="form.name" @change="onDrugChange" required><option value="">请选择</option><option v-for="d in allDrugs" :key="d" :value="d">{{ d }}</option></select></div>
            <div class="form-group"><label>剂量</label><input type="text" v-model="form.dose" placeholder="自动填充"></div>
          </div>
          <div class="form-row">
            <div class="form-group"><label>服用时机</label><select v-model="form.time"><option>晨起空腹</option><option>早餐随餐</option><option>午餐随餐</option><option>晚餐随餐</option><option>睡前</option></select></div>
            <div class="form-group"><label>不良反应</label><select v-model="form.sideEffect"><option>无</option><option>腹胀</option><option>腹泻</option><option>恶心</option><option>低血糖</option><option>其他</option></select></div>
            <div class="form-group"><label>备注</label><input type="text" v-model="form.note"></div>
          </div>
          <div style="display:flex; gap:8px;">
            <button type="submit" class="btn btn-primary">{{ editingId ? '💾 更新' : '➕ 添加' }}</button>
            <button type="button" class="btn btn-sm" @click="copyLast">📋 复制���一条</button>
          </div>
        </form>
      </div>
    </div>
    <div class="dual-right">
      <!-- 汇总 -->
      <div class="card">
        <h2>📊 用药汇总</h2>
        <div class="stats-grid">
          <div v-for="s in summary" :key="s.name" style="background:var(--primary-light); border-radius:8px; padding:10px;">
            <div style="font-size:0.78rem; color:var(--text-light);">{{ s.name }}</div>
            <div style="font-size:1.2rem; font-weight:700;">{{ s.count }} <span style="font-size:0.7rem">次</span></div>
          </div>
          <div v-if="!summary.length" class="empty-state">暂无数据</div>
        </div>
      </div>
      <!-- 列表 -->
      <div class="card">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
          <h2 style="margin:0;">📋 用药记录</h2>
          <button class="btn btn-sm" @click="exportCSV">📥 导出CSV</button>
        </div>
        <div class="table-wrap">
          <table><thead><tr><th>日期</th><th>时间</th><th>药品</th><th>剂量</th><th>时机</th><th>不良反应</th><th>操作</th></tr></thead>
          <tbody>
            <tr v-for="r in records" :key="r.id">
              <td>{{ formatDate(r.date) }}</td><td>{{ r.time_detail || '—' }}</td><td>{{ r.name }}</td><td>{{ r.dose || '—' }}</td><td>{{ r.time_period || '—' }}</td>
              <td :style="{ color: r.side_effect && r.side_effect !== '无' ? 'var(--danger)' : '' }">{{ r.side_effect || '—' }}</td>
              <td><button class="btn btn-sm" @click="startEdit(r)">编辑</button> <button class="btn btn-sm" style="background:var(--danger);color:white" @click="deleteRecord(r.id)">删</button></td>
            </tr>
            <tr v-if="!records.length"><td colspan="7" class="empty-state">暂无记录</td></tr>
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
.quick-btn { padding: 12px 8px; border: 1px solid var(--primary); border-radius: 8px; background: var(--primary-light); color: var(--primary); font-size: 0.85rem; cursor: pointer; font-weight: 600; }
.quick-btn:hover { background: var(--primary); color: white; }
.form-row { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 14px; margin-bottom: 12px; }
.form-group { margin-bottom: 10px; }
.form-group label { display: block; font-size: 0.82rem; color: var(--text-light); margin-bottom: 4px; }
.form-group input, .form-group select { width: 100%; padding: 10px; border: 1px solid var(--border); border-radius: 8px; background: var(--input-bg); color: var(--text); font-size: 0.9rem; box-sizing: border-box; }
.table-wrap { overflow-x: auto; }
table { width: 100%; border-collapse: collapse; font-size: 0.85rem; }
th, td { padding: 8px 10px; text-align: left; border-bottom: 1px solid var(--border); white-space: nowrap; }
th { color: var(--text-light); font-weight: 600; }
</style>
