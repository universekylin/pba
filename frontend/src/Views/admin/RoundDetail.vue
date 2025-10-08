<!-- src/views/admin/RoundDetail.vue -->
<template>
  <div class="page">
    <div class="topbar">
      <button class="btn light" @click="$router.back()">← Back</button>
      <h2>Round {{ roundNo }} · {{ divisionLabel }}</h2>
      <div class="fill"></div>
      <label class="edit-switch">
        <input type="checkbox" v-model="editing" />
        Edit this round
      </label>
      <button class="btn" :disabled="loading" @click="reload">
        {{ loading ? 'Loading…' : 'Refresh' }}
      </button>
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
              <RouterLink
                v-if="m.home_team?.id"
                class="name clickable"
                :to="`/admin-panel/teams/${m.home_team.id}/players`"
              >
                {{ m.home_team.name }}
              </RouterLink>
              <span v-else class="name muted">TBD</span>
            </div>
          </div>

          <!-- Center: score -->
          <div class="center">
            <span class="score-num">{{ m.home_pts ?? 0 }}</span>
            <span class="dash">-</span>
            <span class="score-num">{{ m.away_pts ?? 0 }}</span>
          </div>

          <!-- Away -->
          <div class="side">
            <div class="teamcell">
              <img class="logo" :src="logoOf(m.away_team)" alt="" />
              <RouterLink
                v-if="m.away_team?.id"
                class="name clickable"
                :to="`/admin-panel/teams/${m.away_team.id}/players`"
              >
                {{ m.away_team.name }}
              </RouterLink>
              <span v-else class="name muted">TBD</span>
            </div>
          </div>

          <!-- Right meta -->
          <div class="meta" v-if="!editing">
            <div class="when">{{ mergedWhen(m.date, m.time) || 'Not set' }}</div>
            <div class="venue">{{ m.venue || 'Not set' }}</div>
            <span class="status" :class="statusClass(m)">{{ statusText(m) }}</span>
            <RouterLink class="btn small outline" :to="`/admin-panel/matches/${m.id}/edit`">Edit</RouterLink>
          </div>

          <!-- Edit meta -->
          <div class="meta edit" v-else>
            <div class="row">
              <input class="inp" type="date" v-model="form[m.id].date" />
              <input class="inp" type="time" v-model="form[m.id].time" />
              <input class="inp" placeholder="Court" v-model="form[m.id].venue" />
            </div>
            <div class="row btns">
              <button class="btn small" @click="saveMatch(m.id)">Save</button>
              <button class="btn small danger" @click="removeMatch(m.id)">Delete</button>
            </div>
          </div>
        </div>

        <!-- Create -->
        <div v-if="editing" class="create-card">
          <div class="title">Create a new game</div>
          <div class="row">
            <select class="inp" v-model="create.home_team_id">
              <option :value="null" disabled>Home team</option>
              <option v-for="t in teams" :key="t.id" :value="t.id">{{ t.name }}</option>
            </select>
            <span class="vs">vs</span>
            <select class="inp" v-model="create.away_team_id">
              <option :value="null" disabled>Away team</option>
              <option v-for="t in teams" :key="t.id" :value="t.id">{{ t.name }}</option>
            </select>
          </div>
          <div class="row">
            <input class="inp" type="date" v-model="create.date" />
            <input class="inp" type="time" v-model="create.time" />
            <input class="inp" placeholder="Court" v-model="create.venue" />
            <button class="btn" @click="createMatch">Add</button>
          </div>
        </div>
      </template>
    </section>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import api from '@/api/axios'

// 比赛默认时长：60 分钟（可以按需改）
const GAME_DURATION_MIN = 60;

const route = useRoute()
const roundNo = Number(route.params.no)
const divisionCode = String(route.query.division || 'champion').toLowerCase()
const SEASON_ID = 1

const loading = ref(false)
const matches = ref([])
const teams = ref([])

const editing = ref(false)
const form = ref({})
const create = ref({ home_team_id: null, away_team_id: null, date: '', time: '', venue: '' })

const divisionLabel = computed(() => ({
  champion: 'Division Champion',
  d1: 'Division 1',
  d2: 'Division 2'
}[divisionCode] || divisionCode.toUpperCase()))

function logoOf(team) { return (team && team.logo_url) ? team.logo_url : '/placeholder-team.png' }
function mergedWhen(dateStr, timeStr) {
  if (!dateStr && !timeStr) return ''
  const t = s => String(s || '').trim()
  if (t(dateStr) && t(timeStr)) return `${dateStr} ${timeStr.slice(0,5)}`
  return t(dateStr) || t(timeStr)
}

