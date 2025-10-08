<!-- src/views/admin/ChampionTeamSchedule.vue -->
<template>
  <div class="page">
    <!-- 顶部：返回 + 队徽 -->
    <div class="topbar">
      <router-link class="btn light" to="/admin-panel">← Admin Home</router-link>
      <div class="spacer"></div>
      <div v-if="team" class="team-chip">
        <img v-if="team.logo_url" :src="team.logo_url" alt="Team Logo" />
        <span class="name">{{ team.name }}</span>
      </div>
    </div>

    <!-- 标题 -->
    <div class="titlebar">
      <h2 class="title">Champion Team Schedule (Rounds 1–11)</h2>
      <span class="chip division">Champion</span>
    </div>

    <!-- 常规赛（可能没有，保留） -->
    <div class="card" v-if="regularMatches.length">
      <div class="match-row" v-for="m in regularMatches" :key="'reg-' + m.id">
        <div class="team left">
          <img class="logo" :src="teamLogo(m.home_team?.logo_url)" alt="home" />
          <div class="meta"><div class="name">{{ m.home_team?.name || 'TBD' }}</div></div>
        </div>

        <div class="center">
          <div class="score">
            <span class="num">{{ safeNum(m.home_score) }}</span>
            <span class="dash">-</span>
            <span class="num">{{ safeNum(m.away_score) }}</span>
          </div>
          <div class="sub">R{{ m.round_no ?? '-' }}</div>
        </div>

        <div class="team right">
          <img class="logo" :src="teamLogo(m.away_team?.logo_url)" alt="away" />
          <div class="meta"><div class="name">{{ m.away_team?.name || 'TBD' }}</div></div>
        </div>

        <!-- 右侧信息（只保留日期/时间/场地 + 按钮；不显示状态） -->
        <div class="info">
          <div class="dt">
            <div class="date-time">
              <span class="date">{{ m.date || 'TBD' }}</span>
              <span class="time">{{ m.time || 'TBD' }}</span>
            </div>
            <div class="place">
              <template v-if="m.court_no">Court {{ m.court_no }} · </template>
              {{ m.venue || 'Not set' }}
            </div>
          </div>
          <RouterLink class="btn sm ghost" :to="detailRoute(m)">game detail</RouterLink>
        </div>
      </div>
    </div>
    <div class="empty" v-else-if="!loading">No regular-season games in this range</div>

    <!-- 季后赛 -->
    <h3 class="section-title">Playoffs</h3>
    <div class="card" v-if="playoffMatches.length">
      <div class="match-row" v-for="m in playoffMatches" :key="'po-' + m.id">
        <div class="team left">
          <img class="logo" :src="teamLogo(m.home_team?.logo_url)" alt="home" />
          <div class="meta"><div class="name">{{ m.home_team?.name || 'TBD' }}</div></div>
        </div>

        <div class="center">
          <div class="score">
            <span class="num">{{ safeNum(m.home_score) }}</span>
            <span class="dash">-</span>
            <span class="num">{{ safeNum(m.away_score) }}</span>
          </div>
          <div class="sub">PO</div>
        </div>

        <div class="team right">
          <img class="logo" :src="teamLogo(m.away_team?.logo_url)" alt="away" />
          <div class="meta"><div class="name">{{ m.away_team?.name || 'TBD' }}</div></div>
        </div>

        <!-- 右侧信息（只保留日期/时间/场地 + 按钮；不显示状态） -->
        <div class="info">
          <div class="dt">
            <div class="date-time">
              <span class="date">{{ m.date || 'TBD' }}</span>
              <span class="time">{{ m.time || 'TBD' }}</span>
            </div>
            <div class="place">
              <template v-if="m.court_no">Court {{ m.court_no }} · </template>
              {{ m.venue || 'Not set' }}
            </div>
          </div>
          <RouterLink class="btn sm ghost" :to="detailRoute(m)">game detail</RouterLink>
        </div>
      </div>
    </div>
    <div class="empty" v-else-if="!loading">No playoff games yet</div>

    <div class="loading" v-if="loading">Loading…</div>
  </div>
</template>

<script setup>
import { onMounted, onBeforeUnmount, ref, computed } from 'vue'
import { useRoute } from 'vue-router'
import { fetchTeamSchedule } from '@/api/schedule'

const route = useRoute()
const teamId = Number(route.params.id)
const loading = ref(false)
const team = ref(null)
const matches = ref([])

let timer = null
let paused = false

const safeNum = (v) => (Number.isFinite(+v) ? +v : 0)
const teamLogo = (url) => url || '/placeholder-team.png'

// —— 分组：常规赛 / 季后赛
const normStage = (s) => String(s || '').trim().toLowerCase()
const regularMatches = computed(() =>
  (matches.value || []).filter(m => {
    const st = normStage(m.stage)
    return st === '' || st === 'regular' || st === 'league' || st === 'season'
  })
)
const playoffMatches = computed(() =>
  (matches.value || []).filter(m => {
    const st = normStage(m.stage)
    return st === 'playoff' || st === 'playoffs' || st === 'po'
  })
)

