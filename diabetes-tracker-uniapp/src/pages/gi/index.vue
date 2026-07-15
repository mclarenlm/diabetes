<script setup>
import { ref, computed } from 'vue'
import { GI_DATA, giColor, giLabel } from '@/utils/gi-data'

const search = ref('')
const filtered = computed(() => {
  const kw = search.value.trim().toLowerCase()
  return kw ? GI_DATA.filter(r => r.name.toLowerCase().includes(kw) || r.cat.toLowerCase().includes(kw)) : GI_DATA
})
const cats = computed(() => {
  const m = {}
  filtered.value.forEach(r => { if (!m[r.cat]) m[r.cat] = []; m[r.cat].push(r) })
  return m
})
const catOrder = ['主食', '水果', '蔬菜', '豆奶蛋', '肉鱼', '零食']
</script>

<template>
  <div class="card">
    <h2>🥗 食物升糖指数(GI)查询</h2>
    <p style="font-size:0.82rem; color:var(--text-light); margin-bottom:12px;">
      GI < 55 为低GI（推荐），55-70 为中GI（适量），> 70 为高GI（少吃）
    </p>
    <input v-model="search" placeholder="输入食物名称搜索，如：米饭、苹果、燕麦..." style="width:100%; padding:10px 14px; border:1px solid var(--border); border-radius:8px; font-size:0.9rem; background:var(--input-bg); color:var(--text); box-sizing:border-box; margin-bottom:12px;">
    <div v-for="cat in catOrder" :key="cat" style="margin-bottom:14px;" v-show="cats[cat]">
      <div style="font-weight:600; font-size:0.85rem; color:var(--text-light); margin-bottom:6px;">{{ cat }}（{{ cats[cat].length }}）</div>
      <div style="display:grid; grid-template-columns:repeat(auto-fill, minmax(150px, 1fr)); gap:6px;">
        <div v-for="r in cats[cat]" :key="r.name" :style="{ background:'var(--primary-light)', borderRadius:'8px', padding:'8px 10px', borderLeft:'3px solid '+giColor(r.gi) }">
          <div style="font-weight:600; font-size:0.82rem;">{{ r.name }}</div>
          <div style="font-size:0.78rem;" :style="{ color: giColor(r.gi) }">{{ r.gi > 0 ? 'GI ' + r.gi : '无GI' }} · {{ giLabel(r.gi) }}</div>
        </div>
      </div>
    </div>
    <div v-if="!filtered.length" style="text-align:center; color:var(--text-light); padding:20px;">未找到相关食物</div>
  </div>
</template>
