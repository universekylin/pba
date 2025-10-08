<!-- src/views/AdminPage.vue -->
<template>
  <div class="admin-shell">
    <aside class="sidebar">
      <div class="brand">PBA Admin</div>

      <nav>
        <!-- 总览 -->
        <RouterLink to="/admin-panel" class="navlink" active-class="active">
          📊 Overview
        </RouterLink>

        <!-- 球队管理 -->
        <RouterLink to="/admin-panel/teams" class="navlink" active-class="active">
          🏀 Team Management
        </RouterLink>

        <!-- 赛程管理 -->
        <RouterLink to="/admin-panel/schedule" class="navlink" active-class="active">
          📅 Schedule Management
        </RouterLink>

        <!-- Ladder 排名 -->
        <RouterLink to="/admin-panel/ladder" class="navlink" active-class="active">
          🧭 Ladder
        </RouterLink>
      </nav>

      <div class="fill"></div>
      <button class="ghost" @click="logout">Logout</button>
    </aside>

    <main class="main">
      <!-- 子页面在这里渲染 -->
      <router-view />
    </main>
  </div>
</template>

<script setup>
function logout () {
  sessionStorage.removeItem('ADMIN_OK')
  alert('Admin session cleared. Password will be required next time.')
}
</script>

<style scoped>
.admin-shell {
  position: fixed;
  inset: 0;
  background: #f6f7f9;
  display: grid;
  grid-template-columns: 240px 1fr;
}

.sidebar {
  background: #0f172a;
  color: #e5e7eb;
  display: flex;
  flex-direction: column;
  padding: 16px;
}

.brand {
  font-weight: 800;
  margin-bottom: 12px;
}

nav {
  display: grid;
  gap: 8px;
}

.navlink {
  display: block;
  padding: 10px 12px;
  border-radius: 10px;
  color: #e5e7eb;
  text-decoration: none;
}
.navlink:hover {
  background: #1f2937;
}

.active {
  background: #374151;
}

.fill {
  flex: 1;
}

.ghost {
  background: #fff;
  color: #111827;
  border: 1px dashed #4b5563;
  border-radius: 10px;
  height: 36px;
}

.main {
  overflow: auto;
}
</style>
