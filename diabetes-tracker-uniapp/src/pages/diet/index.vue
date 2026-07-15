<script setup>
import { ref, computed, onMounted } from 'vue'
import * as api from '@/api'
import { formatDate, todayStr } from '@/utils/format'

const records = ref([])
const templates = ref([])
const editingId = ref(null)
const today = todayStr()
const form = ref({ date: today, meal: '早餐', food: '', calories: '', glucose: '', order: '', note: '' })

// 模板弹窗
const showTplModal = ref(false)
const tplForm = ref({ id: null, name: '', meal: '早餐', food: '', calories: '', eating_order: '' })

async function loadData() {
  records.value = await api.listDiet()
  templates.value = await api.listMealTemplates()
}

async function submitForm() {
  if (!form.value.food) { alert('请填写食物内容'); return }
  const data = { ...form.value, order: form.value.order }
  if (editingId.value) await api.updateDiet(editingId.value, data)
  else await api.addDiet(data)
  cancelEdit()
  await loadData()
}

function startEdit(r) {
  editingId.value = r.id
  form.value = { date: r.date, meal: r.meal, food: r.food, calories: String(r.calories || ''), glucose: String(r.glucose || ''), order: r.eating_order || '', note: r.note || '' }
}

function cancelEdit() {
  editingId.value = null
  form.value = { date: today, meal: '早餐', food: '', calories: '', glucose: '', order: '', note: '' }
}

async function deleteRecord(id) {
  if (!confirm('确定删除？')) return
  await api.deleteDiet(id)
  await loadData()
}

async function copyLast() {
  if (!records.value.length) { alert('暂无记录可复制'); return }
  const last = records.value[0]
  form.value = { date: today, meal: last.meal || '早餐', food: last.food || '', calories: String(last.calories || ''), order: last.eating_order || '', glucose: '', note: '' }
}

function applyTemplate(t) {
  form.value.meal = t.meal || '早餐'
  form.value.food = t.food || ''
  form.value.calories = String(t.calories || '')
  form.value.order = t.eating_order || ''
  form.value.glucose = ''
  form.value.note = ''
}

function openTplModal(t = null) {
  tplForm.value = t ? { id: t.id, name: t.name, meal: t.meal, food: t.food, calories: String(t.calories || ''), eating_order: t.eating_order || '' }
                    : { id: null, name: '', meal: '早餐', food: '', calories: '', eating_order: '' }
  showTplModal.value = true
}

async function saveTpl() {
  if (!tplForm.value.name || !tplForm.value.food) { alert('请填写名称和食物'); return }
  if (tplForm.value.id) await api.updateMealTemplate(tplForm.value.id, tplForm.value)
  else await api.addMealTemplate(tplForm.value)
  showTplModal.value = false
  await loadData()
}

async function deleteTpl(id) {
  if (!confirm('确定删除模板？')) return
  await api.deleteMealTemplate(id)
  await loadData()
}

onMounted(loadData)
</script>

