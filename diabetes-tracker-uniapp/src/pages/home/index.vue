<script setup>
import { ref, onMounted, computed } from 'vue'
import { useAppStore } from '@/stores/app'
import * as api from '@/api'
import { formatDate, glucoseBadge, todayStr } from '@/utils/format'

const store = useAppStore()

// 数据
const profile = ref(null)
const dietList = ref([])
const exerciseList = ref([])
const glucoseList = ref([])
const medList = ref([])

// 今天数据
const today = todayStr()
const todayDiet = computed(() => dietList.value.filter(r => r.date === today))
const todayExercise = computed(() => exerciseList.value.filter(r => r.date === today))
const todayGlucose = computed(() => glucoseList.value.filter(r => r.date === today))
const todayMed = computed(() => medList.value.filter(r => r.date === today))

const bmi = computed(() => {
  if (!profile.value) return '—'
  const h = parseFloat(profile.value.height) / 100
  const w = parseFloat(profile.value.weight)
  return isNaN(h) || isNaN(w) || h === 0 ? '—' : (w / (h * h)).toFixed(1)
})

const bmiStatus = computed(() => {
  const v = parseFloat(bmi.value)
  if (isNaN(v)) return ''
  if (v < 18.5) return '⚠️ 偏瘦'
  if (v <= 24) return '✅ 正常'
  if (v <= 28) return '⚠️ 超重'
  return '🔴 肥胖'
})

async function loadAll() {
  try {
    const [p, d, e, g, m] = await Promise.all([
      api.getProfile(),
      api.listDiet(),
      api.listExercise(),
      api.listGlucose(),
      api.listMedication(),
    ])
    profile.value = p
    dietList.value = d
    exerciseList.value = e
    glucoseList.value = g
    medList.value = m
  } catch (e) {
    console.error('加载数据失败:', e)
  }
}

onMounted(async () => {
  await store.loadMembers()
  await loadAll()
})
</script>

<template>
  <!-- 今日概览 -->
  <div class="overview-card">
    <h2>📋 今日健康概览</h2>
    <div class="overview-row">
      <div class="overview-item">
        <div class="label">BMI</div>
        <div class="value">{{ bmi }} <span style="font-size:0.75rem">{{ bmiStatus }}</span></div>
      </div>
      <div class="overview-item">
        <div class="label">今日饮食</div>
        <div class="value">{{ todayDiet.length }} <span style="font-size:0.75rem">条</span></div>
      </div>
      <div class="overview-item">
        <div class="label">今日运动</div>
        <div class="value">{{ todayExercise.length }} <span style="font-size:0.75rem">条</span></div>
      </div>
      <div class="overview-item">
        <div class="label">今日血糖</div>
        <div class="value">{{ todayGlucose.length }} <span style="font-size:0.75rem">条</span></div>
      </div>
    </div>
  </div>

  <!-- 个人信息 -->
  <div class="card">
    <h2><span>👤</span> 个人信息</h2>
    <div class="stats-grid" v-if="profile">
      <div><b>身高</b><br/>{{ profile.height }} cm</div>
      <div><b>体重</b><br/>{{ profile.weight }} kg</div>
      <div><b>年龄</b><br/>{{ profile.age }}</div>
      <div><b>体重目标</b><br/>{{ profile.weight_target }} kg</div>
      <div><b>空腹目标</b><br/>{{ profile.glucose_fasting_target }} mmol/L</div>
      <div><b>餐后目标</b><br/>{{ profile.glucose_post_target }} mmol/L</div>
    </div>
    <div class="empty-state" v-else>未设置个人信息，请前往设置 Tab 配置</div>
  </div>

  <!-- 今日饮食 -->
  <div class="card">
    <h2><span>🍽️</span> 今日饮食</h2>
    <div v-if="todayDiet.length > 0">
      <div v-for="r in todayDiet" :key="'d'+r.id"
        style="padding:8px 0; border-bottom:1px solid var(--border); font-size:0.85rem;">
        <b>{{ r.meal }}</b> · {{ r.food }}
        <span v-if="r.calories" style="color:var(--text-light); margin-left:8px;">{{ r.calories }} kcal</span>
        <span v-if="r.glucose" :style="{ color: parseFloat(r.glucose) > 7.8 ? 'var(--danger)' : 'var(--success)' }">
          · 餐后 {{ r.glucose }} mmol/L {{ glucoseBadge(r.glucose, '餐后2h') }}
        </span>
      </div>
    </div>
    <div class="empty-state" v-else>暂无今日饮食记录</div>
  </div>

  <!-- 今日血糖 -->
  <div class="card">
    <h2><span>🩸</span> 今日血糖</h2>
    <div v-if="todayGlucose.length > 0">
      <div v-for="r in todayGlucose" :key="'g'+r.id"
        style="padding:8px 0; border-bottom:1px solid var(--border); font-size:0.85rem;">
        <b>{{ r.time }}</b> · {{ r.type }}
        <span :style="{ color: parseFloat(r.value) > 7.8 ? 'var(--danger)' : 'var(--success)', marginLeft:'8px' }">
          {{ r.value }} mmol/L
        </span>
        <span v-if="r.note" style="color:var(--text-light);"> · {{ r.note }}</span>
      </div>
    </div>
    <div class="empty-state" v-else>暂无今日血糖记录</div>
  </div>

  <!-- 今日运动 -->
  <div class="card">
    <h2><span>🏃</span> 今日运动</h2>
    <div v-if="todayExercise.length > 0">
      <div v-for="r in todayExercise" :key="'e'+r.id"
        style="padding:8px 0; border-bottom:1px solid var(--border); font-size:0.85rem;">
        <b>{{ r.type }}</b>
        <span v-if="r.duration" style="color:var(--text-light); margin-left:6px;">{{ r.duration }} 分钟</span>
        <span v-if="r.intensity" style="color:var(--text-light); margin-left:6px;">{{ r.intensity }}</span>
      </div>
    </div>
    <div class="empty-state" v-else>暂无今日运动记录</div>
  </div>

  <!-- 今日用药 -->
  <div class="card">
    <h2><span>💊</span> 今日用药</h2>
    <div v-if="todayMed.length > 0">
      <div v-for="r in todayMed" :key="'m'+r.id"
        style="padding:8px 0; border-bottom:1px solid var(--border); font-size:0.85rem;">
        <b>{{ r.time_detail || '—' }}</b>
        · {{ r.name }} {{ r.dose }}
        <span v-if="r.time_period" style="color:var(--text-light); margin-left:6px;">{{ r.time_period }}</span>
        <span v-if="r.side_effect && r.side_effect !== '无'"
          style="color:var(--danger); margin-left:6px;">不良反应: {{ r.side_effect }}</span>
      </div>
    </div>
    <div class="empty-state" v-else>暂无今日用药记录</div>
  </div>
</template>
