<!-- src/views/Teams.vue -->
<template>
  <div class="teams-page">
    <div class="page-wrap">
      <!-- Champion -->
      <section v-if="sections.champion.length" class="section">
        <h2 class="section-title">Champion</h2>
        <div class="divider"></div>
        <div class="grid">
          <router-link
            v-for="t in sections.champion"
            :key="t.id"
            class="cell link-cell"
            :to="{ name: 'teamRosterPublic', params: { id: t.id } }"
          >
            <img class="logo" :src="t.logo" alt="" @error="onImgError" />
            <div class="name">{{ t.name }}</div>
          </router-link>
        </div>
      </section>

      <!-- Division 1 -->
      <section v-if="sections.d1.length" class="section">
        <h2 class="section-title">Division 1</h2>
        <div class="divider"></div>
        <div class="grid">
          <router-link
            v-for="t in sections.d1"
            :key="t.id"
            class="cell link-cell"
            :to="{ name: 'teamRosterPublic', params: { id: t.id } }"
          >
            <img class="logo" :src="t.logo" alt="" @error="onImgError" />
            <div class="name">{{ t.name }}</div>
          </router-link>
        </div>
      </section>

      <!-- Division 2 -->
      <section v-if="sections.d2.length" class="section">
        <h2 class="section-title">Division 2</h2>
        <div class="divider"></div>
        <div class="grid">
          <router-link
            v-for="t in sections.d2"
            :key="t.id"
            class="cell link-cell"
            :to="{ name: 'teamRosterPublic', params: { id: t.id } }"
          >
            <img class="logo" :src="t.logo" alt="" @error="onImgError" />
            <div class="name">{{ t.name }}</div>
          </router-link>
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
import defaultLogo from '@/assets/images/default-team.png' // ✅ 本地占位图（务必存在）

const CURRENT_SEASON_CODE = import.meta.env.VITE_SEASON_CODE || '2025-S8'
const FILE_BASE = (import.meta.env.VITE_FILE_BASE || '').replace(/\/+$/,'') // 去掉尾部斜杠

const loading = ref(false)
const error = ref('')
const sections = reactive({ champion: [], d1: [], d2: [] })

/** 规范化 logo：空 → 占位；相对 → FILE_BASE + path；绝对(http/https) → 原样 */
function resolveLogo(logo) {
  if (!logo || String(logo).trim() === '') return defaultLogo
  const url = String(logo)
  if (/^https?:\/\//i.test(url)) return url
  const path = url.replace(/^\/+/, '') // 去掉多余开头斜杠
  return `${FILE_BASE}/${path}`
}

/** 防止 onerror 死循环：只降级一次 + 取消监听器 */
function onImgError(e) {
  const img = e.target
  if (img.__fallbackDone) return      // 已降级过
  img.__fallbackDone = true           // 内存标记
  img.onerror = null                  // 关键：取消 onerror，避免再次触发
  img.src = defaultLogo
}

/** 后端 division 归一 */
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
    const { data } = await axios.get('/api/teams', { params: { season: CURRENT_SEASON_CODE } })
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
.teams-page { width: 100%; min-height: 100vh; background: #f3f3f3; display: flex; flex-direction: column; }
.page-wrap   { max-width: 960px; margin: 0 auto; padding: 24px 16px 60px; }

.section { margin-bottom: 48px; }
.section-title { font-size: 26px; font-weight: 800; text-align: center; margin: 8px 0 8px; }
.divider { height: 1px; width: 100%; background: #d9d9d9; margin: 6px 0 18px; }

.grid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); column-gap: 120px; row-gap: 28px; }
@media (max-width: 980px){ .grid{ column-gap: 80px; } }
@media (max-width: 900px){ .grid{ grid-template-columns: repeat(2, minmax(0, 1fr)); column-gap: 60px; } }
@media (max-width: 600px){ .grid{ grid-template-columns: 1fr; column-gap: 24px; } }

.cell { display: flex; align-items: center; gap: 10px; }
.logo { width: 50px; height: 50px; object-fit: cover; border-radius: 6px; background: #fff; box-shadow: none; }
.name { font-size: 18px; font-weight: 600; line-height: 1.2; color: #111; }

/* 可点击的视觉反馈 */
.link-cell { text-decoration: none; color: inherit; cursor: pointer; transition: transform .06s ease; }
.link-cell .name { text-decoration: underline; }
.link-cell:hover { transform: translateY(-1px); }
.link-cell:hover .name { text-decoration: underline; }

.loading { margin-top: 16px; color: #666; text-align:center; }
.error   { margin-top: 16px; color: #d33; text-align:center; }
</style>
