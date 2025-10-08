<!-- src/Views/admin/MatchEdit.vue -->
<template>
  <div class="page">
    <!-- 顶部栏 -->
    <div class="topbar">
      <button class="btn light" @click="$router.back()">← Back</button>
      <div class="fill"></div>
      <button class="btn" @click="reload" :disabled="loading">
        {{ loading ? 'Loading…' : 'Refresh' }}
      </button>
    </div>

    <!-- 头部：队徽 + 队名 + 总分/犯规（后端 totals） -->
    <section class="header-card">
      <div class="team-box">
        <img class="logo" :src="teamLogo(home.team)" alt="" />
        <div class="teamname">{{ teamName(home.team) }}</div>
      </div>

      <div class="score-box">
        <div class="score">
          <span>{{ totals.light.pts }}</span>
          <span class="dash">-</span>
          <span>{{ totals.dark.pts }}</span>
        </div>
        <div class="meta">
          Fouls {{ totals.light.fouls }} - {{ totals.dark.fouls }}
        </div>
      </div>

      <div class="team-box right">
        <img class="logo" :src="teamLogo(away.team)" alt="" />
        <div class="teamname">{{ teamName(away.team) }}</div>
      </div>
    </section>

    <!-- 两侧阵容 -->
    <div class="two-cols">
      <!-- Light -->
      <section class="board">
        <div class="board-title">Light</div>

        <div class="thead">
          <div class="th th-num">#</div>
          <div class="th th-name">Name</div>
          <div v-for="f in FIELD_CONFIG" :key="f.key" class="th th-stat">{{ f.label }}</div>
        </div>

        <div v-if="(home.players || []).length === 0" class="empty">No players</div>

        <div v-for="(pl,idx) in home.players" :key="pl.id" class="row player" :class="{ zebra: idx % 2 === 1 }">
          <div class="td td-num">{{ safeNum(pl.number,'-') }}</div>
          <div class="td td-name">{{ pl.name || '-' }}</div>

          <div v-for="f in FIELD_CONFIG" :key="f.key" class="td td-stat">
            <!-- PTS 只显示 -->
            <template v-if="f.key === 'points'">
              <span class="pts-val">{{ safeNum(pl.points) }}</span>
            </template>
            <!-- Foul / 1分 / 2分 / 3分 -->
            <template v-else>
              <div class="stepper">
                <button class="step -minus" @click="incrStat(pl, f.key, -1)">−</button>
                <span class="num">{{ safeNum(pl[f.key]) }}</span>
                <button class="step -plus"  @click="incrStat(pl, f.key, +1)">＋</button>
              </div>
            </template>
          </div>
        </div>
      </section>

      <!-- Dark -->
      <section class="board">
        <div class="board-title">Dark</div>

        <div class="thead">
          <div class="th th-num">#</div>
          <div class="th th-name">Name</div>
          <div v-for="f in FIELD_CONFIG" :key="f.key" class="th th-stat">{{ f.label }}</div>
        </div>

        <div v-if="(away.players || []).length === 0" class="empty">No players</div>

        <div v-for="(pl,idx) in away.players" :key="pl.id" class="row player" :class="{ zebra: idx % 2 === 1 }">
          <div class="td td-num">{{ safeNum(pl.number,'-') }}</div>
          <div class="td td-name">{{ pl.name || '-' }}</div>

          <div v-for="f in FIELD_CONFIG" :key="f.key" class="td td-stat">
            <template v-if="f.key === 'points'">
              <span class="pts-val">{{ safeNum(pl.points) }}</span>
            </template>
            <template v-else>
              <div class="stepper">
                <button class="step -minus" @click="incrStat(pl, f.key, -1)">−</button>
                <span class="num">{{ safeNum(pl[f.key]) }}</span>
                <button class="step -plus"  @click="incrStat(pl, f.key, +1)">＋</button>
              </div>
            </template>
          </div>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import api from '@/api/axios'

const route = useRoute()
const matchId = Number(route.params.id)

const loading = ref(false)
const match = ref(null)
const home = ref({ team: null, players: [] })
const away = ref({ team: null, players: [] })

// 新表头
const FIELD_CONFIG = [
  { key: 'points', label: 'PTS'  }, // display only
  { key: 'foul',   label: 'Foul' },
  { key: 'one',    label: '1分'  },
  { key: 'two',    label: '2分'  },
  { key: 'three',  label: '3分'  },
]

const totals = ref({ light: { pts: 0, fouls: 0 }, dark: { pts: 0, fouls: 0 } })

function pickPayload(res){ return (res && res.data) ? res.data : res }

