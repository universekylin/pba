<template>
  <section class="hero">
    <img class="banner" src="@/assets/images/city-banner.jpg" alt="City Banner" />
  </section>
</template>

<script setup></script>

<style scoped>
.hero {
  margin: 0;
  padding: 0;
  width: 100%;
  height: 420px;
  position: relative;
  overflow: hidden;
}

.banner {
  display: block; /* 关键：去掉img默认间隙 */
  width: 100%;
  height: 100%;
  object-fit: cover;
  object-position: center;
  margin: 0;
  border: 0;
}
</style>
