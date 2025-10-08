<!-- src/views/admin/AdminOverview.vue -->
<template>
  <div class="overview">
    <h1>Admin Overview</h1>
    <p class="muted">This is the admin home (dashboard & entry). Use the shortcuts below to manage data.</p>

    <div class="cards">
      <div class="card">
        <div class="title">Teams</div>
        <div class="num">
          <template v-if="loading">—</template>
          <template v-else>{{ teamCount }}</template>
        </div>
      </div>

      <div class="card">
        <div class="title">Players</div>
        <div class="num">
          <template v-if="loading">—</template>
          <template v-else>{{ playerCount }}</template>
        </div>
      </div>
    </div>

    <div class="actions">
      <RouterLink class="btn" to="/admin-panel/teams">Team Management</RouterLink>
      <RouterLink class="btn" to="/admin-panel/matches">Schedule Management</RouterLink>
      <RouterLink class="btn" to="/admin-panel/ladder">Ladder</RouterLink>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import api from '@/api/axios'

const loading = ref(true)
const teamCount = ref(0)
const playerCount = ref(0)

/**
 * Count strategy (no alerts):
 * 1) GET /teams -> teamCount
 * 2) For each team id, GET /teams/:id/players -> sum lengths  => playerCount
 *    - Filter out items without a valid id (some lists may contain placeholders)
 *    - No /players probe to avoid triggering global axios alert
 */
async function loadCounts () {
  loading.value = true
  try {
    // 1) Teams
    const teamsRes = await api.get('/teams')
    const raw = teamsRes?.data ?? teamsRes
    const teams = Array.isArray(raw) ? raw : (raw?.teams ?? [])
    const list = Array.isArray(teams) ? teams : []
    teamCount.value = list.length

    // 2) Sum players per team
    const getId = (t) => t?.id ?? t?.team_id
    const teamIds = list.map(getId).filter(id => Number.isFinite(+id) && +id > 0)

    const counts = await Promise.all(
      teamIds.map(async (tid) => {
        try {
          const r = await api.get(`/teams/${tid}/players`)
          const body = r?.data ?? r
          const arr = Array.isArray(body) ? body : (body?.players ?? [])
          return Array.isArray(arr) ? arr.length : 0
        } catch {
          return 0
        }
      })
    )
    playerCount.value = counts.reduce((a, b) => a + (Number.isFinite(+b) ? +b : 0), 0)
  } catch (e) {
    console.error('[overview] loadCounts failed:', e)
    teamCount.value = 0
    playerCount.value = 0
  } finally {
    loading.value = false
  }
}

onMounted(loadCounts)
</script>

<style scoped>
.overview { padding: 24px; }
h1 { margin: 0 0 8px; font-size: 22px; font-weight: 800; }
.muted { color:#6b7280; margin-bottom: 16px; }

.cards {
  display:grid;
  grid-template-columns: repeat(2, minmax(0,1fr));
  gap: 12px;
  margin-bottom: 16px;
}
.card {
  background:#fff; border:1px solid #eee; border-radius:16px;
  padding:14px 16px; box-shadow: 0 1px 2px rgba(0,0,0,.04);
}
.title { color:#6b7280; font-size:12px; }
.num { font-size:28px; font-weight:800; margin-top:6px; }

.actions { display:flex; gap:12px; flex-wrap: wrap; }

/* RouterLink as button */
.btn {
  display:inline-flex; align-items:center; justify-content:center;
  height:36px; padding:0 14px; border-radius:10px;
  background:#111827; color:#fff; text-decoration:none;
  border:1px solid #e5e7eb; box-shadow: 0 2px 0 rgba(0,0,0,.06);
}
.btn:hover { opacity:.95; }
.btn:active { transform: translateY(1px); }
</style>
