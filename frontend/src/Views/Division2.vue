<template>
  <div class="division-page">
    <!-- 顶部横幅 -->
    <div class="division-banner">
      <img src="@/assets/images/basketball-banner.jpg" alt="Basketball Banner" class="banner-img" />
    </div>

    <!-- 内容主体 -->
    <div class="division-content">
      <h1 class="title">DIVISION 2</h1>
      <p class="address">Address: 281 Darebin Rd, Thornbury VIC 3071</p>

      <!-- 轮次按钮区域 -->
      <div class="round-grid">
        <RouterLink
          v-for="round in rounds"
          :key="round"
          class="round-btn"
          :to="`/d2/round/${round}`"
        >
          Round {{ round }}
        </RouterLink>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const rounds = ref([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11])
</script>

<style scoped>
/* 整体页面背景 */
.division-page {
  width: 100%;
  min-height: 100vh;
  background: #f8f8f8;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding-top: var(--header-h); /* 避开导航栏 */
}

/* 顶部横幅 */
.division-banner {
  width: 100%;
  height: 300px;
  overflow: hidden;
}

.banner-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

/* 内容主体 */
.division-content {
  text-align: center;
  margin-top: 30px;
  padding: 0 20px;
}

.title {
  font-size: 32px;
  font-weight: bold;
  color: #111;
}

.address {
  font-size: 16px;
  color: #555;
  margin-top: 8px;
  margin-bottom: 30px;
}

/* 轮次按钮区域 */
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
  border-radius: 25px;
  padding: 12px 0;
  font-size: 16px;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.3s;
  text-align: center;
  text-decoration: none;
}

.round-btn:hover {
  background: #d32f2f;
}


</style>
