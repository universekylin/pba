<template>
  <div class="page ranking-bg">
    <div class="head">
      <h1>Player Ranking · {{ title }}</h1>
      <div class="fill"></div>
      <span class="sub" v-if="season">Season: {{ season }}</span>
    </div>

    <div v-if="loading" class="empty">Loading…</div>
    <div v-else class="grid">
      <RankingCard title="Points Per Game"   :rows="tops.points"   colLabel="PTS" />
      <RankingCard title="Rebounds Per Game" :rows="tops.rebounds" colLabel="REB" />
      <RankingCard title="Assists Per Game"  :rows="tops.assists"  colLabel="AST" />
      <RankingCard title="Steals Per Game"   :rows="tops.steals"   colLabel="STL" />
      <RankingCard title="Blocks Per Game"   :rows="tops.blocks"   colLabel="BLK" />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useRoute } from 'vue-router'
import api from '@/api/axios'
import RankingCard from '@/components/RankingCard.vue'

const route = useRoute()
const divisionParam = computed(() => String(route.params.division || 'champ').toLowerCase())
const DIV_MAP   = { champ: 'champion', d1: 'd1', d2: 'd2' }
const TITLE_MAP = { champ: 'Championship', d1: 'Division 1', d2: 'Division 2' }

const apiCode = computed(() => DIV_MAP[divisionParam.value] || 'champion')
const title   = computed(() => TITLE_MAP[divisionParam.value] || 'Championship')

const loading = ref(false)
const season  = ref('')
const tops    = ref({ points:[], rebounds:[], assists:[], steals:[], blocks:[] })

// 名字统一处理 + 过滤掉 fill in
const normName = (s) =>
  (s || '')
    .toLowerCase()
    .replace(/[_-]+/g, ' ')
    .replace(/\s+/g, ' ')
    .trim()

function scrubBoard(arr = []) {
  const cleaned = (arr || []).filter(r => {
    const n = normName(r.player)
    return n !== 'fill in' && n !== 'fillin'
  })
  cleaned.forEach((r, i) => { r.rank = i + 1 })
  return cleaned
}

async function load () {
  loading.value = true
  try {
    const data = await api.get(`/divisions/${apiCode.value}/player-rankings?top=10`)
    console.log('[ranking]', data)

    season.value = data?.season || data?.season_code || ''

    const group = (data && typeof data.top === 'object' && data.top) || data

    // ✅ 在这里过滤
    tops.value = {
      points:   scrubBoard(group?.points   || []),
      rebounds: scrubBoard(group?.rebounds || []),
      assists:  scrubBoard(group?.assists  || []),
      steals:   scrubBoard(group?.steals   || []),
      blocks:   scrubBoard(group?.blocks   || []),
    }
  } finally {
    loading.value = false
  }
}

watch(() => route.params.division, load, { immediate: true })
</script>

<style scoped>
.page {
  padding: 24px;
  min-height: 100vh;
  background: url('/images/basketball.jpg') no-repeat center center fixed;
  background-size: cover;
}

.head {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
  background: rgba(255,255,255,0.8);
  padding: 8px 12px;
  border-radius: 8px;
}

.grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 16px;
}

.empty {
  color: #6b7280;
  padding: 8px 0;
}
</style>