// Champion 详情（可编辑）
const detailRoute = (m) => ({ name: 'championMatchDetail', params: { id: m.id } })

// 拉取 champion 赛程（这里保留 use_raw 也无妨；我们页面不再显示 status）
async function load() {
  if (paused) return
  loading.value = true
  try {
    const from = Number(route.query.from || 1)
    const to = Number(route.query.to || 11)
    const data = await fetchTeamSchedule(teamId, from, to, 'champion', { useRaw: true })
    team.value = data?.team || null
    matches.value = Array.isArray(data?.matches) ? data.matches : []
  } catch (e) {
    console.error('Failed to load champion schedule', e)
  } finally {
    loading.value = false
  }
}

function handleVisibility() {
  paused = document.visibilityState === 'hidden'
  if (!paused) load()
}

onMounted(async () => {
  await load()
  document.addEventListener('visibilitychange', handleVisibility)
  timer = window.setInterval(load, 8000)
})
onBeforeUnmount(() => {
  document.removeEventListener('visibilitychange', handleVisibility)
  if (timer) window.clearInterval(timer)
})
</script>

<style scoped>
/* 与 TeamSchedule 风格一致 */
html, body, #app { overflow-x: hidden; }
.page { padding: 20px; }
.topbar{ display:flex; align-items:center; gap:12px; margin-bottom:14px; }
.btn{ height:34px; padding:0 12px; border-radius:10px; border:1px solid #e5e7eb; background:#111827; color:#fff; cursor:pointer; text-decoration:none; display:inline-flex; align-items:center; justify-content:center; }
.btn.light{ background:#fff; color:#111827; }
.btn.sm{ height:28px; font-size:12px; font-weight:700; border-radius:9999px; }
.btn.ghost{ background:#0f172a; border-color:#0f172a; color:#fff; }
.spacer{ flex:1; }
.team-chip{ display:flex; align-items:center; gap:10px; padding:6px 10px; border:1px solid #e5e7eb; border-radius:9999px; background:#fff; }
.team-chip img{ width:28px; height:28px; border-radius:50%; object-fit:cover; }
.team-chip .name{ font-weight:800; }

.titlebar{ display:grid; grid-template-columns: 1fr auto; align-items:center; margin: 4px 0 12px; }
.title{ font-size:22px; font-weight:900; }
.chip{ font-size:12px; font-weight:900; padding:4px 10px; border-radius:9999px; border:1px solid #e5e7eb; background:#f8fafc; color:#334155; white-space:nowrap; }
.chip.division{ background:#eef2ff; border-color:#e0e7ff; color:#3730a3; }

.card{ background:transparent; border:0; border-radius:0; overflow:visible; }
.match-row{
  display:grid;
  grid-template-columns: 1fr 160px 1fr 220px;
  gap:8px; align-items:center; padding:16px 18px;
  border:1px solid #eef2f7; border-radius:16px; background:#fff;
  transition: box-shadow .18s ease, transform .18s ease;
}
.match-row + .match-row{ margin-top:10px; }
.match-row:hover{ box-shadow:0 8px 24px rgba(15,23,42,.06); transform: translateY(-1px); }

.team{ display:flex; align-items:center; gap:12px; min-width:0; }
.team.right{ justify-self: end; }
.logo{ width:40px; height:40px; border-radius:50%; object-fit:cover; background:#f0f2f5; border:1px solid #e5e7eb; }
.meta .name{ font-weight:800; color:#0f172a; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }

.center{ text-align:center; }
.score{ font-size:34px; font-weight:900; color:#0f172a; line-height:1; }
.score .dash{ padding:0 8px; color:#64748b; }
.center .sub{ font-size:12px; color:#64748b; margin-top:4px; }

.info{ display:flex; flex-direction:column; align-items:flex-end; gap:8px; }
.date-time{ display:flex; gap:8px; color:#0f172a; font-weight:700; font-variant-numeric: tabular-nums; }
.date-time .date, .date-time .time{ font-size:13px; }
.place{ color:#94a3b8; font-size:12px; text-align:right; }

.empty{ padding:14px; color:#6b7280; }

@media (max-width: 1100px){
  .match-row{ grid-template-columns: 1fr 140px 1fr 200px; }
  .score{ font-size:30px; }
}
@media (max-width: 940px){
  .match-row{ grid-template-columns: 1fr 120px 1fr 180px; }
  .score{ font-size:28px; }
}
@media (max-width: 800px){
  .match-row{ grid-template-columns: 1fr 110px 1fr; }
  .info{ grid-column: 1 / -1; align-items:flex-start; margin-top:6px; }
}
</style>
