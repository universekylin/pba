<template>
  <div class="page">
    <!-- 顶部：球队信息 -->
    <div class="topbar">
      <div class="spacer"></div>
      <div v-if="team" class="team-chip">
        <img v-if="team.logo_url" :src="team.logo_url" alt="Team Logo" />
        <span class="name">{{ team.name }}</span>
      </div>
    </div>

    <!-- 标题 + Division 徽章 -->
    <div class="titlebar">
      <h2 class="title">Team Schedule (Rounds 1–11)</h2>
      <span class="chip division">{{ divisionLabel }}</span>
    </div>

    <!-- 常规赛 -->
    <div class="card" v-if="regularMatches.length">
      <div class="match-row" v-for="m in regularMatches" :key="'reg-' + m.id">
        <!-- 左：主队 -->
        <div class="team left">
          <img class="logo" :src="teamLogo(m.home_team?.logo_url)" alt="home" />
          <div class="meta"><div class="name">{{ m.home_team?.name || 'TBD' }}</div></div>
        </div>

        <!-- 中：比分 + 回合 -->
        <div class="center">
          <div class="score">
            <span class="num">{{ safeNum(m.home_score) }}</span>
            <span class="dash">-</span>
            <span class="num">{{ safeNum(m.away_score) }}</span>
          </div>
          <div class="sub">R{{ m.round_no ?? '-' }}</div>
        </div>

        <!-- 右：客队 -->
        <div class="team right">
          <img class="logo" :src="teamLogo(m.away_team?.logo_url)" alt="away" />
          <div class="meta"><div class="name">{{ m.away_team?.name || 'TBD' }}</div></div>
        </div>

        <!-- 信息（时间/场地 + 比赛详情按钮） -->
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
          <div class="status">
            <RouterLink class="btn detail" :to="detailRoute(m)">game detail</RouterLink>
          </div>
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
          <div class="status">
            <RouterLink class="btn detail" :to="detailRoute(m)">game detail</RouterLink>
          </div>
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
const apiDivisionCode = ref(null)

let timer = null
let paused = false

const safeNum = (v) => (Number.isFinite(+v) ? +v : 0)
const teamLogo = (url) => url || '/placeholder-team.png'

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

const normDiv = (x) => {
  const v = String(x || '').trim().toLowerCase()
  if (['d1','division1','1'].includes(v)) return 'd1'
  if (['d2','division2','2'].includes(v)) return 'd2'
  if (['champion','champ','c','championship'].includes(v)) return 'champion'
  return ''
}
const divisionCode = computed(() => {
  const fromQuery = normDiv(route.query.division)
  if (fromQuery) return fromQuery
  if (apiDivisionCode.value) return apiDivisionCode.value
  return 'd1'
})
const divisionLabel = computed(() => ({
  d1: 'Division 1',
  d2: 'Division 2',
  champion: 'Champion'
}[divisionCode.value] || divisionCode.value.toUpperCase()))

// 是否处在 admin 的赛程别名页（该组件同时服务公开和 admin 别名）
const isAdminView = computed(() => route.name === 'teamScheduleAdminAlias')

// “比赛详情”目标路由 —— ✅ 附带 division，Champion 在 admin 别名页跳到管理端详情
const detailRoute = (m) => {
  const div = divisionCode.value
  if (isAdminView.value && div === 'champion') {
    return `/admin-panel/matches/${m.id}`
  }
  return `/${div}/matches/${m.id}?division=${div}`
  // 如果你暂时不想用带 division 的路径，也可以用：
  // return `/matches/${m.id}?division=${div}`
}

// 拉取
async function load() {
  if (paused) return
  loading.value = true
  try {
    const from = Number(route.query.from || 1)
    const to = Number(route.query.to || 11)
    const division = route.query.division || undefined
    const data = await fetchTeamSchedule(teamId, from, to, division)
    team.value = data?.team || null
    apiDivisionCode.value = normDiv(data?.division?.code)
    matches.value = (Array.isArray(data?.matches) ? data.matches : []).map(m => ({
      ...m,
      court_no: m.court_no ?? null,
      venue: m.venue ?? null
    }))
  } catch (e) {
    console.error('Failed to load schedule', e)
  } finally {
    loading.value = false
  }
}

