<!-- src/views/admin/PlayersManage.vue -->
<template>
  <div class="page">
    <!-- 顶部 Header -->
    <div class="header">
      <button class="btn light" @click="goBack">← Back</button>

      <!-- 球队信息 -->
      <div class="team-info" v-if="team">
        <img v-if="team.logo_url" class="team-logo" :src="team.logo_url" alt="Team Logo" />
        <div v-else class="team-logo placeholder">—</div>
        <h1>{{ team.name }}</h1>
      </div>

      <div class="fill"></div>

      <!-- Division 徽章 -->
      <span class="chip division" v-if="divisionLabel">{{ divisionLabel }}</span>
    </div>

    <!-- 工具栏 -->
    <div class="toolbar">
      <button class="btn" @click="openCreate">
        <span class="icon">＋</span> Add Player
      </button>

      <!-- Champion 走 adminChampionTeamSchedule；其余走 teamScheduleAdminAlias -->
      <RouterLink
        class="btn"
        :to="{
          name: scheduleRouteName,
          params: { id: teamId },
          query: { from: 1, to: 11, division: divisionCode || undefined }
        }"
      >
        <span class="icon">🗓</span> View Team Schedule
      </RouterLink>

      <span v-if="loading" class="loading">Loading…</span>
    </div>

    <!-- 球员表格 -->
    <div class="table">
      <div class="thead">
        <div class="th idx">#</div>
        <div class="th name">Name</div>
        <div class="th num">Number</div>
        <div class="th note">Note</div>
        <div class="th act">Actions</div>
      </div>

      <div v-if="players.length === 0 && !loading" class="empty">No players yet</div>

      <div v-for="(p, i) in players" :key="p.id" class="row">
        <div class="td idx">{{ i + 1 }}</div>
        <div class="td name">{{ p.name }}</div>
        <div class="td num">{{ p.number || '-' }}</div>
        <div class="td note">{{ p.note || '-' }}</div>
        <div class="td act">
          <button class="btn manage" @click="onEdit(p)">Edit</button>
          <button class="btn danger" @click="onDelete(p)">Delete</button>
        </div>
      </div>
    </div>

    <!-- 新增 / 编辑球员弹窗 -->
    <div v-if="showModal" class="modal-mask" @click.self="closeModal">
      <div class="modal">
        <h3>{{ editMode ? 'Edit Player' : 'Add Player' }}</h3>

        <div class="form">
          <label class="label">Name <span class="req">*</span></label>
          <input class="input" v-model.trim="form.name" type="text" placeholder="e.g., Stephen Curry" />
          <label class="label">Number</label>
          <input class="input" v-model.number="form.number" type="number" placeholder="30" />
          <label class="label">Note</label>
          <input class="input" v-model.trim="form.note" type="text" placeholder="Optional" />
        </div>

        <div class="modal-actions">
          <button class="btn light" @click="closeModal">Cancel</button>
          <button class="btn" :disabled="saving" @click="onSave">{{ saving ? 'Saving…' : 'Save' }}</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter, RouterLink } from 'vue-router'
import api from '@/api/axios'
import { fetchTeamSchedule } from '@/api/schedule'

const route = useRoute()
const router = useRouter()

const teamId = Number(route.params.id)
const team = ref(null)
const loading = ref(false)
const saving = ref(false)
const players = ref([])

const showModal = ref(false)
const editMode = ref(false)
const form = ref({ id: null, name: '', number: null, note: '' })

// ========== Division 处理 ==========
const apiDivisionCode = ref(null)

const normDiv = (x) => {
  const v = String(x || '').trim().toLowerCase()
  if (['d1', 'division1', '1'].includes(v)) return 'd1'
  if (['d2', 'division2', '2'].includes(v)) return 'd2'
  if (['champion', 'champ', 'c', 'championship'].includes(v)) return 'champion'
  return ''
}

const divisionCode = computed(() => {
  const q = normDiv(route.query.division)
  if (q) return q
  if (apiDivisionCode.value) return apiDivisionCode.value
  return null
})

const divisionLabel = computed(() => {
  const map = { d1: 'Division 1', d2: 'Division 2', champion: 'Champion' }
  return map[divisionCode.value] || null
})

// 根据 division 选择路由名字
const scheduleRouteName = computed(() =>
  divisionCode.value === 'champion' ? 'adminChampionTeamSchedule' : 'teamSchedule'
)

// 返回上一页
const goBack = () => router.push('/admin-panel/teams')

// 打开新增
const openCreate = () => {
  editMode.value = false
  form.value = { id: null, name: '', number: null, note: '' }
  showModal.value = true
}

// 打开编辑
const onEdit = (player) => {
  editMode.value = true
  form.value = { ...player }
  showModal.value = true
}

