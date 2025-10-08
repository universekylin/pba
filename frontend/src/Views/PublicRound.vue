<template>
  <div class="page">
    <div class="topbar">
      <button class="btn light" @click="$router.back()">← Back</button>
      <h2>Round {{ roundNo }}</h2>
      <div class="fill"></div>
    </div>

    <!-- 每个分区一段：如果是 d2 只显示 D2；否则显示 Champion + D1 -->
    <div v-for="sec in sections" :key="sec.code" class="division-block">
      <h2 class="division-title">Round {{ roundNo }} • {{ sec.label }}</h2>

      <section class="card">
        <div v-if="sec.loading" class="empty">Loading…</div>

        <template v-else>
          <div v-if="sec.matches.length === 0" class="empty">No games in this round</div>

          <div v-for="m in sec.matches" :key="m.id" class="match">
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

              <!-- ✅ 关键：Champion 跳 championMatchPublic，其他跳通用 matchDetail -->
              <RouterLink
                class="btn small outline"
                :to="m._division === 'champion'
                      ? { name: 'championMatchPublic', params: { id: m.id } }
                      : { name: 'matchDetail',          params: { id: m.id } }"
              >
                Game Detail
              </RouterLink>
            </div>
          </div>
        </template>
      </section>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import api from '@/api/axios'

const GAME_DURATION_MIN = 60
const SEASON_ID = 1

const route = useRoute()
const roundNo = ref(Number(route.params.no || 1))

function computeDivs() {
  const div = String(route.params.division || '').toLowerCase()
  if (div === 'd2') return [{ code: 'd2', label: 'Division 2' }]
  return [
    { code: 'champion', label: 'Division Champion' },
    { code: 'd1',       label: 'Division 1' },
  ]
}

// 页面状态：每个分区一个 section
const sections = ref(computeDivs().map(d => ({ code: d.code, label: d.label, loading: true, matches: [] })))

function logoOf(team) { return (team && team.logo_url) ? team.logo_url : '/placeholder-team.png' }
function mergedWhen(dateStr, timeStr) {
  if (!dateStr && !timeStr) return ''
  const t = s => String(s || '').trim()
  if (t(dateStr) && t(timeStr)) return `${dateStr} ${timeStr.slice(0,5)}`
  return t(dateStr) || t(timeStr)
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
  return { scheduled: s === 'Not started', ongoing: s === 'Ongoing', finished: s === 'Finished', canceled: s === 'Canceled' }
}

// ----- 数据获取 -----
async function fetchRoundsAPI(divisionCode) {
  try {
    const { data } = await api.get(`/divisions/${divisionCode}/rounds/${roundNo.value}`, { params: { season_id: SEASON_ID } })
    if (Array.isArray(data) && data.length > 0) return data
    return null
  } catch { return null }
}

async function fetchViaScheduleFallback(divisionCode) {
  const [teamsRes, schRes] = await Promise.all([
    api.get(`/divisions/${divisionCode}/teams`, { params: { season_id: SEASON_ID } }),
    api.get(`/divisions/${divisionCode}/schedule`, { params: { season_id: SEASON_ID } })
  ])
  const listTeams = (teamsRes.data || teamsRes) ?? []
  const teamMap = new Map(listTeams.map(t => [t.id, t]))
  const regular = (schRes?.data?.regular) ?? schRes?.regular ?? []
  const r = regular.find(x => Number(x.round_no) === roundNo.value)
  if (!r) return []
  return r.matches.map(m => ({
    id: m.id,
    date: (m.scheduled_at || '').split(' ')[0] || null,
    time: (m.scheduled_at || '').split(' ')[1] || null,
    status: 'scheduled',
    venue: m.venue || null,
    home_team: teamMap.get(m.home_team_id) || null,
    away_team: teamMap.get(m.away_team_id) || null,
  }))
}

async function hydrateScoreFor(m) {
  try {
    const res = await api.get(`/matches/${m.id}/lineup`)
    const payload = res?.data || res
    const sum = arr => (Array.isArray(arr) ? arr.reduce((a,b)=> a + Number(b?.points || 0), 0) : 0)
    const sumF = arr => (Array.isArray(arr) ? arr.reduce((a,b)=> a + Number(b?.fouls  || 0), 0) : 0)
    m.home_pts = sum(payload?.home?.players)
    m.away_pts = sum(payload?.away?.players)
    m.home_fouls = sumF(payload?.home?.players)
    m.away_fouls = sumF(payload?.away?.players)
  } catch {
    m.home_pts = 0; m.away_pts = 0; m.home_fouls = 0; m.away_fouls = 0
  }
}

function sortMatchesInPlace(list) {
  list.sort((a,b)=>{
    const da = asDate(a), db = asDate(b)
    if (da && db) return da.getTime() - db.getTime()
    if (da && !db) return -1
    if (!da && db) return  1
    return (a.id || 0) - (b.id || 0)
  })
}

async function loadDivision(sec) {
  sec.loading = true
  try {
    const data = (await fetchRoundsAPI(sec.code)) ?? (await fetchViaScheduleFallback(sec.code)) ?? []
    // ✅ 给每条比赛打上来源分区，供路由判定
    sec.matches = data.map(m => ({ ...m, _division: sec.code }))
    await Promise.all(sec.matches.map(hydrateScoreFor))
    sortMatchesInPlace(sec.matches)
  } finally {
    sec.loading = false
  }
}

async function reloadAll() {
  const divs = computeDivs()
  sections.value = divs.map(d => ({ code: d.code, label: d.label, loading: true, matches: [] }))
  await Promise.all(sections.value.map(loadDivision))
}

onMounted(reloadAll)

watch(
  () => [route.params.division, route.params.no],
  () => { roundNo.value = Number(route.params.no || 1); reloadAll() }
)
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
