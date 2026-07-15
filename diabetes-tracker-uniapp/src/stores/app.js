import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useAppStore = defineStore('app', () => {
  const members = ref([{ id: 1, name: '本人', role: '本人' }])
  const currentMemberId = ref(1)
  const authEnabled = ref(false)
  const authed = ref(true)

  function switchMember() {
    fetch(`/api/members/switch`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ user_id: currentMemberId.value })
    }).catch(() => {})
  }

  async function loadMembers() {
    try {
      const r = await fetch('/api/members')
      members.value = await r.json()
      const cur = await fetch('/api/members/current')
      if (cur.ok) {
        const c = await cur.json()
        currentMemberId.value = c.id
      }
    } catch {}
    try {
      const s = await fetch('/api/auth-status')
      const st = await s.json()
      authEnabled.value = st.enabled
      authed.value = st.authed
    } catch {}
  }

  return { members, currentMemberId, authEnabled, authed, switchMember, loadMembers }
})
