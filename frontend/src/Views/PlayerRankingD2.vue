<template>
  <div class="page">
    <div class="head">
      <h1>Player Ranking · Division 2</h1>
      <div class="fill"></div>
      <span class="sub" v-if="season">Season: {{ season }}</span>
    </div>

    <div v-if="loading" class="empty">Loading…</div>
    <div v-else class="grid one">
      <!-- 这里传过去的就是已经过滤后的 rows -->
      <RankingCard title="Points Per Game" :rows="tops.points" colLabel="PTS" />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '@/api/axios'
import RankingCard from '@/components/RankingCard.vue'

const loading = ref(false)
const season  = ref('')
const tops    = ref({ points: [] })

// 名字规范化：忽略大小写、下划线、短横线、连续空格
const normName = (s) =>
  (s || '')
    .toLowerCase()
    .replace(/[_-]+/g, ' ')
    .replace(/\s+/g, ' ')
    .trim()

// 过滤 + 重新编号 rank（保持现有排序顺序）
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
    const data = await api.get(`/divisions/d2/player-rankings?top=10`)
    console.log('D2 ranking data', data)

    // 赛季字段兜底
    season.value = data?.season || data?.season_id || ''

    // 兼容 champion 的 { top: { points: [] } } 与 D1/D2 的 { points: [] }
    const rawPoints = (data?.top && data.top.points) ?? data?.points ?? []
    // ✅ 前端保险丝：过滤掉 fill in / fillin，并重排 rank
    tops.value.points = scrubBoard(Array.isArray(rawPoints) ? rawPoints : [])
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>

<style scoped>
.page {
  padding: 24px;
  min-height: 100vh;
  background: url('/images/basketball.jpg') no-repeat center center fixed;
  background-size: cover;
}

.head{ display:flex; align-items:center; gap:12px; margin-bottom:12px; }
.head h1{ margin:0; font-weight:800; font-size:22px; color:#fff; }
.fill{ flex:1; }
.sub{ color:#334155; }
.empty{ color:#6b7280; padding:8px 0; }

.grid{
  display:grid;
  grid-template-columns: minmax(320px, 680px);
  gap:16px;
}
</style>
