<!-- src/components/AddPlayoffMatchModal.vue -->
<template>
  <div class="modal-mask">
    <div class="modal-container">
      <h3>新增季后赛比赛</h3>

      <!-- 轮次 -->
      <label>轮次</label>
      <select v-model="form.round_no">
        <option :value="1">第一轮</option>
        <option :value="2">第二轮</option>
        <option :value="3">总决赛</option>
      </select>

      <!-- 主队 -->
      <label>主队</label>
      <select v-model="form.home_team_id">
        <option disabled value="">请选择主队</option>
        <option v-for="t in teams" :key="t.id" :value="t.id">{{ t.name }}</option>
      </select>

      <!-- 客队 -->
      <label>客队</label>
      <select v-model="form.away_team_id">
        <option disabled value="">请选择客队</option>
        <option v-for="t in teams" :key="t.id" :value="t.id">{{ t.name }}</option>
      </select>

      <!-- 日期 -->
      <label>比赛日期</label>
      <input type="date" v-model="form.date" />

      <!-- 时间 -->
      <label>比赛时间</label>
      <input type="time" v-model="form.time" />

      <!-- 场地 -->
      <label>场地</label>
      <input type="text" v-model="form.venue" placeholder="例如：Court 7" />

      <!-- 操作按钮 -->
      <div class="actions">
        <button class="btn light" @click="$emit('close')">取消</button>
        <button class="btn primary" @click="onSubmit" :disabled="loading">
          {{ loading ? '提交中...' : '确定新增' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import api from '@/api/axios'

// Props
const props = defineProps({
  divisionCode: { type: String, required: true },
  seasonId: { type: Number, required: true },
  teams: { type: Array, required: true }, // 父组件传参
  onSuccess: { type: Function, required: true }
})

const loading = ref(false)
const form = ref({
  round_no: 1,
  home_team_id: '',
  away_team_id: '',
  date: '',
  time: '',
  venue: ''
})

async function onSubmit() {
  if (!form.value.home_team_id || !form.value.away_team_id) {
    alert('请选择主队和客队')
    return
  }
  if (form.value.home_team_id === form.value.away_team_id) {
    alert('主客队不能相同')
    return
  }
  if (!form.value.date || !form.value.time || !form.value.venue) {
    alert('日期、时间、场地不能为空')
    return
  }

  loading.value = true
  try {
    await api.post(`/divisions/${props.divisionCode}/playoffs`, {
      season_id: props.seasonId,
      round_no: form.value.round_no,
      date: form.value.date,
      time: form.value.time,
      venue: form.value.venue,
      home_team_id: form.value.home_team_id,
      away_team_id: form.value.away_team_id,
      status: 'scheduled'
    })

    alert('新增成功')
    props.onSuccess()
    form.value = { round_no: 1, home_team_id: '', away_team_id: '', date: '', time: '', venue: '' }
    props.$emit('close')
  } catch (e) {
    console.error(e)
    alert('新增失败')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.modal-mask {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0,0,0,0.5);
  display: flex; justify-content: center; align-items: center;
}
.modal-container {
  background: #fff; padding: 20px; border-radius: 12px; width: 360px;
  display: flex; flex-direction: column; gap: 12px;
}
.actions {
  display: flex; justify-content: flex-end; gap: 10px;
}
.btn { padding: 8px 12px; border-radius: 6px; cursor: pointer; }
.btn.light { background: #f3f4f6; }
.btn.primary { background: #111827; color: white; }
</style>
