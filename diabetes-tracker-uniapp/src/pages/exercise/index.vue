<script setup>
import { ref, onMounted } from 'vue'
import * as api from '@/api'
import { formatDate, todayStr } from '@/utils/format'

const records = ref([])
const editingId = ref(null)
const today = todayStr()
const form = ref({ date: today, type: '', duration: '', intensity: '', beforeGlucose: '', afterGlucose: '', sugar: '是', symptom: '', note: '' })

async function loadData() {
  records.value = await api.listExercise()
}

async function submitForm() {
  if (!form.value.type) { alert('请填写运动类型'); return }
  const data = {
    date: form.value.date, type: form.value.type, duration: form.value.duration,
    intensity: form.value.intensity, beforeGlucose: form.value.beforeGlucose,
    afterGlucose: form.value.afterGlucose, sugar: form.value.sugar,
    symptom: form.value.symptom, note: form.value.note
  }
  if (editingId.value) await api.updateExercise(editingId.value, data)
  else await api.addExercise(data)
  cancelEdit()
  await loadData()
}

function startEdit(r) {
  editingId.value = r.id
  form.value = { date: r.date, type: r.type, duration: String(r.duration || ''), intensity: r.intensity || '', beforeGlucose: String(r.before_glucose || ''), afterGlucose: String(r.after_glucose || ''), sugar: r.sugar_carried || '是', symptom: r.symptom || '', note: r.note || '' }
}

function cancelEdit() {
  editingId.value = null
  form.value = { date: today, type: '', duration: '', intensity: '', beforeGlucose: '', afterGlucose: '', sugar: '是', symptom: '', note: '' }
}

async function deleteRecord(id) {
  if (!confirm('确定删除？')) return
  await api.deleteExercise(id)
  await loadData()
}

async function copyLast() {
  if (!records.value.length) { alert('暂无记录可复制'); return }
  const last = records.value[0]
  form.value = { date: today, type: last.type || '', duration: String(last.duration || ''), intensity: last.intensity || '', sugar: last.sugar_carried || '是', beforeGlucose: '', afterGlucose: '', symptom: '', note: '' }
}

onMounted(loadData)
</script>

<template>
  <div v-if="editingId" class="edit-bar">📝 正在编辑 #{{ editingId }} <button class="btn btn-sm" @click="cancelEdit">取消</button></div>

  <div class="dual-layout">
    <div class="dual-left">
      <div class="card">
        <h2>📝 添加运动记录</h2>
        <form @submit.prevent="submitForm">
          <div class="form-row">
            <div class="form-group"><label>日期</label><input type="date" v-model="form.date" required></div>
            <div class="form-group"><label>运动类型</label><input type="text" v-model="form.type" placeholder="如 快走/游泳/力量训练" required></div>
            <div class="form-group"><label>时长 (分钟)</label><input type="number" v-model="form.duration" min="0"></div>
            <div class="form-group"><label>强度</label><select v-model="form.intensity"><option value="">未记录</option><option>低</option><option>中</option><option>高</option></select></div>
          </div>
          <div class="form-row">
            <div class="form-group"><label>运动前血糖</label><input type="number" v-model="form.beforeGlucose" step="0.1" min="0" max="30"></div>
            <div class="form-group"><label>运动后血糖</label><input type="number" v-model="form.afterGlucose" step="0.1" min="0" max="30"></div>
            <div class="form-group"><label>是否携带糖果</label><select v-model="form.sugar"><option>是</option><option>否</option></select></div>
          </div>
          <div class="form-row">
            <div class="form-group"><label>不适症状</label><select v-model="form.symptom"><option value="">无</option><option>头晕</option><option>心慌</option><option>出冷汗</option><option>乏力</option><option>其他</option></select></div>
            <div class="form-group"><label>备注</label><input type="text" v-model="form.note"></div>
          </div>
          <div style="display:flex; gap:8px;">
            <button type="submit" class="btn btn-primary">{{ editingId ? '💾 更新' : '➕ 添加' }}</button>
            <button type="button" class="btn btn-sm" @click="copyLast">📋 复制上一条</button>
          </div>
        </form>
      </div>
    </div>
    <div class="dual-right">
      <div class="card">
        <h2>📋 运动记录</h2>
        <div class="table-wrap">
          <table><thead><tr><th>日期</th><th>类型</th><th>时长</th><th>强度</th><th>前血糖</th><th>后血糖</th><th>糖果</th><th>操作</th></tr></thead>
          <tbody>
            <tr v-for="r in records" :key="r.id">
              <td>{{ formatDate(r.date) }}</td><td>{{ r.type }}</td><td>{{ r.duration ? r.duration + '分' : '—' }}</td><td>{{ r.intensity || '—' }}</td>
              <td>{{ r.before_glucose || '—' }}</td><td>{{ r.after_glucose || '—' }}</td><td>{{ r.sugar_carried || '—' }}</td>
              <td><button class="btn btn-sm" @click="startEdit(r)">编辑</button> <button class="btn btn-sm" style="background:var(--danger);color:white" @click="deleteRecord(r.id)">删</button></td>
            </tr>
            <tr v-if="!records.length"><td colspan="8" class="empty-state">暂无记录</td></tr>
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
