<template>
  <div class="page">
    <!-- Head -->
    <div class="card head" v-if="match">
      <div class="row-1">
        <div class="score big">{{ safeNum(homeScore) }}</div>

        <div class="center-pack">
          <div class="team-mini">
            <img class="logo" :src="teamLogo(homeTeam.team?.logo_url)" alt="home logo" />
            <div class="tname">{{ homeName }}</div>
          </div>

          <span class="chip" :class="statusClass(statusFinalized)">
            {{ statusText(statusFinalized) }}
          </span>

          <div class="team-mini">
            <img class="logo" :src="teamLogo(awayTeam.team?.logo_url)" alt="away logo" />
            <div class="tname">{{ awayName }}</div>
          </div>
        </div>

        <div class="score big">{{ safeNum(awayScore) }}</div>
      </div>

      <div class="row-2">
        <div class="info">
          <span class="i">🗓</span>
          <span>{{ prettyDateTime(match.date, match.time) }}</span>
        </div>
        <div class="info">
          <span class="i">📍</span>
          <span>{{ venueText }}</span>
        </div>
      </div>
    </div>

    <!-- tabs -->
    <div class="tabs" v-if="match">
      <button class="tab" :class="{ active: side === 'home' }" @click="side = 'home'">{{ homeName }}</button>
      <button class="tab" :class="{ active: side === 'away' }" @click="side = 'away'">{{ awayName }}</button>
    </div>

    <!-- Player stats (read-only) -->
    <div class="card">
      <div class="table-wrap" v-if="currentPlayers.length">
        <table class="stat-table">
          <thead>
            <tr>
              <th class="num-col">#</th>
              <th class="name-col">Players</th>

              <!-- ✅ Champion 显示完整技术统计 -->
              <template v-if="isChampion">
                <th>PTS</th>
                <th>REB</th>
                <th>STL</th>
                <th>AST</th>
                <th>BLK</th>
                <th>Fouls</th>
                <th>1PT</th>
                <th>2PT</th>
                <th>3PT</th>
              </template>

              <!-- 其他分区：精简 -->
              <template v-else>
                <th>PTS</th>
                <th>Fouls</th>
                <th>1PT</th>
                <th>2PT</th>
                <th>3PT</th>
              </template>
            </tr>
          </thead>
          <tbody>
            <tr v-for="p in currentPlayers" :key="p.id">
              <td class="num-col">{{ p.number ?? '—' }}</td>
              <td class="name-col">{{ p.name || '—' }}</td>

              <template v-if="isChampion">
                <td class="val">{{ safeNum(p.points) }}</td>
                <td class="val">{{ safeNum(getField(p, ['reb','rebounds','rebound'])) }}</td>
                <td class="val">{{ safeNum(getField(p, ['stl','steals'])) }}</td>
                <td class="val">{{ safeNum(getField(p, ['ast','assists'])) }}</td>
                <td class="val">{{ safeNum(getField(p, ['blk','blocks'])) }}</td>
                <td class="val">{{ safeNum(getField(p, ['fouls','pf'])) }}</td>
                <td class="val">{{ col1(p) }}</td>
                <td class="val">{{ col2(p) }}</td>
                <td class="val">{{ col3(p) }}</td>
              </template>

              <template v-else>
                <td class="val">{{ safeNum(p.points) }}</td>
                <td class="val">{{ safeNum(getField(p, ['fouls','pf'])) }}</td>
                <td class="val">{{ col1(p) }}</td>
                <td class="val">{{ col2(p) }}</td>
                <td class="val">{{ col3(p) }}</td>
              </template>
            </tr>
          </tbody>
        </table>
      </div>
      <div class="empty" v-else>No player stats yet.</div>
    </div>

    <div class="loading" v-if="loading">Loading…</div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '@/api/axios'

const route = useRoute()
const router = useRouter()
const id = Number(route.params.id)

const loading = ref(false)
const match = ref(null)
const side = ref('home')

