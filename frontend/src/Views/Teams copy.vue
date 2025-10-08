<!-- src/views/Teams.vue -->
<template>
  <div class="teams-page">
    <!-- ===== 内容主体 ===== -->
    <div class="page-wrap">
      <!-- Champion -->
      <section v-if="sections.champion.length" class="section">
        <h2 class="section-title">Champion</h2>
        <div class="divider"></div>
        <div class="grid">
          <div v-for="t in sections.champion" :key="t.id" class="cell">
            <img class="logo" :src="t.logo" alt="" @error="onImgError($event)" />
            <div class="name">{{ t.name }}</div>
          </div>
        </div>
      </section>

      <!-- Division 1 -->
      <section v-if="sections.d1.length" class="section">
        <h2 class="section-title">Division 1</h2>
        <div class="divider"></div>
        <div class="grid">
          <div v-for="t in sections.d1" :key="t.id" class="cell">
            <img class="logo" :src="t.logo" alt="" @error="onImgError($event)" />
            <div class="name">{{ t.name }}</div>
          </div>
        </div>
      </section>

      <!-- Division 2 -->
      <section v-if="sections.d2.length" class="section">
        <h2 class="section-title">Division 2</h2>
        <div class="divider"></div>
        <div class="grid">
          <div v-for="t in sections.d2" :key="t.id" class="cell">
            <img class="logo" :src="t.logo" alt="" @error="onImgError($event)" />
            <div class="name">{{ t.name }}</div>
          </div>
        </div>
      </section>

      <div v-if="loading" class="loading">Loading…</div>
      <div v-if="error" class="error">{{ error }}</div>
    </div>

  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import axios from 'axios'

/** 用赛季 code，而不是 season_id。和后端 list_teams 的参数一致 */
const CURRENT_SEASON_CODE = import.meta.env.VITE_SEASON_CODE || '2025-S8'
const FILE_BASE = import.meta.env.VITE_FILE_BASE || ''

const loading = ref(false)
const error = ref('')
const sections = reactive({ champion: [], d1: [], d2: [] })

function resolveLogo(logo) {
  if (!logo) return '/static/defaults/team-logo.png'
  const isAbs = /^https?:\/\//i.test(logo)
  return isAbs ? logo : `${FILE_BASE}${logo.startsWith('/') ? '' : '/'}${logo}`
}

/** 前端归一分区（后端可能返回 'D1' / 'D2' / 'champion' / 中文等） */
function normalizeDiv(v) {
  const x = String(v || '').trim().toLowerCase()
  if (['d1', 'division 1', '1'].includes(x)) return 'd1'
  if (['d2', 'division 2', '2'].includes(x)) return 'd2'
  if (['champion', 'champ', 'c', '冠军'].includes(x)) return 'champion'
  return x
}

onMounted(async () => {
  loading.value = true
  error.value = ''
  try {
    // ✅ 正确接口：/api/teams?season=2025-S8
    const { data } = await axios.get('/api/teams', {
      params: { season: CURRENT_SEASON_CODE },
    })
    const all = (data || []).map(t => ({
      id: t.id ?? t.team_id ?? t.name,
      name: t.name,
      logo: resolveLogo(t.logo_url || t.logo || t.logoPath),
      division: normalizeDiv(t.division),
    }))

    sections.champion = all.filter(t => t.division === 'champion')
    sections.d1       = all.filter(t => t.division === 'd1')
    sections.d2       = all.filter(t => t.division === 'd2')
  } catch (e) {
    console.error(e)
    error.value = e?.message || 'Failed to load teams'
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
/* ===== 页面与主体（图二风格） ===== */
.teams-page {
  width: 100%;
  min-height: 100vh;
  background: #f3f3f3;     /* 贴近图二浅灰 */
  display: flex;
  flex-direction: column;
}

.page-wrap {
  max-width: 960px;        /* 图二版心 */
  margin: 0 auto;
  padding: 24px 16px 60px; /* 底部给 footer 留间距 */
}

.section { margin-bottom: 48px; }

.section-title {
  font-size: 26px;
  font-weight: 800;
  text-align: center;      /* 图二标题居中 */
  margin: 8px 0 8px;
}

.divider {
  height: 1px;
  width: 100%;
  background: #d9d9d9;
  margin: 6px 0 18px;
}

/* 三列、列间距大（图二那种稀疏感） */
.grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  column-gap: 120px;
  row-gap: 28px;
}

@media (max-width: 980px)  { .grid { column-gap: 80px;  } }
@media (max-width: 900px)  { .grid { grid-template-columns: repeat(2, minmax(0, 1fr)); column-gap: 60px; } }
@media (max-width: 600px)  { .grid { grid-template-columns: 1fr; column-gap: 24px; } }

.cell {
  display: flex;
  align-items: center;
  gap: 10px;
}

/* 队徽更小、无阴影、轻圆角（贴近图二） */
.logo {
  width: 50px;
  height: 50px;
  object-fit: cover;
  border-radius: 6px;
  background: #fff;
  box-shadow: none;
}

.name {
  font-size: 18px;
  font-weight: 600;
  line-height: 1.2;
  color: #111;
}

.loading { margin-top: 16px; color: #666; text-align:center; }
.error   { margin-top: 16px; color: #d33; text-align:center; }



</style>
