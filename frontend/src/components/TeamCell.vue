<template>
  <div class="teamcell">
    <img class="logo" :src="team?.logo_url || '/placeholder-team.png'" alt="">
    <span class="name">{{ team?.name || '未定' }}</span>
  </div>
</template>
<script setup>
defineProps({ team: Object })
</script>
<style scoped>
.teamcell{display:inline-flex;align-items:center;gap:10px}
.logo{width:36px;height:36px;border-radius:50%;object-fit:cover}
.name{font-weight:600}
</style>
