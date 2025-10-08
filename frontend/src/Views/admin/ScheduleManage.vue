<template>
  <div class="page">
    <h1>Schedule Management</h1>

    <!-- Toolbar -->
    <div class="toolbar">
      <label>
        Division:
        <select v-model="divisionCode" @change="reloadAll" :disabled="busy">
          <option value="champion">Champion</option>
          <option value="d1">D1</option>
          <option value="d2">D2</option>
        </select>
      </label>

      <button class="btn" :disabled="busy" @click="reloadAll">Refresh</button>

      <span class="divider"></span>

      <button class="btn primary" :disabled="busy" @click="onGenerateRegular">
        ⚙️ Generate Regular
      </button>

      <span class="divider"></span>

      <button class="btn danger" :disabled="busy" @click="onClearAll">
        🗑️ Clear All
      </button>

      <span v-if="busy" class="loading">Processing…</span>
      <span v-else-if="loading" class="loading">Loading…</span>
    </div>

    <!-- Teams -->
    <section class="card">
      <h3>Teams</h3>
      <div v-if="teams.length === 0" class="empty">No teams available</div>
      <ul v-else class="team-list">
        <li v-for="t in teams" :key="t.id">
          <button class="team-link" @click="goTeam(t.id)">{{ t.name }}</button>
        </li>
      </ul>
    </section>

    <!-- Regular -->
    <section class="card">
      <h3>Regular Season · {{ rounds.length }} Rounds</h3>
      <div class="round-grid">
        <button
          v-for="n in 11"
          :key="n"
          class="round-btn"
          @click="goRound(n)"
        >
          Round {{ n }}
          <span v-if="roundCount(n)" class="badge">{{ roundCount(n) }} games</span>
        </button>
      </div>
      <div v-if="rounds.length === 0" class="empty">No schedule</div>
    </section>

    <!-- Playoffs -->
    <section class="card">
      <h3>Playoffs · 3 Rounds</h3>

      <div class="stage-grid single-column">
        <div class="stage-card" v-for="st in displayPlayoffs" :key="st.key">
          <div class="stage-head">
            <div class="title">{{ st.name }}</div>
            <button class="btn small light" @click="onAddMatch(st.key)">➕ Add Match</button>
          </div>

          <div v-if="!st.matches || st.matches.length === 0" class="empty">No games</div>

          <div v-for="m in st.matches || []" :key="m.id || m.uid" class="match line">
            <!-- Home -->
            <template v-if="m.home_team_id">
              <button class="team link home" @click="goTeam(m.home_team_id)">{{ teamName(m.home_team_id) }}</button>
            </template>
            <template v-else>
              <span class="team home">{{ seedOrTeam(m.home_seed, m.home_team_id) }}</span>
            </template>

            <!-- Score -->
            <div class="score">
              <span class="score-num">{{ m.home_pts ?? 0 }}</span>
              <span class="dash">-</span>
              <span class="score-num">{{ m.away_pts ?? 0 }}</span>
            </div>

            <!-- Away -->
            <template v-if="m.away_team_id">
              <button class="team link away" @click="goTeam(m.away_team_id)">{{ teamName(m.away_team_id) }}</button>
            </template>
            <template v-else>
              <span class="team away">{{ seedOrTeam(m.away_seed, m.away_team_id) }}</span>
            </template>

            <span class="when">{{ formatDT(m.scheduled_at) || 'TBD' }}</span>
            <span class="venue" v-if="m.venue">· {{ m.venue }}</span>

            <div class="ops" v-if="m.id">
              <button class="btn small light" :disabled="working" @click="goEdit(m.id)">Edit</button>
              <button class="btn small danger" :disabled="working" @click="onDeletePlayoff(m.id)">Delete</button>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Modal -->
    <div v-if="showModal" class="modal-mask">
      <div class="modal-container">
        <h3>New Playoff Match</h3>

        <label>Round</label>
        <select v-model="form.round_no">
          <option :value="1">Round 1</option>
          <option :value="2">Round 2</option>
          <option :value="3">Final</option>
        </select>

        <label>Home Team</label>
        <select v-model="form.home_team_id">
          <option disabled value="">Select home team</option>
          <option v-for="t in teams" :key="t.id" :value="t.id">{{ t.name }}</option>
        </select>

        <label>Away Team</label>
        <select v-model="form.away_team_id">
          <option disabled value="">Select away team</option>
          <option v-for="t in teams" :key="t.id" :value="t.id">{{ t.name }}</option>
        </select>

        <label>Date</label>
        <input type="date" v-model="form.date" />

        <label>Time</label>
        <input type="time" v-model="form.time" />

        <label>Venue</label>
        <input type="text" v-model="form.venue" placeholder="e.g. Court 7" />

        <div class="actions">
          <button class="btn light" @click="showModal = false">Cancel</button>
          <button class="btn primary" @click="submitMatch" :disabled="submitting">
            {{ submitting ? 'Submitting...' : 'Create Match' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/api/axios'

const divisionCode = ref('champion')
const seasonId = 1
const router = useRouter()

const loading = ref(false)
const working = ref(false)
const busy = computed(() => loading.value || working.value)

const teams = ref([])
const rounds = ref([])
const playoffs = ref([])

const showModal = ref(false)
const submitting = ref(false)

const form = ref({
  round_no: 1,
  home_team_id: '',
  away_team_id: '',
  date: '',
  time: '',
  venue: ''
})

const defaultPlayoffStages = [
  { key: 'r1', name: 'Playoff Round 1', matches: [] },
  { key: 'r2', name: 'Playoff Round 2', matches: [] },
  { key: 'final', name: 'Final', matches: [] },
]

const displayPlayoffs = computed(() =>
  Array.isArray(playoffs.value) && playoffs.value.length > 0 ? playoffs.value : defaultPlayoffStages
)

const teamMap = computed(() => {
  const map = new Map()
  teams.value.forEach(t => map.set(t.id, t.name))
  map.set(-1, 'BYE')
  return map
})
const teamName = id => teamMap.value.get(id) ?? (id ? `#${id}` : '-')
const seedOrTeam = (seed, id) => (seed ? `Seed ${seed}` : teamName(id))

function formatDT(iso) {
  if (!iso) return ''
  const d = new Date(iso)
  if (Number.isNaN(d.getTime())) return iso
  const pad = n => String(n).padStart(2, '0')
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}`
}

function roundCount(n) {
  const r = rounds.value.find(x => Number(x.round_no) === Number(n))
  return r?.matches?.length || 0
}

function goRound(n) {
  router.push({ name: 'roundDetail', params: { no: n }, query: { division: divisionCode.value } })
}
function goTeam(id) {
  if (!id) return
  router.push({ name: 'playersManage', params: { id } })
}
function goEdit(matchId) {
  router.push({ name: 'matchEdit', params: { id: matchId } })
}

/** 从 lineup 汇总比分 */
async function hydrateScoreFor(m) {
  if (!m?.id) return
  try {
    const res = await api.get(`/matches/${m.id}/lineup`)
    const payload = res?.data || res
    const sum = arr => (Array.isArray(arr) ? arr.reduce((a, b) => a + Number(b?.points || 0), 0) : 0)
    m.home_pts = sum(payload?.home?.players)
    m.away_pts = sum(payload?.away?.players)
  } catch {
    m.home_pts = 0
    m.away_pts = 0
  }
}

/** 为所有季后赛比赛补比分 */
async function hydrateAllPlayoffScores() {
  const jobs = []
  for (const st of playoffs.value) {
    if (Array.isArray(st.matches)) {
      for (const m of st.matches) jobs.push(hydrateScoreFor(m))
    }
  }
  await Promise.all(jobs)
}

async function onGenerateRegular() {
  if (!confirm('Generate regular season? This will clear existing data.')) return
  working.value = true
  try {
    await api.post(`/divisions/${divisionCode.value}/schedule/generate`, { season_id: seasonId })
    await reloadAll()
    alert('Regular season generated.')
  } catch (e) {
    console.error(e)
    alert('Generation failed.')
  } finally {
    working.value = false
  }
}

async function onClearAll() {
  if (!confirm('Clear all games for this division?')) return
  working.value = true
  try {
    await api.delete(`/divisions/${divisionCode.value}/schedule`, { params: { season_id: seasonId } })
    await reloadAll()
    alert('Cleared.')
  } catch (e) {
    console.error(e)
    alert('Clear failed.')
  } finally {
    working.value = false
  }
}

function onAddMatch(stageKey) {
  showModal.value = true
  form.value.round_no = stageKey === 'r1' ? 1 : stageKey === 'r2' ? 2 : 3
}

async function submitMatch() {
  if (!form.value.home_team_id || !form.value.away_team_id) {
    alert('Please select both teams.')
    return
  }
  if (form.value.home_team_id === form.value.away_team_id) {
    alert('Home and away cannot be the same team.')
    return
  }
  if (!form.value.date || !form.value.time || !form.value.venue) {
    alert('Date, time, and venue are required.')
    return
  }

  submitting.value = true
  try {
    await api.post(`/divisions/${divisionCode.value}/playoffs`, {
      season_id: seasonId,
      round_no: form.value.round_no,
      date: form.value.date,
      time: form.value.time,
      venue: form.value.venue,
      home_team_id: form.value.home_team_id,
      away_team_id: form.value.away_team_id,
      status: 'scheduled'
    })
    alert('Match created.')
    showModal.value = false
    await reloadAll()
  } catch (e) {
    console.error(e)
    alert('Failed to create match.')
  } finally {
    submitting.value = false
  }
}

async function onDeletePlayoff(matchId) {
  if (!matchId) return
  if (!confirm('Delete this playoff match? This cannot be undone.')) return
  working.value = true
  try {
    await api.delete(`/matches/${matchId}`)
    for (const st of playoffs.value) {
      const i = (st.matches || []).findIndex(x => Number(x.id) === Number(matchId))
      if (i >= 0) {
        st.matches.splice(i, 1)
        break
      }
    }
  } catch (e) {
    console.error(e)
    alert('Delete failed.')
  } finally {
    working.value = false
  }
}

async function reloadAll() {
  loading.value = true
  try {
    teams.value = await api.get(`/divisions/${divisionCode.value}/teams?season_id=${seasonId}`)
    const sch = await api.get(`/divisions/${divisionCode.value}/schedule?season_id=${seasonId}`)
    rounds.value = Array.isArray(sch?.regular) ? sch.regular : []
    playoffs.value = Array.isArray(sch?.playoffs) ? sch.playoffs : []
    // ⭐ 补比分
    await hydrateAllPlayoffScores()
  } catch (e) {
    console.error(e)
    teams.value = teams.value || []
    rounds.value = []
    playoffs.value = []
  } finally {
    loading.value = false
  }
}

onMounted(reloadAll)
</script>

<style scoped>
.page { padding: 24px; }
.toolbar { display:flex; gap:12px; align-items:center; margin-bottom:16px; flex-wrap:wrap; }
.btn { height:36px; padding:0 12px; border-radius:10px; border:1px solid #e5e7eb; background:#111827; color:#fff; cursor:pointer; }
.btn.primary { background:#111827; }
.btn.light { background:#fff; color:#111827; }
.btn.danger { background:#ef4444; border-color:#ef4444; }
.btn.small { height:30px; padding:0 10px; border-radius:8px; }
.divider { width:1px; height:22px; background:#e5e7eb; }

.loading { color:#6b7280; }
.card { background:#fff; border:1px solid #eee; border-radius:16px; padding:16px; margin-bottom:16px; }
.empty { color:#6b7280; padding:8px 0; }
.team-list { display:grid; grid-template-columns: repeat(auto-fill, minmax(160px,1fr)); gap:8px; margin:0; padding:0; list-style:none; }
.team-link { background:none; border:none; padding:0; margin:0; color:#0f172a; font-weight:700; cursor:pointer; }
.team-link:hover { text-decoration:underline; }

.round-grid { display:grid; grid-template-columns: repeat(auto-fill, minmax(120px, 1fr)); gap:10px; margin:12px 0 4px; }
.round-btn { height:42px; border-radius:12px; border:1px solid #e5e7eb; background:#fff; cursor:pointer; font-weight:700; display:flex; align-items:center; justify-content:center; gap:8px; transition: all .15s ease; }
.round-btn:hover { background:#111827; color:#fff; border-color:#111827; transform: translateY(-1px); }
.badge { font-size:12px; padding:2px 6px; border-radius:999px; background:#f1f5f9; color:#111827; }

.stage-grid.single-column { display:grid; grid-template-columns: 1fr; gap:12px; margin-top:8px; }
.stage-card { border:1px solid #f1f5f9; border-radius:14px; padding:12px; display:flex; flex-direction:column; gap:8px; background:#fafbfc; }
.stage-head { display:flex; align-items:center; justify-content:space-between; }
.stage-head .title { font-weight:800; font-size:16px; }

.match.line {
  display:grid;
  grid-template-columns: 1.4fr 120px 1.4fr 200px 1fr 160px; /* 改：中间留120px显示比分 */
  align-items:center;
  gap:8px; padding:10px;
  border:1px solid #eef2f7; border-radius:10px; background:#fff;
}
.team { white-space:nowrap; overflow:hidden; text-overflow:ellipsis; font-weight:700; }
.team.link { background:none; border:none; padding:0; margin:0; cursor:pointer; color:#0f172a; text-align:left; }
.team.link:hover { text-decoration:underline; }

.score { display:flex; align-items:center; justify-content:center; gap:8px; }
.score-num { font-size:22px; font-weight:800; color:#0f172a; }
.dash { color:#64748b; font-weight:800; }

.when { color:#111827; white-space:nowrap; }
.venue { color:#6b7280; white-space:nowrap; }
.ops { display:flex; gap:8px; justify-content:flex-end; }
</style>