/** 把 date + time 组合成 Date，失败返回 null */
function asDate(m) {
  if (!m?.date) return null
  try {
    const hhmm = (m.time || '00:00').slice(0,5)
    return new Date(`${m.date}T${hhmm}:00`)
  } catch { return null }
}

/** 动态状态文案 */
function statusText(m) {
  // 后端显式给出状态时优先使用
  if (m.status === 'canceled') return 'Canceled';
  if (m.status === 'finished') return 'Finished';

  const start = asDate(m);
  if (!start) return 'Not set';

  const end = new Date(start.getTime() + GAME_DURATION_MIN * 60000);
  const now = new Date();

  if (now < start) return 'Not started';
  if (now >= end) return 'Finished';
  return 'Ongoing';
}
/** 动态状态样式 */
function statusClass(m) {
  const s = statusText(m);
  return {
    scheduled: s === 'Not started',
    ongoing:   s === 'Ongoing',
    finished:  s === 'Finished',
    canceled:  s === 'Canceled'
  };
}

/** 拉 rounds API（或 fallback） */
async function fetchRoundsAPI() {
  const { data } = await api.get(`/divisions/${divisionCode}/rounds/${roundNo}`, {
    params: { season_id: SEASON_ID }
  })
  if (Array.isArray(data) && data.length > 0) return data
  return null
}
async function fetchViaScheduleFallback() {
  const [teamsRes, schRes] = await Promise.all([
    api.get(`/divisions/${divisionCode}/teams`, { params: { season_id: SEASON_ID } }),
    api.get(`/divisions/${divisionCode}/schedule`, { params: { season_id: SEASON_ID } })
  ])
  const listTeams = (teamsRes.data || teamsRes) ?? []
  const teamMap = new Map(listTeams.map(t => [t.id, t]))
  const regular = (schRes?.data?.regular) ?? schRes?.regular ?? []
  const r = regular.find(x => Number(x.round_no) === roundNo)
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

/** 计算某场的当前得分/犯规（用现有 /matches/:id/lineup） */
async function hydrateScoreFor(m) {
  try {
    const res = await api.get(`/matches/${m.id}/lineup`)
    const payload = res?.data || res
    const sum = (arr) => (Array.isArray(arr) ? arr.reduce((a,b)=> a + Number(b?.points || 0), 0) : 0)
    const sumF = (arr) => (Array.isArray(arr) ? arr.reduce((a,b)=> a + Number(b?.fouls || 0), 0) : 0)
    m.home_pts = sum(payload?.home?.players)
    m.away_pts = sum(payload?.away?.players)
    m.home_fouls = sumF(payload?.home?.players)
    m.away_fouls = sumF(payload?.away?.players)
  } catch {
    m.home_pts = 0
    m.away_pts = 0
    m.home_fouls = 0
    m.away_fouls = 0
  }
}

function sortMatchesInPlace(list) {
  list.sort((a,b)=>{
    const da = asDate(a), db = asDate(b)
    if (da && db) return da.getTime() - db.getTime()
    if (da && !db) return -1
    if (!da && db) return 1
    return a.id - b.id
  })
}

async function reload() {
  loading.value = true
  try {
    const [roundData, teamRes] = await Promise.all([
      (async () => (await fetchRoundsAPI()) ?? await fetchViaScheduleFallback())(),
      api.get(`/divisions/${divisionCode}/teams`, { params: { season_id: SEASON_ID } })
    ])
    matches.value = roundData || []
    teams.value = teamRes.data || teamRes

    // 初始化编辑表单
    const obj = {}
    for (const m of matches.value) {
      obj[m.id] = {
        date: m.date || '',
        time: (m.time || '').slice(0,5),
        venue: m.venue || ''
      }
    }
    form.value = obj

    // 并发补齐当前比分
    await Promise.all(matches.value.map(hydrateScoreFor))

    // 按时间排序（最早在前，没有时间的放最后）
    sortMatchesInPlace(matches.value)
  } finally {
    loading.value = false
  }
}

async function saveMatch(id){
  const body = { ...form.value[id] }
  if (!body.date) body.date = null
  if (!body.time) body.time = null
  if (!body.venue) body.venue = null
  const { data } = await api.patch(`/matches/${id}`, body)
  const idx = matches.value.findIndex(m => m.id === id)
  if (idx >= 0) {
    // 合并返回值（可能只回了部分字段）
    matches.value[idx] = { ...matches.value[idx], ...data }
    // 更新显示的比分（不影响，但让它保持最新）
    await hydrateScoreFor(matches.value[idx])
    // 重新排序
    sortMatchesInPlace(matches.value)
  }
}
async function removeMatch(id){
  await api.delete(`/matches/${id}`)
  matches.value = matches.value.filter(m => m.id !== id)
  delete form.value[id]
}
async function createMatch(){
  if(!create.value.home_team_id || !create.value.away_team_id){
    alert('Pick both home & away team first')
    return
  }
  const body = {
    season_id: SEASON_ID,
    home_team_id: create.value.home_team_id,
    away_team_id: create.value.away_team_id,
    date: create.value.date || null,
    time: create.value.time || null,
    venue: create.value.venue || null,
  }
  const { data } = await api.post(`/divisions/${divisionCode}/rounds/${roundNo}/matches`, body)
  const merged = { ...data, home_pts: 0, away_pts: 0, home_fouls: 0, away_fouls: 0 }
  matches.value.push(merged)
  form.value[data.id] = {
    date: data.date || '',
    time: (data.time || '').slice(0,5),
    venue: data.venue || ''
  }
  create.value = { home_team_id: null, away_team_id: null, date: '', time: '', venue: '' }
  sortMatchesInPlace(matches.value)
}

onMounted(reload)
</script>

<style scoped>
.page{ padding:24px; }
.topbar{ display:flex; align-items:center; gap:12px; margin-bottom:12px; }
.fill{ flex:1; }
.btn{ height:36px; padding:0 12px; border-radius:10px; border:1px solid #e5e7eb; background:#111827; color:#fff; cursor:pointer; }
.btn.light{ background:#fff; color:#111827; }
.btn.outline{ background:#fff; color:#111827; border-color:#cbd5e1; }
.btn.small{ height:30px; padding:0 10px; border-radius:8px; }
.btn.danger{ background:#dc2626; color:#fff; }
.card{ background:#fff; border:1px solid #eee; border-radius:16px; padding:16px; }
.empty{ color:#6b7280; padding:8px 0; }
.edit-switch{ display:flex; align-items:center; gap:6px; color:#374151; font-size:14px; }

.match{
  display:grid; grid-template-columns: 1fr 160px 1fr 320px;
  gap:12px; padding:14px 16px; border:1px solid #f1f5f9; border-radius:12px;
  margin-top:10px; align-items:center; background:#fff;
}

.teamcell{ display:inline-flex; align-items:center; gap:10px; min-width:0; }
.teamcell .logo{ width:40px; height:40px; border-radius:50%; object-fit:cover; flex:0 0 40px; }
.name{ font-weight:600; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
.name.clickable{ color:#2563eb; cursor:pointer; text-decoration:none; }
.name.clickable:hover{ text-decoration:underline; }
.name.muted{ color:#9aa0a6; }

.center{ display:flex; align-items:center; justify-content:center; gap:8px; }
.score-num{ font-size:32px; font-weight:800; color:#0f172a; }
.dash{ color:#64748b; font-weight:800; }

.meta{ display:flex; flex-direction:column; gap:6px; align-items:flex-end; }
.meta .when{ color:#111827; font-size:14px; }
.meta .venue{ color:#6b7280; font-size:12px; }
.status{ display:inline-block; padding:2px 8px; border-radius:999px; background:#e5e7eb; font-size:12px; color:#111827; }
.status.scheduled{ background:#fef3c7; }
.status.ongoing{ background:#dbeafe; }   /* 蓝色表示进行中 */
.status.finished{ background:#dcfce7; }
.status.canceled{ background:#fee2e2; }

.meta.edit{ align-items:flex-end; gap:8px; }
.row{ display:flex; gap:8px; flex-wrap:wrap; }
.row.btns{ margin-top:4px; }
.inp{ height:34px; padding:0 10px; border:1px solid #e5e7eb; border-radius:10px; background:#fff; min-width:120px; }

.create-card{
  margin-top:16px; padding:14px 16px; border:1px dashed #cbd5e1; border-radius:12px; background:#ffffff;
}
.create-card .title{ font-weight:700; margin-bottom:8px; color:#0f172a; }

@media (max-width: 980px){
  .match{ grid-template-columns: 1fr 120px 1fr; }
  .meta, .meta.edit{ grid-column: 1 / -1; align-items:flex-start; }
}
</style>
