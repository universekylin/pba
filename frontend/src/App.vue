<!-- src/App.vue -->
<template>
  <div class="app-shell">
    <!-- 前台导航：仅公共页面显示 -->
    <NavBar v-if="!isAdminRoute" />

    <!-- 主内容：公共页为避开 fixed 导航而留出顶部间距；后台页不留 -->
    <main :class="['app-main', { 'no-nav': isAdminRoute }]">
      <router-view />
    </main>

    <!-- 全站 Footer：仅公共页面显示（自动出现在最底部） -->
    <SiteFooter v-if="!isAdminRoute" />
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import NavBar from '@/components/NavBar.vue'
import SiteFooter from '@/components/common/Footer.vue' // ← 如果你的路径不同，改成对应的

const route = useRoute()

// 后台页面判定：使用路由 meta.layout === 'admin' 或以 /admin-panel 开头
const isAdminRoute = computed(() =>
  route.matched.some(r => r.meta?.layout === 'admin') ||
  route.path.startsWith('/admin-panel')
)
</script>

<style>
/* ===== 导航高度（和 NavBar 保持一致） ===== */
:root { --header-h: 70px; }

/* 基础尺寸 */
html, body, #app {
  margin: 0;
  padding: 0;
  height: 100%;
  width: 100%;
  overflow-x: hidden;
  font-family: system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial,
    "Apple Color Emoji", "Segoe UI Emoji";
}

/* 一个垂直布局的外壳，保证 Footer 贴底 */
.app-shell{
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

/* 主内容占据剩余空间，保证短页也能把 Footer 顶到页面底部 */
.app-main{
  flex: 1 0 auto;
  padding-top: calc(var(--header-h) + env(safe-area-inset-top, 0px));
  min-height: 0; /* 防止子元素溢出影响布局 */
}

/* 后台页面没有前台导航，因此不需要额外的顶部间距 */
.app-main.no-nav{
  padding-top: 0;
}

/* 可选：需要「贴导航下方吸顶」的元素可加这个类 */
.sticky-under-nav{
  position: sticky;
  top: calc(var(--header-h) + 8px);
  z-index: 5;
}
</style>
