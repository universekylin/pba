<template>
  <section class="card">
    <h3 class="card-title">{{ title }}</h3>

    <div v-if="!rows || rows.length === 0" class="empty">No data</div>

    <!-- 只出现上下滚轮：用外层 wrapper 包住表格 -->
    <template v-else>
      <div class="table-wrapper">
        <table class="table">
          <colgroup>
            <col style="width: 10%" />   <!-- Rank -->
            <col style="width: 30%" />   <!-- Player -->
            <col style="width: 20%" />   <!-- Team -->
            <col style="width: 13%" />   <!-- Total -->
            <col style="width: 13%" />   <!-- Games -->
            <col style="width: 14%" />   <!-- Points -->
          </colgroup>

          <thead>
            <tr>
              <th>Rank</th>
              <th class="th-left">Player</th>
              <th class="th-left">Team</th>
              <th class="th-num">{{ colLabel }}</th>
              <th class="th-num">Games</th>
              <th class="th-num">{{ avgLabel || 'Points' }}</th>
            </tr>
          </thead>

          <tbody>
            <tr v-for="r in rows" :key="r.rank + '-' + r.player">
              <td class="rank">{{ r.rank }}</td>
              <td class="player ellipsis" :title="r.player">{{ r.player }}</td>
              <td class="team">
                <img v-if="r.logo_url" :src="r.logo_url" alt="" />
                <span class="ellipsis" :title="r.team">{{ r.team }}</span>
              </td>
              <td class="num">{{ r.total }}</td>
              <td class="num">{{ r.games }}</td>
              <td class="num">{{ r.avg?.toFixed ? r.avg.toFixed(1) : r.avg }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </template>
  </section>
</template>

<script setup>
defineProps({
  title: String,
  rows: Array,
  colLabel: String,
  avgLabel: {
    type: String,
    default: 'Points'
  }
})
</script>

<style scoped>
.card {
  background: #fff;
  border: 1px solid #eee;
  border-radius: 16px;
  padding: 14px 16px;
  box-shadow: 0 4px 14px rgba(0,0,0,.05);
  overflow: hidden; /* 兜底：卡片不出横向滚动 */
}

.card-title {
  margin: 0 0 8px;
  font-weight: 800;
  font-size: 16px;
}

.empty {
  color: #6b7280;
  padding: 8px 0;
}

/* 只允许上下滚动，禁止左右滚动 */
.table-wrapper {
  max-height: 320px;        /* 行多时才出现竖滚；需要更高自己改 */
  overflow-y: auto;
  overflow-x: hidden;
  -webkit-overflow-scrolling: touch;
}

.table {
  width: 100%;              /* 跟随卡片宽度，不会撑出 */
  table-layout: fixed;      /* 按 colgroup 百分比固定列宽 */
  border-collapse: collapse;
}

.table thead th,
.table tbody td {
  border-top: 1px solid #f1f5f9;
  padding: 10px 12px;
  font-size: 14px;
  vertical-align: middle;
  white-space: nowrap;
}

.table thead th {
  border-top: 0;
  color: #6b7280;
  font-weight: 700;
}

.th-left { text-align: left; }
.th-num  { text-align: right; }

.rank { text-align: center; font-weight: 700; }
.player { text-align: left; }

.team {
  display: flex;
  align-items: center;
  gap: 8px;
}
.team img {
  width: 20px;
  height: 20px;
  border-radius: 4px;
  object-fit: cover;
}
.team span { flex: 1; min-width: 0; }

.num {
  text-align: right;
  font-variant-numeric: tabular-nums; /* 数字等宽，更整齐 */
}

.ellipsis {
  overflow: hidden;
  text-overflow: ellipsis;
}
</style>