// 页面可见性控制
function handleVisibility() {
  paused = document.visibilityState === 'hidden'
  if (!paused) load()
}

onMounted(async () => {
  await load()
  document.addEventListener('visibilitychange', handleVisibility)
  timer = setInterval(load, 8000)
})
onBeforeUnmount(() => {
  document.removeEventListener('visibilitychange', handleVisibility)
  if (timer) clearInterval(timer)
})
</script>

<style scoped>
/* 防横向滚动 */
html, body, #app { overflow-x: hidden; }
.page { padding: 20px; }

/* 顶部条 */
.topbar{ display:flex; align-items:center; gap:12px; margin-bottom:14px; }
.btn{
  height:34px; padding:0 12px; border-radius:10px; border:1px solid #e5e7eb;
  background:#111827; color:#fff; cursor:pointer; text-decoration:none;
  display:inline-flex; align-items:center; justify-content:center;
}
.btn.light{ background:#fff; color:#111827; }
.spacer{ flex:1; }
.team-chip{
  display:flex; align-items:center; gap:10px; padding:6px 10px; border:1px solid #e5e7eb;
  border-radius:9999px; background:#fff;
}
.team-chip img{ width:28px; height:28px; border-radius:50%; object-fit:cover; }
.team-chip .name{ font-weight:800; }

/* 标题行：左标题右徽章 */
.titlebar{ display:grid; grid-template-columns: 1fr auto; align-items:center; margin: 4px 0 12px; }
.title{ font-size:22px; font-weight:900; }

/* 徽章 */
.chip{ font-size:12px; font-weight:900; padding:4px 10px; border-radius:9999px; border:1px solid #e5e7eb; background:#f8fafc; color:#334155; white-space:nowrap; }
.chip.division{ background:#eef2ff; border-color:#e0e7ff; color:#3730a3; }

/* 列表容器 */
.card{ background:transparent; border:0; border-radius:0; overflow:visible; }

/* 单行 */
.match-row{
  display:grid;
  grid-template-columns: 1fr 160px 1fr 220px;
  gap:8px; align-items:center; padding:16px 18px;
  border:1px solid #eef2f7; border-radius:16px; background:#fff;
  transition: box-shadow .18s ease, transform .18s ease;
}
.match-row + .match-row{ margin-top:10px; }
.match-row:hover{ box-shadow:0 8px 24px rgba(15,23,42,.06); transform: translateY(-1px); }

/* 球队块 */
.team{ display:flex; align-items:center; gap:12px; min-width:0; }
.team.right{ justify-self: end; }
.logo{ width:40px; height:40px; border-radius:50%; object-fit:cover; background:#f0f2f5; border:1px solid #e5e7eb; }
.meta .name{ font-weight:800; color:#0f172a; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }

/* 中央比分 */
.center{ text-align:center; }
.score{ font-size:34px; font-weight:900; color:#0f172a; line-height:1; }
.score .dash{ padding:0 8px; color:#64748b; }
.center .sub{ font-size:12px; color:#64748b; margin-top:4px; }

/* 右侧信息块 */
.info{ display:flex; flex-direction:column; align-items:flex-end; gap:6px; }
.date-time{ display:flex; gap:8px; color:#0f172a; font-weight:700; font-variant-numeric: tabular-nums; }
.date-time .date, .date-time .time{ font-size:13px; }
.place{ color:#94a3b8; font-size:12px; text-align:right; }

/* 按钮 */
.btn.detail{ background:#0f172a; border-color:#0f172a; color:#fff; padding:0 12px; height:28px; border-radius:9999px; font-size:12px; font-weight:700; }
.btn.detail:hover{ opacity:.95; }

.empty{ padding:14px; color:#6b7280; }
.loading{ padding:14px; }

/* 响应式 */
@media (max-width: 1100px){ .match-row{ grid-template-columns: 1fr 140px 1fr 200px; } .score{ font-size:30px; } }
@media (max-width: 940px){ .match-row{ grid-template-columns: 1fr 120px 1fr 180px; } .score{ font-size:28px; } }
@media (max-width: 800px){
  .match-row{ grid-template-columns: 1fr 110px 1fr; }
  .info{ grid-column: 1 / -1; align-items:flex-start; margin-top:6px; }
}
</style>