async function reload() {
  loading.value = true
  try {
    const resLineup = await api.get(`/matches/${matchId}/lineup`)
    const dataL = pickPayload(resLineup)

    match.value = dataL?.match || null
    home.value = {
      team: dataL?.home?.team ?? null,
      players: Array.isArray(dataL?.home?.players) ? normalizePlayers(dataL.home.players) : []
    }
    away.value = {
      team: dataL?.away?.team ?? null,
      players: Array.isArray(dataL?.away?.players) ? normalizePlayers(dataL.away.players) : []
    }

    const resBox = await api.get(`/matches/${matchId}/boxscore`)
    const dataB = pickPayload(resBox)

    const statsMap = Object.create(null)
    for (const r of (dataB?.players ?? [])) statsMap[r.player_id] = r

    home.value.players = mergeStats(home.value.players, statsMap)
    away.value.players = mergeStats(away.value.players, statsMap)

    if (dataB?.totals) totals.value = dataB.totals
  } finally {
    loading.value = false
  }
}

function normalizePlayers(list) {
  return list.map(p => ({
    ...p,
    points: Number.isFinite(+p.points) ? +p.points : 0,
    foul:   Number.isFinite(+p.foul)   ? +p.foul   : 0,
    one:    Number.isFinite(+p.one)    ? +p.one    : 0,
    two:    Number.isFinite(+p.two)    ? +p.two    : 0,
    three:  Number.isFinite(+p.three)  ? +p.three  : 0,
  }))
}

function mergeStats(playerList, statsMap) {
  return (playerList || []).map(p => {
    const s = statsMap[p.id] || {}
    const out = { ...p }
    out.points = Number.isFinite(+s.points) ? +s.points : 0
    out.foul   = Number.isFinite(+s.foul)   ? +s.foul   : 0
    out.one    = Number.isFinite(+s.one)    ? +s.one    : 0
    out.two    = Number.isFinite(+s.two)    ? +s.two    : 0
    out.three  = Number.isFinite(+s.three)  ? +s.three  : 0
    return out
  })
}

function teamLogo(team) { return team?.logo_url || '/placeholder-team.png' }
function teamName(team) { return team?.name || 'TBD' }
function safeNum(v, alt = 0){ const n = Number(v); return Number.isFinite(n) ? n : alt }

async function incrStat(player, field, delta) {
  if (field === 'points') return
  const before = { foul: player.foul, one: player.one, two: player.two, three: player.three, points: player.points }

  if (field === 'foul')  player.foul  = Math.max(0, safeNum(player.foul)  + delta)
  if (field === 'one')   player.one   = Math.max(0, safeNum(player.one)   + delta)
  if (field === 'two')   player.two   = Math.max(0, safeNum(player.two)   + delta)
  if (field === 'three') player.three = Math.max(0, safeNum(player.three) + delta)
  player.points = player.one + 2*player.two + 3*player.three

  try {
    const resp = await api.post(`/matches/${matchId}/stat`, { player_id: player.id, field, delta })
    const data = pickPayload(resp)
    if (data?.updated) {
      player.one   = safeNum(data.updated.one)
      player.two   = safeNum(data.updated.two)
      player.three = safeNum(data.updated.three)
      player.foul  = safeNum(data.updated.foul)
      player.points= safeNum(data.updated.points)
    }
    if (data?.totals) totals.value = data.totals
  } catch (e) {
    Object.assign(player, before)
  }
}

onMounted(reload)
</script>

<!-- 全局样式（非 scoped）：彻底禁用横向滚动 -->
<style>
html, body, #app { overflow-x: hidden; }
*, *::before, *::after { box-sizing: border-box; }
.page, .two-cols, .board { overflow-x: hidden !important; }
</style>

<!-- 全局样式（非 scoped） -->
<style>
html, body, #app { overflow-x: hidden; }
*, *::before, *::after { box-sizing: border-box; }
/* 防止任何容器出现横向滚动条 */
.page, .two-cols, .board { overflow-x: hidden !important; }
</style>
<!-- 全局样式（非 scoped） -->
<style>
html, body, #app { overflow-x: hidden; }
*, *::before, *::after { box-sizing: border-box; }

/* 防止父容器出现横向滚动条：注意这里不再包含 .board，避免裁掉 3分列 */
.page, .two-cols { overflow-x: hidden !important; }
</style>

<!-- 页面私有样式（scoped） -->
<!-- 全局样式（非 scoped） -->
<style>
html, body, #app { overflow-x: hidden; }   /* 禁止横向滚动 */
*, *::before, *::after { box-sizing: border-box; }
</style>

<!-- 页面私有样式（scoped） -->
<!-- 全局样式（非 scoped） -->
<style>
html, body, #app { overflow-x: hidden; }  /* 禁止横向滚动 */
*, *::before, *::after { box-sizing: border-box; }
</style>

<!-- 页面私有样式（scoped） -->
<!-- 全局样式（非 scoped） -->
<style>
html, body, #app { overflow-x: hidden; } /* 禁止横向滚动 */
*, *::before, *::after { box-sizing: border-box; }
</style>

