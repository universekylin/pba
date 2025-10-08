<template>
  <section class="partner-section">
    <!-- 标题 -->
    <h2 class="partner-title">PARTNER</h2>

    <!-- 两个合作 Logo -->
    <div class="partner-logos">
      <img src="@/assets/images/pba1.jpg" alt="To Future" class="partner-logo" />
      <img src="@/assets/images/pba2.jpg" alt="Study Melbourne" class="partner-logo" />
    </div>
  </section>
</template>

<script setup></script>

<style scoped>
/* 整体容器 */
.partner-section {
  width: 100%;
  padding: 60px 24px;
  background: #f8f8f8; /* 灰白色背景 */
  text-align: center;
}

/* 标题样式 */
.partner-title {
  font-size: clamp(24px, 4vw, 36px);
  font-weight: 900;
  margin-bottom: 40px;
  letter-spacing: 1.5px;
}

/* Logo 容器：水平排列并居中 */
.partner-logos {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 80px; /* Logo 之间的间距 */
  flex-wrap: wrap; /* 小屏幕自动换行 */
}

/* 单个 Logo 样式 */
.partner-logo {
  max-width: 300px;
  height: auto;
  object-fit: contain;
  transition: transform 0.3s ease;
  cursor: pointer;
}

.partner-logo:hover {
  transform: scale(1.05); /* 鼠标悬停微微放大 */
}
</style>
