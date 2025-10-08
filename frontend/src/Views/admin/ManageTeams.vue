<template>
  <div class="page">
    <div class="page-head">
      <div>
        <h1>Team Management</h1>
        <p class="muted">Add or remove teams here.</p>
      </div>

      <div class="toolbar">
        <button class="btn" @click="openCreate">➕ Add Team</button>
        <button class="btn primary" :disabled="!hasDirty || saving" @click="saveAll">
          {{ saving ? 'Saving…' : 'Save Changes' }}
        </button>
        <span v-if="loading" class="loading">Loading…</span>
      </div>
    </div>

    <!-- Table -->
    <div class="table">
      <div class="thead">
        <div class="th idx">#</div>
        <div class="th logo">Logo</div>
        <div class="th name">Team Name</div>
        <div class="th div">Division</div>
        <div class="th act">Actions</div>
      </div>

      <div v-if="teams.length === 0 && !loading" class="empty">No data</div>

      <div
        v-for="(t, i) in teams"
        :key="t.id"
        class="row"
        :class="{ pendingDelete: t._pendingDelete }"
      >
        <div class="td idx">{{ i + 1 }}</div>

        <!-- Logo column: only shown when there is a link -->
        <div class="td logo">
          <img
            v-if="t.logo_url && !t._logoBroken && !t._pendingDelete"
            :src="resolveFileUrl(t.logo_url)"
            alt="logo"
            class="logo-img"
            @error="t._logoBroken = true"
          />
        </div>

        <!-- Name column -->
        <div class="td name">
          <input
            class="cell-input"
            v-model="t.name"
            :disabled="t._pendingDelete"
            @input="markDirty(t, 'name')"
            :class="{ dirty: t._dirty?.name }"
            placeholder="Team name"
          />
        </div>

        <!-- Division column -->
        <div class="td div">
          <select
            class="cell-select"
            v-model="t.division"
            :disabled="t._pendingDelete"
            @change="markDirty(t, 'division')"
            :class="{ dirty: t._dirty?.division }"
          >
            <option v-for="opt in divisionOptions" :key="opt.value" :value="opt.value">
              {{ opt.label }}
            </option>
          </select>
        </div>

        <!-- Actions column -->
        <div class="td act">
          <input
            type="file"
            accept="image/png,image/jpeg"
            class="file-input-hidden"
            :ref="el => fileInputs[t.id] = el"
            @change="e => onUploadLogoFile(t, e)"
          />
          <button class="btn light" :disabled="t._pendingDelete" @click="triggerUpload(t.id)">
            Upload Logo
          </button>

          <button class="btn danger" v-if="!t._pendingDelete" @click="markDelete(t)">Delete</button>
          <button class="btn light" v-else @click="undoDelete(t)">Undo</button>

          <button class="btn manage" :disabled="t._pendingDelete" @click="onManagePlayers(t)">
            Manage Players
          </button>
        </div>
      </div>
    </div>

    <!-- Create Team modal -->
    <div v-if="showCreate" class="modal-mask" @click.self="closeCreate">
      <div class="modal">
        <h3>Add Team</h3>

        <div class="form">
          <div class="field">
            <label class="label">Team Name <span class="req">*</span></label>
            <input class="input" v-model.trim="form.name" type="text" placeholder="e.g., Box Hill Tigers" />
          </div>

          <div class="field">
            <label class="label">Division <span class="req">*</span></label>
            <select class="input" v-model="form.division">
              <option v-for="opt in divisionOptions" :key="opt.value" :value="opt.value">
                {{ opt.label }}
              </option>
            </select>
          </div>

          <div class="field">
            <label class="label">Team Logo (PNG / JPG)</label>
            <input class="input-file" type="file" accept="image/png,image/jpeg" @change="onCreateFile" />
          </div>

          <div class="field">
            <label class="label">Notes</label>
            <input class="input" v-model.trim="form.note" type="text" placeholder="Optional" />
          </div>
        </div>

        <div class="modal-actions">
          <button class="btn light" @click="closeCreate">Cancel</button>
          <button class="btn" @click="applyCreate">Add to List (Pending Save)</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/api/axios'

const SEASON_CODE = '2025-S8'

const router = useRouter()
const loading = ref(false)
const saving  = ref(false)
const teams   = ref([])

// 触发每行隐藏 file input
const fileInputs = ref({})

// 分区选项（值以 code 形式统一）
const divisionOptions = [
  { value: 'champion', label: 'Champion' },
  { value: 'D1', label: 'Division 1' },
  { value: 'D2', label: 'Division 2' },
]

