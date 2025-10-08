<template>
  <section class="venue">
    <h2 class="venue-title">VENUE</h2>

    <div class="map-card">
      <iframe
        class="map-frame"
        title="Narrandjeri Stadium Map"
        loading="lazy"
        referrerpolicy="no-referrer-when-downgrade"
        allowfullscreen
        src="https://www.google.com/maps?q=Narrandjeri%20Stadium%20281%20Darebin%20Rd,%20Thornbury%20VIC%203071&output=embed&z=15">
      </iframe>
    </div>
  </section>
</template>

<script setup></script>

<style scoped>
/* 整体区块：居中、上下留白 */
.venue{
  width: 100%;
  margin: 48px auto 56px;
}

/* 标题样式，居中，和示例一致的粗体感 */
.venue-title{
  margin: 0 0 24px;
  text-align: center;
  font-size: clamp(28px, 4vw, 48px);
  font-weight: 900;
  letter-spacing: 2px;
}

/* 地图外卡片：限制宽度并居中，圆角+阴影 */
.map-card{
  width: min(1200px, 100% - 96px);  /* 左右有 48px 安全边距 */
  margin: 0 auto;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 12px 30px rgba(0,0,0,.15);
  background: #f7f7f8;
}

/* 用新式 aspect-ratio 保持 16:9，高度自适应 */
.map-frame{
  display: block;
  width: 100%;
  aspect-ratio: 16 / 9;  /* 大约等于你截图比例 */
  border: 0;
}
</style>
