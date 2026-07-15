<script setup>
import { ref, onMounted } from 'vue'
import { useAppStore } from '@/stores/app'
import * as api from '@/api'
import { todayStr } from '@/utils/format'

const store = useAppStore()
const today = todayStr()

// Profile
const profile = ref({ height: '175', weight: '51', age: '35', gender: '男', glucose_fasting_target: '5.6', glucose_post_target: '7.8', weight_target: '56' })
const bmi = ref(0)

function calcBMI() {
  const h = parseFloat(profile.value.height) / 100
  const w = parseFloat(profile.value.weight)
  bmi.value = (h && w) ? (w / (h * h)) : 0
}

async function loadProfile() {
  try {
    const p = await api.getProfile()
    if (p && p.height) profile.value = p
  } catch {}
  calcBMI()
}

async function saveProfile() {
  await api.updateProfile(profile.value)
  alert('✅ 设置已保存')
}

// Members
const memberStats = ref({})
const showMemberModal = ref(false)
const memberForm = ref({ id: null, name: '', role: '家属' })

async function loadMembers() {
  await store.loadMembers()
  try {
    const bk = await api.backup()
    for (const m of store.members) {
      let c = 0
      for (const t of ['diet', 'exercise', 'glucose', 'medication', 'followup'])
        if (bk[t]) c += bk[t].filter(r => r.user_id === m.id).length
      memberStats.value[m.id] = c
    }
  } catch {}
}

function openMemberEdit(m = null) {
  memberForm.value = m ? { id: m.id, name: m.name, role: m.role || '家属' } : { id: null, name: '', role: '家属' }
  showMemberModal.value = true
}

async function submitMember() {
  if (!memberForm.value.name) { alert('请填写姓名'); return }
  if (memberForm.value.id) await api.updateMember(memberForm.value.id, { name: memberForm.value.name, role: memberForm.value.role })
  else await api.addMember({ name: memberForm.value.name, role: memberForm.value.role })
  showMemberModal.value = false
  await loadMembers()
}

async function deleteMember(id) {
  if (!confirm('删除该成员将同时清空其所有数据，确定继续？')) return
  await api.deleteMember(id)
  await loadMembers()
  if (store.currentMemberId === id) store.switchMember()
}

async function switchMember(uid) {
  await api.switchMember(uid)
  store.currentMemberId = uid
  location.reload()
}

const memberColors = ['#3182ce', '#e53e3e', '#38a169', '#805ad5', '#d69e2e', '#dd6b20']

// Backup
async function doBackup() {
  const bk = await api.backup()
  const blob = new Blob([JSON.stringify(bk, null, 2)], { type: 'application/json' })
  const a = document.createElement('a')
  a.href = URL.createObjectURL(blob)
  a.download = `diabetes-backup-${today}.json`
  a.click()
}

function doRestore() {
  const input = document.createElement('input')
  input.type = 'file'
  input.accept = '.json'
  input.onchange = async () => {
    const file = input.files[0]
    if (!file) return
    if (!confirm('恢复将覆盖当前所有数据，确定继续？')) return
    const text = await file.text()
    const r = await api.restore(JSON.parse(text))
    alert(r.ok ? '✅ 数据已恢复' : '❌ 恢复失败：' + (r.error || ''))
    location.reload()
  }
  input.click()
}

onMounted(() => { loadProfile(); loadMembers(); calcBMI() })
</script>