// —— 统一图片 URL：DB 存 path（/static/...），前端拼完整地址 —— //
const API_BASE = api?.defaults?.baseURL || ''                 // e.g. http://localhost:3001/api
const FILE_HOST = API_BASE.replace(/\/api\/?$/, '') || ''     // e.g. http://localhost:3001
const resolveFileUrl = (u) => {
  if (!u) return ''
  if (/^https?:\/\//i.test(u)) return u
  if (u.startsWith('/static')) return `${FILE_HOST}${u}`
  return u
}

// —— 分区值规范化（兜底） —— //
const normalizeDivision = (v) => {
  if (v == null) return null
  const s = String(v).trim().toLowerCase()
  if (s === 'd1' || s === 'division 1' || s === '1') return 'D1'
  if (s === 'd2' || s === 'division 2' || s === '2') return 'D2'
  if (s === 'champion' || s === '冠军' || s === 'c') return 'champion'
  return v
}

// ====== 新增弹窗 ======
const showCreate = ref(false)
const form = ref({ name: '', division: 'D1', logo_url: '', note: '' })
const openCreate = () => { form.value = { name: '', division: 'D1', logo_url: '', note: '' }; showCreate.value = true }
const closeCreate = () => (showCreate.value = false)

// 新增上传：存 path
const onCreateFile = async (e) => {
  const file = e.target.files?.[0]
  if (!file) return
  if (!['image/png', 'image/jpeg'].includes(file.type)) { alert('仅支持 PNG 或 JPG'); return }
  try {
    const fd = new FormData()
    fd.append('file', file)
    const res = await api.post('/uploads', fd, { headers: { 'Content-Type': 'multipart/form-data' } })
    form.value.logo_url = res?.data?.path || res?.data?.url || res?.path || res?.url
  } catch (err) {
    console.error(err); alert('上传失败')
  }
}

const applyCreate = () => {
  if (!form.value.name.trim()) return alert('请输入球队名称')
  if (!form.value.division) return alert('请选择分区')

  const tempId = -(Date.now())
  teams.value.push({
    id: tempId,
    name: form.value.name.trim(),
    division: form.value.division,
    logo_url: form.value.logo_url || null,
    note: form.value.note || null,
    season: SEASON_CODE,
    _logoBroken: false,
    _pendingCreate: true,
    _pendingDelete: false,
    _original: { name: '', division: '', logo_url: null },
    _dirty: { name: true, division: true, logo_url: !!form.value.logo_url }
  })
  closeCreate()
}

// ====== 列表 & 行内编辑 ======
const fetchTeams = async () => {
  loading.value = true
  try {
    const data = await api.get('/teams', { params: { season: SEASON_CODE } })
    teams.value = (Array.isArray(data) ? data : []).map(t => {
      const div = normalizeDivision(t.division)   // ★ 兜底规范化
      return {
        ...t,
        division: div,
        _logoBroken: false,
        _pendingCreate: false,
        _pendingDelete: false,
        _original: { name: t.name, division: div, logo_url: t.logo_url },
        _dirty: {}
      }
    })
  } catch (e) {
    console.error(e); alert('获取球队列表失败')
  } finally {
    loading.value = false
  }
}

const markDirty = (row, field) => {
  if (row._pendingCreate) { row._dirty[field] = true; return }
  const changed = row[field] !== row._original[field]
  if (changed) row._dirty[field] = true
  else delete row._dirty[field]
}

const markDelete = (row) => {
  if (row._pendingCreate) teams.value = teams.value.filter(t => t.id !== row.id)
  else row._pendingDelete = true
}
const undoDelete = (row) => { row._pendingDelete = false }

const triggerUpload = (teamId) => {
  const el = fileInputs.value[teamId]
  if (el) el.click()
}

// 行内上传 Logo：存 path，立刻预览
const onUploadLogoFile = async (row, e) => {
  const file = e.target.files?.[0]
  if (!file) return
  if (!['image/png', 'image/jpeg'].includes(file.type)) { alert('仅支持 PNG 或 JPG'); e.target.value = ''; return }
  try {
    const fd = new FormData()
    fd.append('file', file)
    const res = await api.post('/uploads', fd, { headers: { 'Content-Type': 'multipart/form-data' } })
    const path = res?.data?.path || res?.path || res?.data?.url || res?.url
    if (!path) throw new Error('上传返回缺少 path/url')
    row.logo_url = path
    row._logoBroken = false
    markDirty(row, 'logo_url')
  } catch (err) {
    console.error(err); alert('上传失败')
  } finally {
    e.target.value = ''
  }
}

// ====== Save Edit：统一提交 ======
const hasDirty = computed(() =>
  teams.value.some(t => t._pendingCreate || t._pendingDelete || Object.keys(t._dirty).length > 0)
)

const saveAll = async () => {
  if (!hasDirty.value) return
  saving.value = true
  try {
    // 1) 新增
    for (const row of teams.value.filter(t => t._pendingCreate)) {
      const payload = {
        name: row.name?.trim(),
        division: row.division,
        logo_url: row.logo_url || null,
        note: row.note || null,
        season: SEASON_CODE,
      }
      const created = await api.post('/teams', payload)
      row.id = created?.id ?? row.id
      row._pendingCreate = false
      row._original = { name: row.name, division: row.division, logo_url: row.logo_url }
      row._dirty = {}
    }

    // 2) 修改 —— 只要有改动，就总是带上 season + 当前 division（确保映射写入）
    for (const row of teams.value.filter(t => !t._pendingCreate && !t._pendingDelete)) {
      const fields = Object.keys(row._dirty || {})
      if (fields.length > 0) {
        const payload = {}
        fields.forEach(f => (payload[f] = row[f] ?? null))
        payload.season = SEASON_CODE
        if (row.division) payload.division = row.division

        await api.patch(`/teams/${row.id}`, payload)
        row._original = { ...row._original, ...payload }
        row._dirty = {}
      } else {
        // 历史数据兜底：这一季没映射就补一次
        if ((row._original?.division == null) && row.division) {
          await api.patch(`/teams/${row.id}`, { season: SEASON_CODE, division: row.division })
          row._original = { ...row._original, division: row.division }
        }
      }
    }

    // 3) 删除
    const toDelete = teams.value.filter(t => t._pendingDelete && !t._pendingCreate)
    for (const row of toDelete) await api.delete(`/teams/${row.id}`)
    teams.value = teams.value.filter(t => !t._pendingDelete)

    alert('已保存修改')
  } catch (e) {
    console.error(e); alert('保存失败，请重试')
  } finally {
    saving.value = false
  }
}

// 其它
const onManagePlayers = (team) => router.push(`/admin-panel/teams/${team.id}/players`)

const beforeUnload = (e) => { if (hasDirty.value) { e.preventDefault(); e.returnValue = '' } }
onMounted(() => { fetchTeams(); window.addEventListener('beforeunload', beforeUnload) })
onBeforeUnmount(() => window.removeEventListener('beforeunload', beforeUnload))
</script>

<style scoped>
.page { padding: 24px; }
.page-head { display:flex; align-items:center; justify-content:space-between; gap:16px; }
h1 { margin: 0 0 8px; font-size: 28px; font-weight: 800; }
.muted { color:#6b7280; margin-bottom: 0; }

.toolbar { display:flex; gap:12px; align-items:center; }
.loading { color:#6b7280; font-size: 14px; }

.btn { height:36px; padding:0 12px; border-radius:10px; border:1px solid #e5e7eb; background:#111827; color:#fff; cursor:pointer; }
.btn:hover { opacity:.95; }
.btn.primary { background:#111827; }
.btn.light { background:#fff; color:#111827; }
.btn.danger { background:#ef4444; border-color:#ef4444; }
.btn.manage { background:#3b82f6; border-color:#3b82f6; }

/* 表格：所有列单行 */
.table { background:#fff; border:1px solid #eee; border-radius:16px; overflow:hidden; margin-top:12px; }
.thead, .row {
  display:grid;
  grid-template-columns: 60px 80px minmax(240px, 1fr) 180px 320px; /* idx | logo | name | division | actions */
  align-items:center;
  column-gap:12px;
}
.thead { background:#f8fafc; font-weight:700; color:#111827; }
.th, .td { padding: 14px 12px; border-bottom: 1px solid #f1f5f9; white-space: nowrap; overflow: hidden; }
.empty { padding: 20px; color:#6b7280; text-align:center; }
.idx { text-align:center; }

.logo-img { width:40px; height:40px; object-fit:cover; border-radius:6px; }
.pendingDelete { opacity:.55; }

.cell-input, .cell-select {
  width:100%; height:34px; border:1px solid #e5e7eb; border-radius:8px; padding:0 8px; outline:none; font-size:14px;
}
.cell-select { background:#fff; }
.dirty { border-color:#3b82f6 !important; box-shadow: 0 0 0 2px rgba(59,130,246,.25); }

.file-input-hidden { position:absolute; width:1px; height:1px; opacity:0; pointer-events:none; }
.act { display:flex; gap:8px; align-items:center; flex-wrap:nowrap; }

.modal-mask { position: fixed; inset: 0; background: rgba(0,0,0,.35); display:flex; align-items:center; justify-content:center; padding:16px; }
.modal { width: 520px; max-width:95vw; background:#fff; border-radius:12px; padding:16px; box-shadow:0 10px 30px rgba(0,0,0,.15); }
.modal h3 { margin: 6px 0 12px; font-size: 18px; font-weight: 800; }
.form { display:grid; gap:12px; }
.field { display:flex; flex-direction:column; gap:6px; }
.label { font-size:13px; color:#374151; display:block; }
.req { color:#ef4444; }
.input { height:36px; border:1px solid #e5e7eb; border-radius:8px; padding:0 10px; outline:none; }
.input:focus { border-color:#111827; }
.input-file { display:block; }
.modal-actions { display:flex; justify-content:flex-end; gap:10px; margin-top:14px; }
</style>
