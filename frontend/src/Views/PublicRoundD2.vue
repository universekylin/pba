<!-- src/views/public/PublicRoundD2.vue -->
<template>
  <div class="page">
    <div class="topbar">
      <button class="btn light" @click="$router.back()">← Back</button>
      <h2>Round {{ roundNo }} · Division 2</h2>
      <div class="fill"></div>
    </div>

    <section class="card">
      <div v-if="loading" class="empty">Loading…</div>

      <template v-else>
        <div v-if="matches.length === 0" class="empty">No games in this round</div>

        <div v-for="m in matches" :key="m.id" class="match">
          <!-- Home -->
          <div class="side">
            <div class="teamcell">
              <img class="logo" :src="logoOf(m.home_team)" alt="" />
              <span class="name">{{ m.home_team?.name || 'TBD' }}</span>
            </div>
          </div>

          <!-- Score -->
          <div class="center">
            <span class="score-num">{{ m.home_pts ?? 0 }}</span>
            <span class="dash">-</span>
            <span class="score-num">{{ m.away_pts ?? 0 }}</span>
          </div>

          <!-- Away -->
          <div class="side">
            <div class="teamcell">
              <img class="logo" :src="logoOf(m.away_team)" alt="" />
              <span class="name">{{ m.away_team?.name || 'TBD' }}</span>
            </div>
          </div>

          <!-- Meta -->
          <div class="meta">
            <div class="when">{{ mergedWhen(m.date, m.time) || 'Not set' }}</div>
            <div class="venue">{{ m.venue || 'Not set' }}</div>
            <span class="status" :class="statusClass(m)">{{ statusText(m) }}</span>
            <RouterLink class="btn small outline" :to="`/games/${m.id}`">Game Detail</RouterLink>
          </div>
        </div>
      </template>
    </section>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import api from '@/api/axios'

const GAME_DURATION_MIN = 60
const SEASON_ID = 1

const route = useRoute()
const roundNo = Number(route.params.no)

const loading = ref(false)
const matches = ref([])

function logoOf(team) { return (team && team.logo_url) ? team.logo_url : '/placeholder-team.png' }
function mergedWhen(dateStr, timeStr) {
  if (!dateStr && !timeStr) return ''
  if (dateStr && timeStr) return `${dateStr} ${timeStr.slice(0,5)}`
  return dateStr || timeStr
}
function asDate(m) {
  if (!m?.date) return null
  try {
    const hhmm = (m.time || '00:00').slice(0,5)
    return new Date(`${m.date}T${hhmm}:00`)
  } catch { return null }
}
function statusText(m) {
  if (m.status === 'canceled') return 'Canceled'
  if (m.status === 'finished') return 'Finished'
  const start = asDate(m)
  if (!start) return 'Not started'
  const end = new Date(start.getTime() + GAME_DURATION_MIN * 60000)
  const now = new Date()
  if (now < start) return 'Not started'
  if (now >= end) return 'Finished'
  return 'Ongoing'
}
function statusClass(m) {
  const s = statusText(m)
  return {
    scheduled: s === 'Not started',
    ongoing:   s === 'Ongoing',
    finished:  s === 'Finished',
    canceled:  s === 'Canceled'
  }
}

async function reload() {
  loading.value = true
  try {
    const { data } = await api.get(`/divisions/d2/rounds/${roundNo}`, {
      params: { season_id: SEASON_ID }
    })
    matches.value = Array.isArray(data) ? data : []
  } finally {
    loading.value = false
  }
}

onMounted(reload)
</script>

<style scoped>
.page{ padding:24px; }
.topbar{ display:flex; align-items:center; gap:12px; margin-bottom:12px; }
.fill{ flex:1; }

.division-block{ margin-top: 8px; }
.division-title{ font-size: 28px; font-weight: 800; color:#111; margin: 16px 0 8px; }

.btn{ height:36px; padding:0 12px; border-radius:10px; border:1px solid #e5e7eb; background:#111827; color:#fff; cursor:pointer; }
.btn.light{ background:#fff; color:#111827; }
.btn.outline{ background:#fff; color:#111827; border-color:#cbd5e1; }
.btn.small{ height:30px; padding:0 10px; border-radius:8px; }

.card{ background:#fff; border:1px solid #eee; border-radius:16px; padding:16px; }
.empty{ color:#6b7280; padding:8px 0; }

.match{
  display:grid; grid-template-columns: 1fr 160px 1fr 320px;
  gap:12px; padding:14px 16px; border:1px solid #f1f5f9; border-radius:12px;
  margin-top:10px; align-items:center; background:#fff;
}

.teamcell{ display:inline-flex; align-items:center; gap:10px; min-width:0; }
.teamcell .logo{ width:40px; height:40px; border-radius:50%; object-fit:cover; flex:0 0 40px; }
.name{ font-weight:600; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }

.center{ display:flex; align-items:center; justify-content:center; gap:8px; }
.score-num{ font-size:32px; font-weight:800; color:#0f172a; }
.dash{ color:#64748b; font-weight:800; }

.meta{ display:flex; flex-direction:column; gap:6px; align-items:flex-end; }
.meta .when{ color:#111827; font-size:14px; }
.meta .venue{ color:#6b7280; font-size:12px; }
.status{ display:inline-block; padding:2px 8px; border-radius:999px; background:#e5e7eb; font-size:12px; color:#111827; }
.status.scheduled{ background:#fef3c7; }
.status.ongoing{ background:#dbeafe; }
.status.finished{ background:#dcfce7; }
.status.canceled{ background:#fee2e2; }

@media (max-width: 980px){
  .match{ grid-template-columns: 1fr 120px 1fr; }
  .meta{ grid-column: 1 / -1; align-items:flex-start; }
}
</style>
