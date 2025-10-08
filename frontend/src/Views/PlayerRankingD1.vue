  <template>
    <div class="page">
      <div class="head">
        <h1>Player Ranking · Division 1</h1>
        <div class="fill"></div>
        <span class="sub" v-if="season">Season: {{ season }}</span>
      </div>

      <div v-if="loading" class="empty">Loading…</div>
      <div v-else class="grid one">
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
    const data = await api.get(`/divisions/d1/player-rankings?top=10`)
    console.log('D1 ranking data', data)
    season.value = data?.season || data?.season_id || ''
    const points = (data?.top && data.top.points) ?? data?.points ?? []
    tops.value.points = scrubBoard(Array.isArray(points) ? points : [])
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
