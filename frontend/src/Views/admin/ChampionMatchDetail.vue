<!-- src/views/admin/ChampionMatchDetail.vue -->
<template>
  <div class="page">
    <!-- 头部，与 MatchDetail 一致 -->
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
        <div class="info"><span class="i">🗓</span><span>{{ prettyDateTime(match.date, match.time) }}</span></div>
        <div class="info"><span class="i">📍</span><span>{{ venueText }}</span></div>
        <div class="spacer"></div>
        <button class="btn light" @click="reload" :disabled="loading">{{ loading ? 'Loading…' : 'Refresh' }}</button>
      </div>
    </div>

    <!-- tabs -->
    <div class="tabs" v-if="match">
      <button class="tab" :class="{ active: side === 'home' }" @click="side = 'home'">{{ homeName }}</button>
      <button class="tab" :class="{ active: side === 'away' }" @click="side = 'away'">{{ awayName }}</button>
    </div>

    <!-- 表格：显示=MatchDetail；但单元格可点即编辑，自动保存 -->
    <div class="card">
      <div class="table-wrap" v-if="currentRows.length">
        <table class="stat-table">
          <thead>
            <tr>
              <th class="num-col">#</th>
              <th class="name-col">Player</th>
              <th>PTS</th>
              <th>REB</th>
              <th>STL</th>
              <th>AST</th>
              <th>BLK</th>
              <th>Fouls</th>
              <th>1PT</th>
              <th>2PT</th>
              <th>3PT</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="r in currentRows" :key="r._key">
              <!-- 号码 -->
              <td class="num-col">
                <span v-if="!isEditing(r,'number')" class="cell" @click="startEdit(r,'number')">{{ r.number ?? '—' }}</span>
                <input v-else ref="editInput" class="cell-input center" v-model="r.number"
                       @keydown.enter="commitEdit(r,'number')" @blur="commitEdit(r,'number')" />
              </td>

              <!-- 姓名 -->
              <td class="name-col">
                <span v-if="!isEditing(r,'name')" class="cell" @click="startEdit(r,'name')">{{ r.name || '—' }}</span>
                <input v-else ref="editInput" class="cell-input" v-model="r.name"
                       @keydown.enter="commitEdit(r,'name')" @blur="commitEdit(r,'name')" />
              </td>

              <!-- 数值列 -->
              <td class="val">
                <span v-if="!isEditing(r,'pts')" class="cell" @click="startEdit(r,'pts')">{{ safeNum(r.pts) }}</span>
                <input v-else ref="editInput" type="number" class="cell-input center" v-model.number="r.pts"
                       @keydown.enter="commitEdit(r,'pts')" @blur="commitEdit(r,'pts')" />
              </td>
              <td class="val">
                <span v-if="!isEditing(r,'reb')" class="cell" @click="startEdit(r,'reb')">{{ safeNum(r.reb) }}</span>
                <input v-else ref="editInput" type="number" class="cell-input center" v-model.number="r.reb"
                       @keydown.enter="commitEdit(r,'reb')" @blur="commitEdit(r,'reb')" />
              </td>
              <td class="val">
                <span v-if="!isEditing(r,'stl')" class="cell" @click="startEdit(r,'stl')">{{ safeNum(r.stl) }}</span>
                <input v-else ref="editInput" type="number" class="cell-input center" v-model.number="r.stl"
                       @keydown.enter="commitEdit(r,'stl')" @blur="commitEdit(r,'stl')" />
              </td>
              <td class="val">
                <span v-if="!isEditing(r,'ast')" class="cell" @click="startEdit(r,'ast')">{{ safeNum(r.ast) }}</span>
                <input v-else ref="editInput" type="number" class="cell-input center" v-model.number="r.ast"
                       @keydown.enter="commitEdit(r,'ast')" @blur="commitEdit(r,'ast')" />
              </td>
              <td class="val">
                <span v-if="!isEditing(r,'blk')" class="cell" @click="startEdit(r,'blk')">{{ safeNum(r.blk) }}</span>
                <input v-else ref="editInput" type="number" class="cell-input center" v-model.number="r.blk"
                       @keydown.enter="commitEdit(r,'blk')" @blur="commitEdit(r,'blk')" />
              </td>
              <td class="val">
                <span v-if="!isEditing(r,'fouls')" class="cell" @click="startEdit(r,'fouls')">{{ safeNum(r.fouls) }}</span>
                <input v-else ref="editInput" type="number" class="cell-input center" v-model.number="r.fouls"
                       @keydown.enter="commitEdit(r,'fouls')" @blur="commitEdit(r,'fouls')" />
              </td>

              <td class="val">
                <span v-if="!isEditing(r,'pt1')" class="cell" @click="startEdit(r,'pt1')">{{ safeNum(r.pt1) }}</span>
                <input v-else ref="editInput" type="number" class="cell-input center" v-model.number="r.pt1"
                       @keydown.enter="commitEdit(r,'pt1')" @blur="commitEdit(r,'pt1')" />
              </td>
              <td class="val">
                <span v-if="!isEditing(r,'pt2')" class="cell" @click="startEdit(r,'pt2')">{{ safeNum(r.pt2) }}</span>
                <input v-else ref="editInput" type="number" class="cell-input center" v-model.number="r.pt2"
                       @keydown.enter="commitEdit(r,'pt2')" @blur="commitEdit(r,'pt2')" />
              </td>
              <td class="val">
                <span v-if="!isEditing(r,'pt3')" class="cell" @click="startEdit(r,'pt3')">{{ safeNum(r.pt3) }}</span>
                <input v-else ref="editInput" type="number" class="cell-input center" v-model.number="r.pt3"
                       @keydown.enter="commitEdit(r,'pt3')" @blur="commitEdit(r,'pt3')" />
              </td>
            </tr>
          </tbody>
        </table>

        <div class="totals">
          <div>Players: {{ currentRows.length }}</div>
          <div>PTS Sum: {{ sum(currentRows, 'pts') }}</div>
          <div>REB Sum: {{ sum(currentRows, 'reb') }}</div>
          <div>AST Sum: {{ sum(currentRows, 'ast') }}</div>
          <div v-if="saving.any" class="muted">Saving…</div>
          <div v-else-if="okMsg" class="ok">✓ {{ okMsg }}</div>
          <div v-else-if="error" class="error">⚠ {{ error }}</div>
        </div>
      </div>

      <div class="empty" v-else>No player stats yet.</div>
    </div>

    <div class="loading" v-if="loading">Loading…</div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, reactive, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import api from '@/api/axios'