/* ---------- helpers ---------- */
const safeNum = (v) => (Number.isFinite(+v) ? +v : 0)

// === 静态文件根路径（后端 3001 端口） ===
const FILE_BASE =
  import.meta.env.VITE_FILE_BASE
  || (import.meta.env.VITE_API_BASE ? import.meta.env.VITE_API_BASE.replace(/\/api\/?$/,'') : '')
  || 'http://localhost:3001'

// 处理球队 Logo
const teamLogo = (url) => {
  if (!url) return '/placeholder-team.png'
  const u = String(url)
  if (/^https?:\/\//i.test(u)) return u
  if (u.startsWith('/')) return `${FILE_BASE}${u}`
  return `${FILE_BASE}/static/team-logos/${u}`
}

// 顶部状态文本和样式
function statusText(s) {
  const v = String(s || '').toLowerCase()
  if (['finished','final','done'].includes(v)) return 'FINAL'
  if (['ongoing','live'].includes(v)) return 'LIVE'
  return 'UPCOMING'
}
function statusClass(s) {
  const v = String(s || '').toLowerCase()
  if (['finished','final','done'].includes(v)) return 'finished'
  if (['ongoing','live'].includes(v)) return 'ongoing'
  if (['upcoming','scheduled','not started',''].includes(v)) return 'scheduled'
  return 'unknown'
}

// 日期+时间格式化
function prettyDateTime(d, t, locale = 'en-AU') {
  if (!d && !t) return 'TBD'
  try {
    let dt
    if (d && t) dt = new Date(`${d}T${t}`)
    else if (d) dt = new Date(d)
    else dt = new Date(`1970-01-01T${t}`)
    return dt.toLocaleString(locale, {
      weekday: 'short', day: '2-digit', month: 'short', year: 'numeric',
      hour: '2-digit', minute: '2-digit', hour12: true,
    })
  } catch {
    return [d, t].filter(Boolean).join(' ')
  }
}

const venueText = computed(() => {
  const c = match.value?.court_no
  const v = match.value?.venue
  if (v && c) return `${v} / Court ${c}`
  if (v) return v
  if (c) return `Court ${c}`
  return 'Not set'
})

/* ---------- division 识别 ---------- */
const normDiv = (x) => {
  const v = String(x || '').trim().toLowerCase()
  if (['d1','division1','1'].includes(v)) return 'd1'
  if (['d2','division2','2'].includes(v)) return 'd2'
  if (['champion','champ','c','championship'].includes(v)) return 'champion'
  return ''
}

const divisionFromRoute = computed(() =>
  normDiv(route.params.division || route.query.division)
)

const divisionFromAPI = computed(() =>
  normDiv(match.value?.division_code || match.value?.division)
)

const division = computed(() => divisionFromRoute.value || divisionFromAPI.value || '')

const isChampion = computed(() => division.value === 'champion')

/* ---------- team/players ---------- */
const homeTeam = computed(() => match.value?.home || {})
const awayTeam = computed(() => match.value?.away || {})
const homeName = computed(() => (homeTeam.value?.team?.name ?? '').trim() || 'Home')
const awayName = computed(() => (awayTeam.value?.team?.name ?? '').trim() || 'Away')

const homeScore = computed(() => {
  const s = homeTeam.value?.score
  if (Number.isFinite(+s)) return +s
  return (homeTeam.value?.players || []).reduce((a, b) => a + safeNum(b.points), 0)
})
const awayScore = computed(() => {
  const s = awayTeam.value?.score
  if (Number.isFinite(+s)) return +s
  return (awayTeam.value?.players || []).reduce((a, b) => a + safeNum(b.points), 0)
})

const currentPlayers = computed(() => {
  const arr = (side.value === 'home' ? homeTeam.value?.players : awayTeam.value?.players) || []
  return [...arr].sort((a, b) => safeNum(a.number) - safeNum(b.number))
})

// 字段解析
const getField = (obj, keys = []) => { 
  for (const k of keys) if (obj[k] !== undefined && obj[k] !== null) return obj[k]
  return 0
}
const col1 = (p) => safeNum(getField(p, ['one_pt_made','one_points','one_pointers','ones','p1']))
const col2 = (p) => safeNum(getField(p, ['two_pt_made','two_points','two_pointers','twos','p2']))
const col3 = (p) => safeNum(getField(p, ['three_pt_made','three_points','three_pointers','threes','p3']))

/* ---------- 比赛状态逻辑 ---------- */
const ONGOING_WINDOW_MIN = 60
function parseStartLocal(d, t) {
  try {
    if (d && t) return new Date(`${d}T${t}`)
    if (d) return new Date(d)
    if (t) return new Date(`1970-01-01T${t}`)
  } catch {}
  return null
}
const statusFinalized = computed(() => {
  const raw = String(match.value?.status || '').trim().toLowerCase()
  const known = ['finished','final','done','ongoing','live','scheduled','upcoming','not started']
  if (known.includes(raw)) return raw
  const start = parseStartLocal(match.value?.date, match.value?.time)
  if (!start) {
    const total = safeNum(homeScore.value) + safeNum(awayScore.value)
    return total > 0 ? 'finished' : 'upcoming'
  }
  const now = new Date()
  const diffMs = now - start
  if (diffMs < 0) return 'upcoming'
  if (diffMs <= ONGOING_WINDOW_MIN * 60 * 1000) return 'ongoing'
  return 'finished'
})

/* ---------- fetch ---------- */
async function load() {
  loading.value = true
  try {
    const data = await api.get(`/matches/${id}`)

    const m = data?.match || {}

    // 提取 Team 对象
    const pickTeamObj = (side) =>
      (data?.[side]?.team) ||
      (m?.[`${side}_team`]) ||
      (data?.[`${side}_team`]) || {}

    const homeObj = pickTeamObj('home')
    const awayObj = pickTeamObj('away')

    const allPlayers = Array.isArray(data?.players) ? data.players : []
    const byTeam = (tid) => allPlayers.filter(p => p.team_id === tid)

    const homePlayers = Array.isArray(data?.home?.players) ? data.home.players :
                        byTeam(homeObj?.id || m?.home_team_id || data?.home_team_id || 0)
    const awayPlayers = Array.isArray(data?.away?.players) ? data.away.players :
                        byTeam(awayObj?.id || m?.away_team_id || data?.away_team_id || 0)

    const firstTeamId = (arr) => (arr && arr.length ? arr[0].team_id : null)
    const homeId = homeObj?.id ?? m?.home_team_id ?? data?.home_team_id ?? firstTeamId(homePlayers)
    const awayId = awayObj?.id ?? m?.away_team_id ?? data?.away_team_id ?? firstTeamId(awayPlayers)

    // 如果接口里包含 division_code，记录下来
    const division_code = m?.division_code || data?.division_code || data?.division

    // 补取球队信息（兜底）
    async function fetchTeamHard(id) {
      if (!id) return null
      try {
        const res = await api.get(`/teams/${id}`)
        const t = res?.data ?? res
        return t ? { id: t.id, name: t.name, logo_url: t.logo_url } : null
      } catch (e) {
        console.warn('fetch /teams failed', id, e)
        return null
      }
    }
    const [homeInfo, awayInfo] = await Promise.all([fetchTeamHard(homeId), fetchTeamHard(awayId)])

    const sNum = (v) => (Number.isFinite(+v) ? +v : 0)
    const sumPts = (arr) => (arr || []).reduce((a, b) => a + sNum(b.points ?? b.pts), 0)

    match.value = {
      id: m.id ?? data.id,
      division_code,                          // ✅ 保留给前端识别
      status: m.status ?? data.status ?? '',
      date: m.date ?? data.date ?? null,
      time: m.time ?? data.time ?? null,
      court_no: m.court_no ?? m.court ?? data.court_no ?? data.court ?? null,
      venue: m.venue ?? data.venue ?? null,

      home: {
        team: {
          id: homeId || null,
          name: (homeInfo?.name ?? homeObj?.name ?? '').trim() || 'Home',
          logo_url: homeInfo?.logo_url ?? homeObj?.logo_url ?? null,
        },
        score: sumPts(homePlayers),
        players: homePlayers,
      },

      away: {
        team: {
          id: awayId || null,
          name: (awayInfo?.name ?? awayObj?.name ?? '').trim() || 'Away',
          logo_url: awayInfo?.logo_url ?? awayObj?.logo_url ?? null,
        },
        score: sumPts(awayPlayers),
        players: awayPlayers,
      },
    }

    // 若 URL 没带 division，但是接口给到了，做一次无刷新规范化（可选）
    if (!divisionFromRoute.value && normDiv(division_code)) {
      router.replace({ path: `/${normDiv(division_code)}/matches/${id}`, query: { division: normDiv(division_code) } })
    }
  } catch (e) {
    console.error('Failed to load match detail', e)
    alert('Match detail API not found.')
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>

<style scoped>
.page { padding: 20px; }
.card { background: #fff; border: 1px solid #eef2f7; border-radius: 16px; padding: 16px; margin-bottom: 14px; }

.chip { font-size: 12px; font-weight: 800; padding: 4px 10px; border-radius: 9999px; border: 1px solid #e5e7eb; background: #f8fafc; color: #334155; letter-spacing: 0.2px; }
.chip.finished { background: #ecfdf5; border-color: #bbf7d0; color: #065f46; }
.chip.ongoing { background: #e6f4ff; border-color: #bee3ff; color: #0c4a6e; }
.chip.scheduled { background: #fff7ed; border-color: #ffedd5; color: #9a3412; }
.chip.unknown { background: #f1f5f9; color: #475569; }

/* 头部布局 */
.head .row-1 { display: grid; grid-template-columns: 1fr auto 1fr; align-items: center; gap: 16px; }
.score.big { font-size: 48px; font-weight: 900; color: #0f172a; line-height: 1; text-align: center; }
.center-pack { display: flex; align-items: center; gap: 18px; }

/* LOGO */
.team-mini { text-align: center; min-width: 112px; }
.team-mini .logo { width: 96px; height: 96px; aspect-ratio: 1/1; display: block; border-radius: 50%; border: 1px solid #e5e7eb; object-fit: cover; background: #f3f4f6; }
.team-mini .tname { margin-top: 8px; font-weight: 900; color: #0f172a; white-space: nowrap; }

/* 时间 & 场地 */
.head .row-2 { display: flex; gap: 18px; flex-wrap: wrap; margin-top: 12px; color: #0f172a; font-weight: 700; }
.info { display: flex; align-items: center; gap: 8px; }
.i { opacity: 0.75; }

/* Tabs */
.tabs { display: flex; gap: 8px; margin: 8px 0 12px; }
.tab { flex: 1; height: 38px; border-radius: 9999px; border: 1px solid #e5e7eb; background: #f8fafc; font-weight: 800; cursor: pointer; }
.tab.active { background: #1e3a8a; color: #fff; border-color: #1e3a8a; }

/* 表格 */
.table-wrap { overflow-x: auto; }
.stat-table { width: 100%; border-collapse: separate; border-spacing: 0; }
.stat-table thead th { text-align: left; font-size: 12px; color: #64748b; font-weight: 900; padding: 10px 12px; border-bottom: 1px solid #eef2f7; background: #f8fafc; }
.stat-table tbody td { padding: 12px; border-bottom: 1px solid #f1f5f9; font-weight: 700; color: #0f172a; }
.stat-table tbody tr:hover { background: #fafafa; }
.num-col { width: 68px; text-align: center; }
.name-col { min-width: 220px; }
.val { text-align: center; }

/* 响应式 */
@media (max-width: 960px) {
  .score.big { font-size: 36px; }
  .team-mini .logo { width: 80px; height: 80px; }
}
</style>
