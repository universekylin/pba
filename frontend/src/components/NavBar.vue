<!-- src/components/NavBar.vue -->
<template>
  <header class="site-header">
    <div class="inner">
      <!-- 红色菜单 -->
      <div class="ribbon-wrapper">
        <div class="ribbon">
          <nav class="menu">
            <!-- 首页 -->
            <RouterLink to="/">Home</RouterLink>
            <RouterLink to="/policy">PBA League Policy</RouterLink>

            <!-- ===== S8：左一级，右二级 ===== -->
            <div class="dropdown">
              <button>S8 ▾</button>
              <div class="panel panel-l1">
                <ul class="menu-list">
                  <!-- Fixture & Result -->
                  <li class="has-sub">
                    <a class="item">Fixture &amp; Result</a>
                    <div class="sub-panel">
                      <RouterLink class="sub-item" to="/champ-d1">Champ &amp; D1</RouterLink>
                      <RouterLink class="sub-item" to="/division-2">Division 2</RouterLink>
                    </div>
                  </li>

                  <!-- Ladder -->
                  <li>
                    <RouterLink class="item" to="/s8/ladder">Ladder</RouterLink>
                  </li>

                  <!-- Player Ranking -->
                  <li class="has-sub">
                    <a class="item">Player Ranking</a>
                    <div class="sub-panel">
                      <RouterLink class="sub-item" to="/s8/ranking/champ">Championship</RouterLink>
                      <RouterLink class="sub-item" to="/s8/ranking/div1">Division 1</RouterLink>
                      <RouterLink class="sub-item" to="/s8/ranking/div2">Division 2</RouterLink>
                    </div>
                  </li>

                  <!-- Teams -->
                  <li>
                    <RouterLink class="item" to="/s8/teams">Teams</RouterLink>
                  </li>
                </ul>
              </div>
            </div>

            <!-- ===== Gallery：二级下拉 ===== -->
            <div class="dropdown">
              <button>Gallery ▾</button>
              <div class="panel panel-l1">
                <ul class="menu-list">
                  <li>
                    <a
                      class="item"
                      href="https://drive.google.com/drive/folders/1Qhu_G2n9XpwD_-T4zDptQVwwEhba6pPO"
                      target="_blank"
                      rel="noopener"
                    >Photo</a>
                  </li>
                  <li>
                    <a
                      class="item"
                      href="https://www.youtube.com/@pbamelbourne"
                      target="_blank"
                      rel="noopener"
                    >Video</a>
                  </li>
                </ul>
              </div>
            </div>

            <!-- Enrolment 下拉 -->
            <div class="dropdown">
              <button>Enrolment ▾</button>
              <div class="panel panel-l1">
                <ul class="menu-list">
                  <li><RouterLink class="item" to="/enrolment/individual">Join As Individual</RouterLink></li>
                  <li><RouterLink class="item" to="/enrolment/team">Join As Team</RouterLink></li>
                </ul>
              </div>
            </div>

            <!-- 其他单层菜单 -->
            <RouterLink to="/about">About Us</RouterLink>
            <RouterLink to="/hall-of-fame">Hall of Fame</RouterLink>
          </nav>
        </div>
      </div>

      <!-- 右侧社交图标（全部可点击） -->
      <div class="social">
        <a
          href="https://www.instagram.com/pba__official/?igshid=OGQ5ZDc2ODk2ZA%3D%3D&utm_source=qr"
          target="_blank"
          rel="noopener"
          aria-label="Instagram"
        >
          <img src="@/assets/icons/instagram.png" alt="Instagram" />
        </a>

        <a
          href="https://www.douyin.com/user/MS4wLjABAAAAV9Q7OG45GqBQfDiaHJIIdfVRLGimnDK93VpAQMAXIyA"
          target="_blank"
          rel="noopener"
          aria-label="Douyin"
        >
          <img src="@/assets/icons/tiktok.png" alt="Douyin" />
        </a>

        <a
          href="https://mp.weixin.qq.com/mp/profile_ext?action=home&__biz=Mzg2Mjc4NjMwNg==&scene=124#wechat_redirect"
          target="_blank"
          rel="noopener"
          aria-label="WeChat"
        >
          <img src="@/assets/icons/wechat.png" alt="WeChat" />
        </a>
      </div>
    </div>
  </header>
</template>

<script setup>
import { RouterLink } from 'vue-router'
</script>

<style scoped>
/* 顶部导航：fixed，并用全局变量控制高度 */
.site-header {
  position: fixed;
  inset: 0 0 auto 0;
  height: var(--header-h);
  background: #e0e0e0;
  z-index: 1000;
  display: flex;
  justify-content: center;
}

/* 让内容在固定高度里垂直居中 */
.inner {
  width: 100%;
  height: 100%;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 24px;
}

/* ===== 红色菜单居中 ===== */
.ribbon-wrapper {
  flex: 1;
  display: flex;
  justify-content: center;
}

.ribbon {
  position: relative;
  background: #d32f2f;
  padding: 12px 30px;
  display: flex;
  justify-content: center;
  border-radius: 2px;
}
.ribbon::before,
.ribbon::after {
  content: "";
  position: absolute;
  top: 0;
  bottom: 0;
  width: 40px;
  background: #c62828;
  clip-path: polygon(0 0, 100% 0, 72% 100%, 0 100%);
}
.ribbon::before { left: -40px; }
.ribbon::after  { right: -40px; transform: scaleX(-1); }

/* 菜单整体 */
.menu {
  display: flex;
  gap: 30px;
  align-items: center;
}
.menu a,
.menu button {
  color: #fff;
  text-decoration: none;
  background: transparent;
  border: none;
  cursor: pointer;
  font-size: 18px;
  font-weight: 600;
  padding: 5px 10px;
}

/* ===== 一级下拉 ===== */
.dropdown { position: relative; }
.panel-l1 {
  position: absolute;
  top: 100%;
  left: 0;
  background: #2c2c2c;
  color: #fff;
  border-radius: 4px;
  min-width: 220px;
  display: none;
}
.dropdown:hover .panel-l1 { display: block; }

.menu-list { list-style: none; padding: 0; margin: 0; }
.menu-list li { position: relative; }

.menu-list .item {
  display: block;
  padding: 12px 16px;
  color: #fff;
}
.menu-list .item:hover { background: #b71c1c; }

/* ===== 二级子菜单 ===== */
.has-sub > .item::after {
  content: ">";
  float: right;
  font-weight: bold;
}
.sub-panel {
  position: absolute;
  top: 0;
  left: 100%;
  background: #2c2c2c;
  min-width: 200px;
  display: none;
}
.has-sub:hover .sub-panel { display: block; }
.sub-item {
  display: block;
  padding: 12px 16px;
  color: #fff;
}
.sub-item:hover { background: #b71c1c; }

/* ===== 右侧社交 ===== */
.social {
  display: flex;
  gap: 15px;
}
.social img {
  width: 34px;
  height: 34px;
  cursor: pointer;
}
</style>