<!-- 页面私有样式（scoped） -->
<style scoped>
/* ===== 主题变量 ===== */
.page{
  --bg:#f5f7fb; --card:#ffffff; --line:#eef2f7;
  --muted:#6b7280; --text:#0f172a; --chip:#f3f4f6;

  padding:20px 24px; background:var(--bg);
}

/* 顶部栏 */
.topbar{ display:flex; align-items:center; gap:12px; margin-bottom:12px; }
.fill{ flex:1; }
.btn{
  height:34px; padding:0 12px; border-radius:12px; border:1px solid #e5e7eb;
  background:#111827; color:#fff; font-size:13px;
}
.btn.light{ background:#fff; color:#111827; }

/* 记分牌 */
.header-card{
  display:grid; grid-template-columns: 1fr auto 1fr; align-items:center;
  gap:10px; padding:18px; border:1px solid var(--line); border-radius:18px;
  background:var(--card); margin-bottom:14px; box-shadow:0 6px 18px rgba(17,24,39,.05);
}
.team-box{ display:flex; align-items:center; gap:12px; min-width:0; }
.team-box.right{ justify-content:flex-end; }
.logo{ width:52px; height:52px; border-radius:50%; object-fit:cover; }
.teamname{ font-size:20px; font-weight:800; color:var(--text); white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
.score-box{ text-align:center; }
.score{ font-size:54px; font-weight:900; color:var(--text); font-variant-numeric: tabular-nums; line-height:1; }
.score .dash{ padding:0 10px; color:#475569; }
.meta{ font-size:12px; color:#6b7280; margin-top:6px; }

/* ===== 始终左右两栏（不堆叠） ===== */
.two-cols{
  display:grid;
  grid-template-columns: minmax(0,1fr) minmax(0,1fr);
  gap:16px;
}

/* 卡片 */
.board{
  background:var(--card); border:1px solid var(--line); border-radius:16px; padding:12px;
  box-shadow:0 2px 10px rgba(17,24,39,.04);

  /* 列宽变量：统一在这改就行 */
  --num-w: 32px;    /* # */
  --name-w: 60px;   /* Name（更窄，左对齐）*/
  --pts-w: 56px;    /* PTS */
  --stat-w: 80px;   /* Foul/1分/2分/3分 */
}
.board-title{ font-weight:800; color:var(--text); margin-bottom:8px; font-size:16px; }

/* ===== 表头与行 ===== */
/* 布局：# | Name | PTS | Foul | 1分 | 2分 | 3分 */
.thead, .row.player{
  display:grid;
  grid-template-columns: var(--num-w) var(--name-w) var(--pts-w) repeat(4, var(--stat-w));
  gap:6px; align-items:center; min-width:0; max-width:100%;
}
.th, .td{ padding:6px 4px; }
.th{ color:var(--muted); font-weight:700; font-size:12px; text-align:center; }
.td{ color:var(--text); font-weight:600; font-size:13px; text-align:center; }

/* Name 列强制左对齐并省略号 */
.th-name, .td-name{
  text-align:left !important;
  padding-left:6px;
  white-space:nowrap; overflow:hidden; text-overflow:ellipsis;
}

/* 斑马 + 分隔 */
.row.player{ border-top:1px dashed #f1f5f9; border-radius:12px; }
.row.player.zebra{ background:#fafcff; }

/* PTS 芯片 */
.pts-val{
  display:inline-block; width:100%; max-width:40px; padding:4px 8px; margin:0 auto;
  background:var(--chip); border-radius:10px; font-weight:800; text-align:center;
  font-variant-numeric: tabular-nums;
}

/* Stepper（- 数 +）占满单元格，随列宽缩放 */
.stepper{
  display:flex; align-items:center; justify-content:space-between;
  gap:4px; padding:2px 4px; background:var(--chip); border-radius:9999px;
  width:100%;
}
.step{
  flex:0 0 18px; height:18px; line-height:16px; text-align:center;
  border-radius:9999px; border:1px solid #e5e7eb; background:#fff; cursor:pointer;
  font-weight:900; font-size:11px; color:#0f172a;
}
.num{
  flex:1 1 auto; min-width:0; text-align:center; font-weight:800;
  font-variant-numeric: tabular-nums; font-size:12px;
}

/* 空状态 */
.empty{ color:#94a3b8; padding:8px; font-size:13px; text-align:center; }

/* ===== 渐进压缩（仍保持左右两栏、无横向滚动）===== */
@media (max-width: 1360px){
  .board{ --name-w: 88px; --pts-w: 52px; --stat-w: 76px; }
  .step{ flex-basis:16px; height:16px; line-height:14px; font-size:10px; }
  .num{ font-size:11px; }
}
@media (max-width: 1220px){
  .board{ --name-w: 80px; --pts-w: 50px; --stat-w: 74px; }
  .td, .th{ font-size:12px; }
  .pts-val{ max-width:36px; }
}
</style>