// 关闭弹窗
const closeModal = () => (showModal.value = false)

// 保存
const onSave = async () => {
  if (!form.value.name.trim()) {
    return alert('Please enter player name')
  }
  saving.value = true
  try {
    if (editMode.value) {
      await api.put(`/players/${form.value.id}`, { ...form.value, team_id: teamId })
    } else {
      await api.post('/players', { ...form.value, team_id: teamId })
    }
    await fetchPlayers()
    closeModal()
  } catch (e) {
    console.error('Save failed', e)
    alert('Save failed')
  } finally {
    saving.value = false
  }
}

// 删除
const onDelete = async (player) => {
  if (!confirm(`Delete player "${player.name}"?`)) return
  try {
    await api.delete(`/players/${player.id}`)
    players.value = players.value.filter((p) => p.id !== player.id)
  } catch (e) {
    console.error('Delete failed', e)
    alert('Delete failed')
  }
}

// 获取球队信息
const fetchTeamInfo = async () => {
  try {
    const data = await api.get(`/teams/${teamId}`)
    team.value = data || null
  } catch (e) {
    console.error('Failed to fetch team info', e)
  }
}

// 获取球员列表
const fetchPlayers = async () => {
  loading.value = true
  try {
    const list = await api.get(`/teams/${teamId}/players`)
    players.value = Array.isArray(list) ? list : []
  } finally {
    loading.value = false
  }
}

// 获取 division（若路由未显式带 division，则从公开赛程接口拿）
const fetchDivision = async () => {
  const qDiv = normDiv(route.query.division)
  if (qDiv) {
    apiDivisionCode.value = qDiv
    return
  }
  try {
    const data = await fetchTeamSchedule(teamId, 1, 1) // 取一条即可
    apiDivisionCode.value = normDiv(data?.division?.code)
  } catch (e) {
    console.error('Failed to fetch division', e)
  }
}

onMounted(async () => {
  await Promise.all([fetchTeamInfo(), fetchPlayers(), fetchDivision()])
})
</script>

<style scoped>
.page { padding: 24px; }

.header { display: flex; align-items: center; gap: 16px; margin-bottom: 20px; }
.fill { flex: 1; }

.team-info { display: flex; align-items: center; gap: 12px; }
.team-logo { width: 40px; height: 40px; border-radius: 8px; object-fit: cover; border: 1px solid #ddd; background: #f3f4f6; }
.team-logo.placeholder { display: flex; align-items: center; justify-content: center; font-size: 18px; color: #aaa; }
.team-info h1 { font-size: 22px; font-weight: 700; }

.chip{ font-size:12px; font-weight:900; padding:4px 10px; border-radius:9999px;
  border:1px solid #e5e7eb; background:#f8fafc; color:#334155; white-space:nowrap; }
.chip.division{ background:#eef2ff; border-color:#e0e7ff; color:#3730a3; }

.toolbar { display: flex; gap: 12px; margin-bottom: 12px; }
.loading { color: #6b7280; font-size: 14px; }

.btn { height: 36px; padding: 0 14px; border-radius: 10px; border: 1px solid #e5e7eb; background: #111827; color: #fff; cursor: pointer; display: inline-flex; align-items: center; justify-content: center; }
.btn:hover { opacity: 0.95; }
.btn.light { background: #fff; color: #111827; }
.btn.danger { background: #ef4444; border-color: #ef4444; }
.btn.manage { background: #3b82f6; border-color: #3b82f6; }
.btn .icon { margin-right: 8px; font-weight: 700; }

.table { background: #fff; border: 1px solid #eee; border-radius: 16px; overflow: hidden; }
.thead, .row { display: grid; grid-template-columns: 60px 1fr 100px 100px 200px; align-items: center; }
.thead { background: #f8fafc; font-weight: 700; }
.th, .td { padding: 12px 14px; border-bottom: 1px solid #f1f5f9; }
.empty { padding: 20px; color: #6b7280; text-align: center; }
.idx { text-align: center; }
.act { display: flex; gap: 8px; }

.modal-mask { position: fixed; inset: 0; background: rgba(0, 0, 0, 0.35); display: flex; align-items: center; justify-content: center; }
.modal { width: 480px; background: #fff; border-radius: 16px; padding: 16px; }
.modal h3 { margin-bottom: 12px; }
.form { display: grid; gap: 8px; }
.label { font-size: 13px; color: #374151; }
.req { color: #ef4444; }
.input { height: 36px; border: 1px solid #e5e7eb; border-radius: 10px; padding: 0 10px; outline: none; }
.input:focus { border-color: #111827; }
.modal-actions { display: flex; justify-content: flex-end; gap: 10px; margin-top: 14px; }
</style>
