<template>
  <div class="champ-page">
    <!-- 顶部横幅 -->
    <div class="champ-banner">
      <img src="@/assets/images/basketball-banner.jpg" alt="Basketball Banner" class="banner-img" />
    </div>

    <!-- 内容主体 -->
    <div class="champ-content">
      <h1 class="title">CHAMP &amp; D1</h1>
      <p class="address">Address: 281 Darebin Rd, Thornbury VIC 3071</p>

      <!-- 轮次按钮：1~11 -->
      <div class="round-grid">
        <button
          v-for="round in 11"
          :key="round"
          class="round-btn"
          @click="$router.push({ name: 'PublicRound', params: { division: 'champion', no: round } })"
        >
          Round {{ round }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
/* 无逻辑需求，这里无需脚本 */
</script>

<style scoped>
/* 整体页面：给导航让出高度，避免被盖住 */
.champ-page {
  width: 100%;
  min-height: 100vh;
  background: #f8f8f8;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding-top: var(--header-h);
}

/* 顶部横幅 */
.champ-banner {
  width: 100%;
  height: 300px;
  overflow: hidden;
}
.banner-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

/* 主体 */
.champ-content {
  text-align: center;
  margin-top: 30px;
  padding: 0 20px;
  width: 100%;
  max-width: 1200px;
}
.title {
  font-size: 32px;
  font-weight: 800;
  color: #111;
}
.address {
  font-size: 16px;
  color: #555;
  margin: 8px 0 30px;
}

/* 轮次按钮 */
.round-grid {
  display: grid;
  grid-template-columns: repeat(3, 120px);
  justify-content: center;
  gap: 30px;
}
.round-btn {
  background: #333;
  color: #fff;
  border: none;
  border-radius: 24px;
  padding: 12px 0;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: background .25s ease;
}
.round-btn:hover { background: #d32f2f; }



</style>
