<!-- src/views/TeamRoster.vue -->
<template>
  <div class="roster-page">
    <div class="topbar">
      <button class="btn-back" @click="$router.back()">← Back</button>

      <div class="title-wrap">
        <h1 class="team-name">{{ team?.name || 'Team' }}</h1>
        <span v-if="divisionName" class="chip">{{ divisionName }}</span>
      </div>

      <button
        v-if="team?.id"
        class="btn-primary"
        @click="$router.push({ name: 'teamSchedule', params: { id: team.id } })"
      >
        📅 View Team Schedule
      </button>
    </div>

    <div class="card">
      <table class="table">
        <thead>
          <tr>
            <th style="width:60px">#</th>
            <th>Name</th>
            <th style="width:120px">Number</th>
            <th style="width:30%">Note</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(p, idx) in players" :key="p.id || idx">
            <td>{{ idx + 1 }}</td>
            <td>{{ p.name }}</td>
            <td>{{ p.number ?? p.no ?? '-' }}</td>
            <td>{{ p.note || '-' }}</td>
          </tr>
          <tr v-if="!loading && players.length === 0">
            <td colspan="4" class="empty">No players yet.</td>
          </tr>
        </tbody>
      </table>
      <div v-if="loading" class="hint">Loading…</div>
      <div v-if="error" class="error">Failed: {{ error }}</div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref, computed } from 'vue'
import axios from 'axios'
import { useRoute } from 'vue-router'

const route = useRoute()
const teamId = Number(route.params.id)

const loading = ref(false)
const error = ref('')
const team = ref(null)
const players = ref([])

/** 拉团队基本信息（含 division） */
async function fetchTeam() {
  const { data } = await axios.get(`/api/teams/${teamId}`)
  team.value = data
}

const divisionName = computed(() => team.value?.division?.name || null)

/** 拉队员列表：沿用你 admin 页面用的接口 */
async function fetchPlayers() {
  const { data } = await axios.get(`/api/teams/${teamId}/players`)
  // 兼容不同字段命名
  players.value = (data?.players || data || []).map(x => ({
    id: x.id ?? x.player_id,
    name: x.name,
    number: x.number ?? x.jersey_no ?? x.no,
    note: x.note,
  }))
}

onMounted(async () => {
  loading.value = true
  error.value = ''
  try {
    await Promise.all([fetchTeam(), fetchPlayers()])
  } catch (e) {
    error.value = e?.message || 'Load failed'
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.roster-page {
  max-width: 1080px;
  margin: 0 auto;
  padding: 24px 16px 48px;
  background: #f6f7f9;
}

.topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 16px;
}

.btn-back {
  border: 1px solid #d5d9e0;
  background: #fff;
  border-radius: 10px;
  padding: 8px 14px;
  cursor: pointer;
}

.title-wrap { display: flex; align-items: center; gap: 12px; }
.team-name { margin: 0; font-size: 24px; font-weight: 800; }
.chip {
  background: #eef2ff;
  color: #3b5bfd;
  border-radius: 999px;
  padding: 6px 10px;
  font-size: 12px;
  font-weight: 700;
}

.btn-primary {
  background: #1e40af;
  color: #fff;
  border: none;
  border-radius: 12px;
  padding: 10px 16px;
  font-weight: 700;
  cursor: pointer;
}

.card {
  background: #fff;
  border: 1px solid #e5e7eb;
  border-radius: 14px;
  padding: 12px;
}

.table { width: 100%; border-collapse: collapse; }
.table thead th {
  text-align: left;
  font-weight: 800;
  padding: 12px 14px;
  border-bottom: 1px solid #e5e7eb;
  background: #fafafa;
}
.table tbody td {
  padding: 14px;
  border-bottom: 1px solid #f1f1f1;
}
.empty { text-align: center; color: #777; }

.hint { padding: 12px; color: #666; }
.error { padding: 12px; color: #c0392b; }
</style>
