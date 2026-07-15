<script setup>
import { onMounted, onUnmounted, ref, watch } from 'vue'
import { useAppStore } from '@/stores/app'

const store = useAppStore()
const isDark = ref(false)
const currentDate = ref('')

function updateDate() {
  currentDate.value = new Date().toLocaleDateString('zh-CN', {
    year: 'numeric', month: 'long', day: 'numeric', weekday: 'long'
  })
}

function toggleTheme() {
  isDark.value = !isDark.value
  document.body.classList.toggle('dark', isDark.value)
  localStorage.setItem('theme', isDark.value ? 'dark' : 'light')
}

onMounted(() => {
  updateDate()
  isDark.value = localStorage.getItem('theme') === 'dark'
  document.body.classList.toggle('dark', isDark.value)
})
</script>

<template>
  <!-- Header -->
  <header class="header">
    <div class="header-inner">
      <div class="header-left">
        <h1>🍃 糖尿病个性化治疗与控糖方案</h1>
        <select class="member-switch" v-model="store.currentMemberId" @change="store.switchMember">
          <option v-for="m in store.members" :key="m.id" :value="m.id">👤 {{ m.name }}</option>
        </select>
      </div>
      <div class="header-center">
        <div class="date-display">{{ currentDate }}</div>
      </div>
      <div class="header-right">
        <button class="theme-toggle" @click="toggleTheme">{{ isDark ? '☀️' : '🌙' }}</button>
      </div>
    </div>
  </header>

  <!-- Tab Bar -->
  <nav class="tabs">
    <button class="tab-btn active">
      <span class="emoji">🏠</span>
      <span>今日</span>
    </button>
    <button class="tab-btn" disabled>
      <span class="emoji">💊</span>
      <span>用药</span>
    </button>
    <button class="tab-btn" disabled>
      <span class="emoji">🍽️</span>
      <span>饮食</span>
    </button>
    <button class="tab-btn" disabled>
      <span class="emoji">🏃</span>
      <span>运动</span>
    </button>
    <button class="tab-btn" disabled>
      <span class="emoji">🩸</span>
      <span>血糖</span>
    </button>
    <button class="tab-btn" disabled>
      <span class="emoji">🎯</span>
      <span>目标</span>
    </button>
    <button class="tab-btn" disabled>
      <span class="emoji">🥗</span>
      <span>GI查询</span>
    </button>
    <button class="tab-btn" disabled>
      <span class="emoji">⚙️</span>
      <span>设置</span>
    </button>
  </nav>

  <!-- Page Content -->
  <div class="container">
    <router-view />
  </div>
</template>

<style>
:root {
  --primary: #2c7a7b;
  --primary-light: #e6fffa;
  --bg: #f7fafc;
  --card: #ffffff;
  --header-bg: #2c7a7b;
  --border: #e2e8f0;
  --text: #2d3748;
  --text-light: #718096;
  --danger: #e53e3e;
  --warning: #dd6b20;
  --success: #38a169;
  --input-bg: #edf2f7;
}
.dark {
  --primary: #319795;
  --primary-light: #234e52;
  --bg: #1a202c;
  --card: #2d3748;
  --header-bg: #1a202c;
  --border: #4a5568;
  --text: #e2e8f0;
  --text-light: #a0aec0;
  --input-bg: #4a5568;
}

* { box-sizing: border-box; margin: 0; padding: 0; }
body {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "PingFang SC", "Microsoft YaHei", sans-serif;
  background: var(--bg);
  color: var(--text);
  min-height: 100vh;
}

.header { background: var(--header-bg); padding: 18px 0; color: white; position: sticky; top: 0; z-index: 100; }
.header-inner { max-width: 1400px; margin: 0 auto; padding: 0 20px; display: flex; align-items: center; gap: 12px; }
.header h1 { font-size: 1.1rem; font-weight: 600; }
.header-left { display:flex; align-items:center; gap:10px; flex: 0 0 auto; }
.header-center { flex: 1 1 auto; display:flex; justify-content:center; min-width: 0; }
.header-right { display:flex; align-items:center; gap:8px; flex: 0 0 auto; }

.member-switch {
  padding: 6px 8px; border: 1px solid rgba(255,255,255,0.3); border-radius: 8px;
  font-size: 0.8rem; background: rgba(255,255,255,0.15); color: white; cursor: pointer;
  max-width: 120px;
}
.date-display { font-size: 1rem; opacity: 0.95; white-space: nowrap; font-weight: 500; }
.theme-toggle {
  background: rgba(255,255,255,0.15); border: none; border-radius: 8px;
  padding: 6px 10px; font-size: 1.2rem; cursor: pointer; color: white;
}

.tabs {
  display: flex; gap: 4px; padding: 12px 20px;
  background: var(--card); border-bottom: 1px solid var(--border);
  overflow-x: auto; max-width: 1400px; margin: 0 auto;
}
.tab-btn {
  flex: 1; padding: 10px 4px; font-size: 0.8rem; border: none;
  background: transparent; color: var(--text-light); border-radius: 8px;
  cursor: pointer; display: flex; flex-direction: column; align-items: center; gap: 2px;
  white-space: nowrap; min-width: 56px;
}
.tab-btn.active { background: var(--primary); color: white; font-weight: 600; }
.tab-btn:not(.active):not(:disabled):hover { background: var(--primary-light); }
.tab-btn:disabled { opacity: 0.4; cursor: not-allowed; }
.tab-btn .emoji { font-size: 1.1rem; }

.container { max-width: 1400px; margin: 0 auto; padding: 16px 20px; }

.card {
  background: var(--card); border-radius: 12px; padding: 18px 20px;
  margin-bottom: 16px; border: 1px solid var(--border);
}
.card h2 { font-size: 1.1rem; color: var(--text); margin-bottom: 12px; display: flex; align-items: center; gap: 6px; }

.stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); gap: 14px; }

.overview-card {
  background: var(--primary); color: white; border-radius: 14px; padding: 20px 24px;
  margin-bottom: 16px;
}
.overview-card h2 { color: white; }
.overview-row { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 14px; margin-top: 8px; }
.overview-item { background: rgba(255,255,255,0.12); border-radius: 10px; padding: 12px 14px; }
.overview-item .label { font-size: 0.78rem; opacity: 0.8; margin-bottom: 2px; }
.overview-item .value { font-size: 1.3rem; font-weight: 700; }

.btn {
  display: inline-flex; align-items: center; gap: 4px; padding: 10px 18px;
  border: 1px solid var(--border); border-radius: 8px; font-size: 0.85rem;
  cursor: pointer; background: var(--card); color: var(--text);
  transition: all 0.2s;
}
.btn-primary { background: var(--primary); color: white; border-color: var(--primary); }

.empty-state { text-align: center; color: var(--text-light); padding: 24px; font-size: 0.9rem; }

@media (max-width: 768px) {
  .header { padding: 12px 0; }
  .header h1 { font-size: 0.95rem; }
  .header-inner { padding: 0 12px; gap: 8px; flex-wrap: wrap; }
  .header-center { order: 3; flex: 1 0 100%; justify-content: flex-start; }
  .date-display { font-size: 0.9rem; }
  .tabs { padding: 8px 12px; gap: 2px; }
  .container { padding: 12px; }
}
</style>