const route = useRoute()
const id = Number(route.params.id)

const loading = ref(false)
const error = ref('')
const okMsg = ref('')
const saving = reactive({ any: false })

/* ---------- helpers（与 MatchDetail 一致） ---------- */
const safeNum = (v) => (Number.isFinite(+v) ? +v : 0)
const FILE_BASE =
  import.meta.env.VITE_FILE_BASE
  || (import.meta.env.VITE_API_BASE ? import.meta.env.VITE_API_BASE.replace(/\/api\/?$/,'') : '')
  || 'http://localhost:3001'
const teamLogo = (url) => {
  if (!url) return '/placeholder-team.png'
  const u = String(url)
  if (/^https?:\/\//i.test(u)) return u
  if (u.startsWith('/')) return `${FILE_BASE}${u}`
  return `${FILE_BASE}/static/team-logos/${u}`
}
function statusText(s){ const v=String(s||'').toLowerCase(); if(['finished','final','done'].includes(v)) return 'FINAL'; if(['ongoing','live'].includes(v)) return 'LIVE'; return 'UPCOMING' }
function statusClass(s){ const v=String(s||'').toLowerCase(); if(['finished','final','done'].includes(v)) return 'finished'; if(['ongoing','live'].includes(v)) return 'ongoing'; if(['upcoming','scheduled','not started',''].includes(v)) return 'scheduled'; return 'unknown' }
function prettyDateTime(d, t, locale='en-AU'){
  if (!d && !t) return 'TBD'
  try{
    let dt
    if (d && t) dt = new Date(`${d}T${t}`)
    else if (d) dt = new Date(d)
    else dt = new Date(`1970-01-01T${t}`)
    return dt.toLocaleString(locale, {weekday:'short', day:'2-digit', month:'short', year:'numeric', hour:'2-digit', minute:'2-digit', hour12:true})
  }catch{ return [d,t].filter(Boolean).join(' ') }
}

const match = ref(null)
const side = ref('home')

const venueText = computed(() => {
  const c = match.value?.court_no
  const v = match.value?.venue
  if (v && c) return `${v} / Court ${c}`
  if (v) return v
  if (c) return `Court ${c}`
  return 'Not set'
})

/* ---------- team / players ---------- */
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

/** 统一一行的数据结构（便于编辑与提交） */
function normalizeRow(p){
  const pid = p.player_id ?? p.id
  const tid = p.team_id
  const num = (p.number ?? p.jersey_no ?? p.no ?? null)
  const name = (p.name ?? p.player_name ?? '').trim()
  const pt1 = ['one_pt_made','one_points','ones','p1'].map(k=>p[k]).find(v=>v!==undefined) ?? 0
  const pt2 = ['two_pt_made','two_points','twos','p2'].map(k=>p[k]).find(v=>v!==undefined) ?? 0
  const pt3 = ['three_pt_made','three_points','threes','p3'].map(k=>p[k]).find(v=>v!==undefined) ?? 0
  const pts = (p.points ?? p.pts ?? (1*safeNum(pt1)+2*safeNum(pt2)+3*safeNum(pt3)))
  return {
    _key: `${pid}-${tid}`,
    id: pid,
    player_id: pid,
    team_id: tid,
    number: num,
    name,
    pt1: safeNum(pt1),
    pt2: safeNum(pt2),
    pt3: safeNum(pt3),
    pts: safeNum(pts),
    reb: safeNum(p.rebounds ?? p.reb),
    ast: safeNum(p.assists ?? p.ast),
    stl: safeNum(p.steals  ?? p.stl),
    blk: safeNum(p.blocks  ?? p.blk),
    fouls: safeNum(p.fouls ?? p.foul ?? 0),
  }
}

const rowsHome = ref([])
const rowsAway = ref([])

const currentRows = computed(() => side.value === 'home' ? rowsHome.value : rowsAway.value)

/* ---------- 比赛状态推断（与公开页一致） ---------- */
const ONGOING_WINDOW_MIN = 60
function parseStartLocal(d,t){ try{ if(d&&t) return new Date(`${d}T${t}`); if(d) return new Date(d); if(t) return new Date(`1970-01-01T${t}`)}catch{} return null }
const statusFinalized = computed(() => {
  const raw = String(match.value?.status || '').trim().toLowerCase()
  const known = ['finished','final','done','ongoing','live','scheduled','upcoming','not started']
  if (known.includes(raw)) return raw
  const start = parseStartLocal(match.value?.date, match.value?.time)
  if (!start){
    const total = safeNum(homeScore.value)+safeNum(awayScore.value)
    return total>0 ? 'finished' : 'upcoming'
  }
  const diff = Date.now() - start.getTime()
  if (diff < 0) return 'upcoming'
  if (diff <= ONGOING_WINDOW_MIN*60*1000) return 'ongoing'
  return 'finished'
})

/* ---------- 编辑状态 + 保存 ---------- */
const editing = ref({ key: null, field: null })
const editInput = ref(null)
const isEditing = (r, f) => editing.value.key === r._key && editing.value.field === f
function startEdit(r,f){
  editing.value = { key: r._key, field: f }
  nextTick(()=>editInput.value?.focus())
}
function endEdit(){ editing.value = { key:null, field:null } }

function recomputePts(r){
  // 若改了 1/2/3 分，自动回填 PTS
  r.pts = safeNum(r.pt1)*1 + safeNum(r.pt2)*2 + safeNum(r.pt3)*3
}

async function commitEdit(row, field){
  // 结束编辑
  endEdit()

  // 规范化数字
  if (['pts','reb','stl','ast','blk','fouls','pt1','pt2','pt3','number'].includes(field)) {
    row[field] = safeNum(row[field])
  }
  if (['pt1','pt2','pt3'].includes(field)) recomputePts(row)

  // 调用写入接口（见第 2 节后端）
  saving.any = true
  error.value = ''
  okMsg.value = ''
  try{
    await api.post(`/matches/${id}/player-stats`, {
      match_id: id,
      team_id: row.team_id,
      player_id: row.player_id,

      // 数值字段
      points: row.pts,
      rebounds: row.reb,
      assists: row.ast,
      steals: row.stl,
      blocks: row.blk,
      fouls: row.fouls,

      one_points: row.pt1,
      two_points: row.pt2,
      three_points: row.pt3,

      // 非数值（可选）
      number: row.number,
      name: row.name
    })
    okMsg.value = 'Saved'
    setTimeout(()=> okMsg.value = '', 1200)
  }catch(e){
    error.value = e?.response?.data?.error || e?.message || 'Save failed'
  }finally{
    saving.any = false
  }
}

function sum(arr, key){ return (arr||[]).reduce((a,b)=> a + safeNum(b[key]||0), 0) }

/* ---------- 拉取 ---------- */
async function reload(){
  loading.value = true
  error.value = ''
  try{
    const data = await api.get(`/matches/${id}`)
    const m = data?.match || {}

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

    const sNum = (v) => (Number.isFinite(+v) ? +v : 0)
    const sumPts = (arr) => (arr || []).reduce((a, b) => a + sNum(b.points ?? b.pts), 0)

    match.value = {
      id: m.id ?? data.id,
      status: m.status ?? data.status ?? '',
      date: m.date ?? data.date ?? null,
      time: m.time ?? data.time ?? null,
      court_no: m.court_no ?? m.court ?? data.court_no ?? data.court ?? null,
      venue: m.venue ?? data.venue ?? null,
      home: {
        team: { id: homeObj?.id ?? m?.home_team_id ?? data?.home_team_id ?? null,
                name: homeObj?.name ?? 'Home', logo_url: homeObj?.logo_url ?? null },
        score: sumPts(homePlayers),
        players: homePlayers
      },
      away: {
        team: { id: awayObj?.id ?? m?.away_team_id ?? data?.away_team_id ?? null,
                name: awayObj?.name ?? 'Away', logo_url: awayObj?.logo_url ?? null },
        score: sumPts(awayPlayers),
        players: awayPlayers
      }
    }

    rowsHome.value = (match.value.home.players || []).map(normalizeRow)
    rowsAway.value = (match.value.away.players || []).map(normalizeRow)
  }catch(e){
    error.value = e?.message || 'Failed to load'
  }finally{
    loading.value = false
  }
}

onMounted(reload)
</script>

<style scoped>
.page{ padding:20px; }
.card{ background:#fff; border:1px solid #eef2f7; border-radius:16px; padding:16px; margin-bottom:14px; }
.spacer{ flex:1; }
.btn{ height:34px; padding:0 12px; border-radius:10px; border:1px solid #e5e7eb; background:#111827; color:#fff; }
.btn.light{ background:#fff; color:#111827; }
.chip{ font-size:12px; font-weight:800; padding:4px 10px; border-radius:9999px; border:1px solid #e5e7eb; background:#f8fafc; color:#334155; }
.chip.finished{ background:#ecfdf5; border-color:#bbf7d0; color:#065f46; }
.chip.ongoing{ background:#e6f4ff; border-color:#bee3ff; color:#0c4a6e; }
.chip.scheduled{ background:#fff7ed; border-color:#ffedd5; color:#9a3412; }
.head .row-1{ display:grid; grid-template-columns:1fr auto 1fr; align-items:center; gap:16px; }
.score.big{ font-size:48px; font-weight:900; color:#0f172a; text-align:center; line-height:1; }
.center-pack{ display:flex; align-items:center; gap:18px; }
.team-mini{ text-align:center; min-width:112px; }
.team-mini .logo{ width:96px; height:96px; border-radius:50%; border:1px solid #e5e7eb; object-fit:cover; background:#f3f4f6; }
.team-mini .tname{ margin-top:8px; font-weight:900; color:#0f172a; white-space:nowrap; }
.head .row-2{ display:flex; gap:18px; flex-wrap:wrap; margin-top:12px; color:#0f172a; font-weight:700; }
.info{ display:flex; align-items:center; gap:8px; }
.tabs{ display:flex; gap:8px; margin:8px 0 12px; }
.tab{ flex:1; height:38px; border-radius:9999px; border:1px solid #e5e7eb; background:#f8fafc; font-weight:800; cursor:pointer; }
.tab.active{ background:#1e3a8a; color:#fff; border-color:#1e3a8a; }

.table-wrap{ overflow-x:auto; }
.stat-table{ width:100%; border-collapse:separate; border-spacing:0; }
.stat-table thead th{ text-align:left; font-size:12px; color:#64748b; font-weight:900; padding:10px 12px; border-bottom:1px solid #eef2f7; background:#f8fafc; }
.stat-table tbody td{ padding:12px; border-bottom:1px solid #f1f5f9; font-weight:700; color:#0f172a; }
.stat-table tbody tr:hover{ background:#fafafa; }
.num-col{ width:68px; text-align:center; }
.name-col{ min-width:220px; }
.val{ text-align:center; }
.cell{ display:inline-block; min-width:24px; cursor:text; }
.cell-input{ width:100%; height:28px; border:1px solid #e5e7eb; border-radius:8px; padding:0 8px; font-weight:700; color:#0f172a; }
.center{ text-align:center; }
.totals{ display:flex; gap:16px; margin-top:8px; color:#475569; font-size:13px; align-items:center; }
.ok{ color:#065f46; }
.error{ color:#b91c1c; }
.loading{ padding:12px; }
@media (max-width:960px){
  .score.big{ font-size:36px; }
  .team-mini .logo{ width:80px; height:80px; }
}
</style>
