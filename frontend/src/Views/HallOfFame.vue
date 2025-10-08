<template>
  <div class="hof-page">
    <!-- 顶部横幅（如果不需要可以删掉这块） -->
    <div class="hero">
      <img src="@/assets/images/basketball-banner.jpg" alt="Hero" />
    </div>

    <div class="container">
      <h1 class="title">HALL OF FAME</h1>

      <!-- 收窄并居中的列表容器 -->
      <div class="hof-list">
        <div class="hof-item">
          <img class="badge" src="@/assets/images/default-team.png" alt="PBA Player 1" />
          <div class="text">
            <div class="name">PBA Player 1</div>
          </div>
        </div>

        <div class="hof-item">
          <img class="badge" src="@/assets/images/default-team.png" alt="PBA Player 2" />
          <div class="text">
            <div class="name">PBA Player 2</div>
          </div>
        </div>

        <!-- 继续复制 hof-item 即可新增 -->
      </div>
    </div>
  </div>
</template>

<script setup>
// 纯展示，无逻辑
</script>

<style scoped>
/* 顶部横幅 */
.hero { width:100%; height:380px; overflow:hidden; }
.hero img { width:100%; height:100%; object-fit:cover; }

/* 页面容器（跟站点一致的最大宽度） */
.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 36px 24px 80px;
  background: #fff;
}

/* 标题 */
.title {
  text-align: center;
  font-size: 28px;
  font-weight: 800;
  letter-spacing: .5px;
  margin: 0 0 24px;
  color: #111;
}

/* === 关键调整：列表本身再收窄并居中 === */
.hof-list {
  width: min(900px, 100%);   /* 这里控制整体“靠中”的紧凑程度，900 可按需微调 */
  margin: 0 auto;            /* 居中 */
  display: grid;
  grid-template-columns: 1fr;
  row-gap: 48px;             /* 两个条目之间的竖向间距 */
}

/* 单条项目：左图 + 右文字 */
.hof-item {
  display: grid;
  grid-template-columns: 220px 1fr;  /* 左图固定宽，右侧自适应 */
  align-items: center;
  column-gap: 28px;
}

/* 徽章大图（和原站一样的圆形） */
.badge {
  width: 220px;
  height: 220px;
  object-fit: cover;
  border-radius: 999px;
  background: #f5f5f5;
}

/* 名称字号/粗细 */
.text .name {
  font-size: 28px;          /* 适当大一点靠近参考页字号 */
  font-weight: 700;
  color: #232323;
}

/* 响应式 */
@media (max-width: 900px) {
  .hero { height: 260px; }
  .hof-list { width: min(640px, 100%); }
  .hof-item { grid-template-columns: 160px 1fr; column-gap: 20px; }
  .badge { width: 160px; height: 160px; }
  .text .name { font-size: 22px; }
}
@media (max-width: 560px) {
  .hero { height: 200px; }
  .hof-list { width: 100%; }
  .hof-item {
    grid-template-columns: 1fr;
    justify-items: center;   /* 小屏时图文都居中 */
    row-gap: 10px;
  }
  .text .name { text-align: center; }
}
</style>