<template>
  <div v-if="editingId" class="edit-bar">📝 正在编辑 #{{ editingId }} <button class="btn btn-sm" @click="cancelEdit">取消</button></div>

  <!-- 饮食模板 -->
  <div class="card">
    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
      <h2 style="margin:0;">🍱 饮食模板</h2>
      <button class="btn btn-sm" @click="openTplModal()" style="background:var(--primary); color:white;">➕ 新建</button>
    </div>
    <div style="display:grid; grid-template-columns:repeat(auto-fit,minmax(200px,1fr)); gap:8px;">
      <div v-for="t in templates" :key="t.id" style="background:var(--primary-light); border-radius:10px; padding:10px 12px; border:1px solid var(--border);">
        <div style="font-weight:600; font-size:0.85rem; cursor:pointer;" @click="applyTemplate(t)">🍱 {{ t.name }}</div>
        <div style="font-size:0.78rem; color:var(--text-light); cursor:pointer;" @click="applyTemplate(t)">{{ t.meal }} · {{ t.food }}</div>
        <div v-if="t.calories" style="font-size:0.72rem; color:var(--text-light);">{{ t.calories }} kcal</div>
        <div style="display:flex; gap:6px; margin-top:8px;">
          <button class="btn btn-sm" @click="applyTemplate(t)" style="background:var(--primary); color:white; flex:1;">应用</button>
          <button class="btn btn-sm" @click="openTplModal(t)" style="flex:1;">编辑</button>
          <button class="btn btn-sm" style="background:var(--danger); color:white;" @click="deleteTpl(t.id)">删</button>
        </div>
      </div>
    </div>
  </div>

  <div class="dual-layout">
    <div class="dual-left">
      <div class="card">
        <h2>📝 添加饮食记录</h2>
        <form @submit.prevent="submitForm">
          <div class="form-row">
            <div class="form-group"><label>日期</label><input type="date" v-model="form.date" required></div>
            <div class="form-group"><label>餐次</label><select v-model="form.meal"><option>早餐</option><option>午餐</option><option>晚餐</option><option>加餐</option></select></div>
          </div>
          <div class="form-row">
            <div class="form-group"><label>食物内容</label><input type="text" v-model="form.food" placeholder="如 糙米饭100g+鲈鱼150g" required></div>
            <div class="form-group"><label>热量 (kcal)</label><input type="number" v-model="form.calories" min="0"></div>
          </div>
          <div class="form-row">
            <div class="form-group"><label>餐后血糖</label><input type="number" v-model="form.glucose" step="0.1" min="0" max="30"></div>
            <div class="form-group"><label>进食顺序</label><select v-model="form.order"><option value="">未注意</option><option value="蔬菜→蛋白质→主食">蔬菜→蛋白质→主食（推荐）</option><option value="主食→蛋白质→蔬菜">主食→蛋白质→蔬菜</option><option value="混合进食">混合进食</option></select></div>
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
        <h2>📋 饮食记录</h2>
        <div class="table-wrap">
          <table><thead><tr><th>日期</th><th>餐次</th><th>食物</th><th>热量</th><th>餐后血糖</th><th>操作</th></tr></thead>
          <tbody>
            <tr v-for="r in records" :key="r.id">
              <td>{{ formatDate(r.date) }}</td><td>{{ r.meal }}</td><td>{{ r.food }}</td><td>{{ r.calories || '—' }}</td>
              <td>{{ r.glucose ? r.glucose + ' mmol/L' : '—' }}</td>
              <td><button class="btn btn-sm" @click="startEdit(r)">编辑</button> <button class="btn btn-sm" style="background:var(--danger);color:white" @click="deleteRecord(r.id)">删</button></td>
            </tr>
            <tr v-if="!records.length"><td colspan="6" class="empty-state">暂无记录</td></tr>
          </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>

  <!-- 模板弹窗 -->
  <div v-if="showTplModal" style="position:fixed;inset:0;background:rgba(0,0,0,0.5);z-index:1000;display:flex;align-items:center;justify-content:center;padding:16px;" @click.self="showTplModal=false">
    <div style="background:var(--card);border-radius:14px;width:100%;max-width:440px;padding:20px;">
      <h3 style="margin:0 0 14px;">{{ tplForm.id ? '编辑模板' : '新建模板' }}</h3>
      <div class="form-group"><label>名称</label><input type="text" v-model="tplForm.name" placeholder="如 营养早餐" style="width:100%;padding:10px;border:1px solid var(--border);border-radius:8px;box-sizing:border-box;"></div>
      <div class="form-row">
        <div class="form-group"><label>餐次</label><select v-model="tplForm.meal"><option>早餐</option><option>午餐</option><option>晚餐</option><option>加餐</option></select></div>
        <div class="form-group"><label>热量</label><input type="number" v-model="tplForm.calories" min="0"></div>
      </div>
      <div class="form-group"><label>食物内容</label><textarea v-model="tplForm.food" rows="3" placeholder="如 糙米饭100g+清蒸鲈鱼150g" style="width:100%;padding:10px;border:1px solid var(--border);border-radius:8px;box-sizing:border-box;"></textarea></div>
      <div class="form-group"><label>进食顺序</label><select v-model="tplForm.eating_order"><option value="">未注意</option><option value="蔬菜→蛋白质→主食">蔬菜→蛋白质→主食</option><option value="混合进食">混合进食</option></select></div>
      <div style="display:flex;gap:10px;margin-top:16px;"><button class="btn btn-primary" style="flex:1;" @click="saveTpl">保存</button><button class="btn btn-sm" style="flex:1;background:var(--border);" @click="showTplModal=false">取消</button></div>
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
.form-group input, .form-group select, .form-group textarea { width: 100%; padding: 10px; border: 1px solid var(--border); border-radius: 8px; background: var(--input-bg); color: var(--text); font-size: 0.9rem; box-sizing: border-box; }
.table-wrap { overflow-x: auto; }
table { width: 100%; border-collapse: collapse; font-size: 0.85rem; }
th, td { padding: 8px 10px; text-align: left; border-bottom: 1px solid var(--border); white-space: nowrap; }
th { color: var(--text-light); font-weight: 600; }
</style>
