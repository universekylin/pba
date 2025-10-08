<template>
  <div class="page">
    <!-- 顶部只保留标题 + Division 选择 -->
    <div class="topbar">
      <h1>Ladder</h1>
      <div class="fill"></div>

      <label class="field">
        <span>Division</span>
        <select v-model="division" @change="loadLadder">
          <option value="champion">Champion</option>
          <option value="d1">D1</option>
          <option value="d2">D2</option>
        </select>
      </label>
    </div>

    <section class="card">
      <div v-if="loading" class="empty">Loading…</div>
      <div v-else-if="ladder.length === 0" class="empty">No data</div>

      <div v-else class="ladder-list">
        <!-- 表头 -->
        <div class="ladder-row header">
          <div class="col rank">#</div>
          <div class="col logo"></div>
          <div class="col name">Team</div>
          <div class="col stat">Win</div>
          <div class="col stat">Draw</div>
          <div class="col stat">Lose</div>
          <div class="col pts">PTS</div>
        </div>

        <!-- 数据行 -->
        <div v-for="t in ladder" :key="t.team_id" class="ladder-row">
          <div class="col rank"><span class="pill">{{ t.rank }}</span></div>
          <div class="col logo">
            <img v-if="t.logo_url" :src="t.logo_url" alt="Logo" />
            <div v-else class="logo-placeholder">🏀</div>
          </div>
          <div class="col name">{{ t.name }}</div>
          <div class="col stat">{{ t.wins }}</div>
          <div class="col stat">{{ t.draws }}</div>
          <div class="col stat">{{ t.losses }}</div>
          <div class="col pts"><span class="chip">{{ t.points }}</span></div>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '@/api/axios'

// 默认 Champion，可根据需要改为从 query 读
const division = ref('champion')
const ladder = ref([])
const loading = ref(false)

async function loadLadder () {
  loading.value = true
  try {
    // 你的 axios 封装在其它页返回的就是 data，这里保持一致写法
    const data = await api.get(`/divisions/${division.value}/ladder`)
    ladder.value = Array.isArray(data?.ladder) ? data.ladder : []
  } finally {
    loading.value = false
  }
}

onMounted(loadLadder)
</script>

<style scoped>
.page { padding: 24px; display:flex; flex-direction:column; gap:16px; }
.topbar { display:flex; align-items:center; gap:12px; }
.topbar h1 { margin:0; font-size:22px; font-weight:800; }
.fill { flex:1; }
.field { display:flex; align-items:center; gap:8px; color:#374151; }
select { padding:6px 10px; border-radius:10px; border:1px solid #e5e7eb; }

.card {
  background:#fff; border:1px solid #eee; border-radius:16px;
  padding:14px 16px; box-shadow: 0 1px 2px rgba(0,0,0,.04);
}
.empty { padding:24px; color:#6b7280; }

.ladder-list { display:flex; flex-direction:column; gap:8px; }
.ladder-row {
  display:grid;
  grid-template-columns: 64px 56px 1fr 64px 64px 64px 84px;
  align-items:center; gap:8px;
  background:#f9fafb; padding:10px 12px; border-radius:12px;
}
.ladder-row.header { background:transparent; color:#6b7280; font-weight:700; }

.col.rank { display:flex; justify-content:center; }
.pill { display:inline-block; min-width:36px; text-align:center; padding:4px 8px; border-radius:999px; background:#eef2ff; font-weight:700; }
.col.logo { display:flex; justify-content:center; }
.col.logo img { width:40px; height:40px; object-fit:cover; border-radius:8px; }
.logo-placeholder { width:40px; height:40px; display:grid; place-items:center; background:#eee; border-radius:8px; }
.col.name { font-weight:600; }
.col.stat, .col.pts { text-align:center; font-variant-numeric: tabular-nums; }
.chip { display:inline-block; min-width:48px; text-align:center; padding:6px 10px; border-radius:999px; background:#e5f3ff; font-weight:800; }

@media (max-width: 520px) {
  .ladder-row { grid-template-columns: 48px 44px 1fr 48px 48px 48px 64px; }
}
</style>