<template>
  <!-- 个人信息 -->
  <div class="card">
    <h2>👤 个人信息</h2>
    <div class="profile-grid">
      <div>
        <h3 style="font-size:0.9rem; margin-bottom:10px;">基本信息</h3>
        <div class="form-group"><label>身高 (cm)</label><input type="number" v-model="profile.height" step="0.1" @input="calcBMI"></div>
        <div class="form-group"><label>当前体重 (kg)</label><input type="number" v-model="profile.weight" step="0.1" @input="calcBMI"></div>
        <div class="form-group"><label>年龄</label><input type="number" v-model="profile.age"></div>
        <div class="form-group"><label>性别</label><select v-model="profile.gender"><option>男</option><option>女</option></select></div>
      </div>
      <div>
        <h3 style="font-size:0.9rem; margin-bottom:10px;">控糖目标</h3>
        <div class="form-group"><label>空腹血糖目标 (mmol/L)</label><input type="number" v-model="profile.glucose_fasting_target" step="0.1"></div>
        <div class="form-group"><label>餐后2h血糖目标 (mmol/L)</label><input type="number" v-model="profile.glucose_post_target" step="0.1"></div>
        <div class="form-group"><label>体重目标 (kg)</label><input type="number" v-model="profile.weight_target" step="0.1"></div>
        <div style="margin-top:10px; font-size:0.82rem; color:var(--text-light);">
          BMI: <b>{{ bmi ? bmi.toFixed(1) : '—' }}</b>
          <span v-if="bmi" :style="{ color: bmi < 18.5 ? '#e53e3e' : bmi <= 24 ? '#38a169' : '#dd6b20' }">
            · {{ bmi < 18.5 ? '偏瘦' : bmi <= 24 ? '正常' : bmi <= 28 ? '超重' : '肥胖' }}
          </span>
        </div>
      </div>
    </div>
    <button class="btn btn-primary" style="margin-top:14px;" @click="saveProfile">保存设置</button>
  </div>

  <!-- 成员管理 -->
  <div class="card">
    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
      <h2 style="margin:0;">👥 家庭成员管理</h2>
      <button class="btn btn-sm" @click="openMemberEdit()" style="background:var(--primary); color:white;">➕ 添加成员</button>
    </div>
    <p style="font-size:0.8rem; color:var(--text-light); margin-bottom:10px;">页头切换后数据完全隔离。本人为默认成员不可删除。</p>
    <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(240px, 1fr)); gap:10px;">
      <div v-for="m in store.members" :key="m.id"
        :style="{ background:'var(--primary-light)', borderRadius:'12px', padding:'14px', border:'2px solid '+(m.id===store.currentMemberId?memberColors[(m.id-1)%6]:'var(--border)') }">
        <div style="display:flex; align-items:center; gap:8px; margin-bottom:8px;">
          <div :style="{ width:'36px',height:'36px',borderRadius:'50%',background:memberColors[(m.id-1)%6],color:'white',display:'flex',alignItems:'center',justifyContent:'center',fontSize:'1rem',fontWeight:600 }">{{ m.name.charAt(0) }}</div>
          <div>
            <div style="font-weight:600; font-size:0.9rem;">{{ m.name }} <span v-if="m.id===store.currentMemberId" :style="{color:memberColors[(m.id-1)%6],fontSize:'0.7rem'}">● 当前</span></div>
            <div style="font-size:0.72rem; color:var(--text-light);">{{ m.role || '' }}{{ m.id===1?' · 默认':'' }}</div>
          </div>
        </div>
        <div style="font-size:0.78rem; color:var(--text-light); margin-bottom:8px;">📋 共 <b style="color:var(--text);">{{ memberStats[m.id]||0 }}</b> 条记录</div>
        <div style="display:flex; gap:6px;">
          <button v-if="m.id!==store.currentMemberId" class="btn btn-sm" @click="switchMember(m.id)" :style="{ background: memberColors[(m.id-1)%6], color:'white', flex:1 }">切换</button>
          <button v-if="m.id!==1" class="btn btn-sm" @click="openMemberEdit(m)" style="flex:1;">编辑</button>
          <button v-if="m.id!==1" class="btn btn-sm" @click="deleteMember(m.id)" style="background:var(--danger); color:white; flex:1;">删除</button>
        </div>
      </div>
    </div>
  </div>

  <!-- 备份恢复 -->
  <div class="card">
    <h2>📦 数据备份与恢复</h2>
    <p style="font-size:0.82rem; color:var(--text-light); margin-bottom:12px;">导出全部数据为JSON文件，可用于跨设备迁移。恢复操作会覆盖当前所有数据。</p>
    <div style="display:flex; gap:12px;">
      <button class="btn btn-primary" @click="doBackup">📥 导出备份</button>
      <button class="btn" style="background:var(--warning); color:white;" @click="doRestore">📤 导入恢复</button>
    </div>
  </div>

  <!-- 项目信息 -->
  <div class="card">
    <h2>ℹ️ 项目信息</h2>
    <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(180px, 1fr)); gap:10px;">
      <div style="background:var(--primary-light); border-radius:8px; padding:10px; border-left:3px solid var(--primary);"><div style="font-size:0.72rem; color:var(--text-light);">版本</div><div style="font-weight:600;">v3.4.0</div></div>
      <div style="background:var(--primary-light); border-radius:8px; padding:10px; border-left:3px solid #3182ce;"><div style="font-size:0.72rem; color:var(--text-light);">技术栈</div><div>Vue 3 + Pinia + ECharts</div></div>
      <div style="background:var(--primary-light); border-radius:8px; padding:10px; border-left:3px solid #38a169;"><div style="font-size:0.72rem; color:var(--text-light);">后端</div><div>Flask + SQLite</div></div>
      <div style="background:var(--primary-light); border-radius:8px; padding:10px; border-left:3px solid #805ad5;"><div style="font-size:0.72rem; color:var(--text-light);">GitHub</div><div><a href="https://github.com/mclarenlm/diabetes-tracker-nas-app" target="_blank">mclarenlm/diabetes-tracker-nas-app</a></div></div>
    </div>
  </div>

  <!-- 成员弹窗 -->
  <div v-if="showMemberModal" style="position:fixed;inset:0;background:rgba(0,0,0,0.5);z-index:1000;display:flex;align-items:center;justify-content:center;padding:16px;" @click.self="showMemberModal=false">
    <div style="background:var(--card);border-radius:14px;width:100%;max-width:380px;padding:20px;">
      <h3 style="margin:0 0 14px;">{{ memberForm.id ? '编辑成员' : '添加成员' }}</h3>
      <div class="form-group"><label>姓名</label><input v-model="memberForm.name" placeholder="如 张三 / 妈妈" style="width:100%;padding:10px;border:1px solid var(--border);border-radius:8px;box-sizing:border-box;"></div>
      <div class="form-group"><label>角色</label><select v-model="memberForm.role" style="width:100%;padding:10px;border:1px solid var(--border);border-radius:8px;box-sizing:border-box;"><option>本人</option><option>配偶</option><option>子女</option><option>父母</option><option>家属</option></select></div>
      <div style="display:flex;gap:10px;margin-top:16px;"><button class="btn btn-primary" style="flex:1;" @click="submitMember">保存</button><button class="btn btn-sm" style="flex:1;background:var(--border);" @click="showMemberModal=false">取消</button></div>
    </div>
  </div>
</template>

<style scoped>
.profile-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; }
.form-group { margin-bottom: 10px; }
.form-group label { display: block; font-size: 0.82rem; color: var(--text-light); margin-bottom: 4px; }
.form-group input, .form-group select { width: 100%; padding: 10px; border: 1px solid var(--border); border-radius: 8px; background: var(--input-bg); color: var(--text); font-size: 0.9rem; box-sizing: border-box; }
</style>
