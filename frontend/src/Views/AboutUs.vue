<template>
  <div class="about-page">
    <!-- 顶部全幅横幅 -->
    <section class="hero">
      <!-- 你自己的大图：替换为实际地址或放到 assets 中 -->
      <img
        class="hero-img"
        src="@/assets/images/basketball-banner.jpg"
        alt="About PBA Banner"
        @error="onHeroError"
      />
      <div class="hero-mask"></div>
    </section>

    <!-- 内页正文容器 -->
    <div class="container">
      <h1 class="page-title">ABOUT US</h1>

      <!-- 正文段落（按你截图的文案结构排版） -->
      <div class="rich-text">
        <p>
          After the 2021 lockdown, we noticed a real rise in loneliness and blues among our
          international student mates in Victoria. It hit us hard, so we decided to do something
          about it. Lockdown made things tougher, with less chit-chat and hangouts. That’s when we
          kicked off the PBA international student sporting initiative, centred around basketball
          and badminton. And guess what? We brought together a whopping 2,500 international
          students, building connections and friendships that really last.
        </p>

        <p>
          Here at PBA, we get that looking after your physical and mental well-being is a big deal.
          Our events are a breather from study stress, especially after all that COVID chaos. Our
          first basketball bash at Oakleigh Recreation Centre was a surprise hit, pulling in 300
          mates, even with next to no advertising. And now, with our not-for-profit setup, we’ve
          made joining in even better. It’s all about making the international student experience
          richer, helping you feel at home and pumped up.
        </p>

        <p>
          It’s not just the regular stuff. We’re talking big badminton showdowns, star-studded
          basketball events, and even training sessions with your favourite celebs. Streamed live
          and watched by tens of thousands of sport enthusiasts locally and internationally, our
          events aren’t just games; they’re a real social scene. The response from international
          students has been epic, with heaps signing up before even landing in Melbourne and more
          queuing up for future events. It’s more than just sport; it’s a vibe, and we love being
          part of the international student community’s story. Cheers to more good times ahead!
        </p>
      </div>

      <!-- 管理团队卡片（3列） -->
      <div class="team-grid">
        <div class="card">
          <img
            class="avatar"
            src="@/assets/images/team-eric.jpg"
            alt="Eric Sima"
            @error="onAvatarError"
          />
          <div class="card-meta">
            <div class="name">Eric Sima</div>
            <div class="role">Director</div>
          </div>
        </div>

        <div class="card">
          <img
            class="avatar"
            src="@/assets/images/team-pan.jpg"
            alt="Pan"
            @error="onAvatarError"
          />
          <div class="card-meta">
            <div class="name">Pan</div>
            <div class="role">Director</div>
          </div>
        </div>

        <div class="card">
          <img
            class="avatar"
            src="@/assets/images/team-tony.jpg"
            alt="Tony Ma"
            @error="onAvatarError"
          />
          <div class="card-meta">
            <div class="name">Tony Ma</div>
            <div class="role">Director</div>
          </div>
        </div>
      </div>
    </div>

    <!-- 你现有站点的统一 Footer（如果 App.vue 已经全局注入，就不需要再写） -->
  </div>
</template>

<script setup>
/**
 * 若上面几张图片暂时没有，先放占位图，避免加载失败导致的空白。
 * 你可以把 /assets/images/ 里的文件名换成自己的实际文件。
 */
import heroFallback from '@/assets/images/basketball-banner.jpg'
import avatarFallback from '@/assets/images/default-team.png'

function onHeroError(e) {
  if (e.target.dataset.fallback === '1') return
  e.target.dataset.fallback = '1'
  e.target.src = heroFallback
}
function onAvatarError(e) {
  if (e.target.dataset.fallback === '1') return
  e.target.dataset.fallback = '1'
  e.target.src = avatarFallback
}
</script>

<style scoped>
/* 页面基底 */
.about-page {
  width: 100%;
  background: #fff;
}

/* 顶部大图 */
.hero {
  position: relative;
  width: 100%;
  height: 360px;            /* 按你截图比例做的高度，如需更高就调这里 */
  overflow: hidden;
}
.hero-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transform: scale(1.02);   /* 轻微放大，避免裁切边缘空白 */
}
.hero-mask {
  position: absolute;
  inset: 0;
  /* 顶部菜单下的暗化对比：左上角稍暗，右下角略亮，贴近你截图的氛围 */
  background: linear-gradient(
    180deg,
    rgba(0,0,0,0.35) 0%,
    rgba(0,0,0,0.15) 40%,
    rgba(0,0,0,0.00) 100%
  );
  pointer-events: none;
}

/* 内页容器 */
.container {
  max-width: 980px;       /* 贴近你 WordPress 页面的版心宽度 */
  margin: 0 auto;
  padding: 32px 20px 60px;
}

/* 标题 */
.page-title {
  text-align: center;
  font-size: 28px;
  font-weight: 900;
  letter-spacing: .06em;
  margin: 6px 0 22px;
  color: #111;
}

/* 正文（跟你截图的行高、字宽感觉去调的） */
.rich-text {
  color: #222;
  font-size: 16px;
  line-height: 1.9;
}
.rich-text p { margin: 0 0 18px; }

/* 三列管理团队卡片 */
.team-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 28px;
  margin-top: 22px;
}
.card {
  background: #fff;
  border: 1px solid #e9e9e9;
  border-radius: 6px;
  overflow: hidden;
  transition: transform .12s ease, box-shadow .12s ease;
}
.card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 22px rgba(0,0,0,0.06);
}
.avatar {
  display: block;
  width: 100%;
  aspect-ratio: 1/1;      /* 正方形头像 */
  object-fit: cover;
  background: #f5f5f5;
}
.card-meta {
  padding: 12px 14px 16px;
  text-align: center;
}
.name {
  font-weight: 800;
  color: #111;
  margin-bottom: 4px;
}
.role {
  color: #6b7280;
  font-size: 14px;
}

/* 响应式：平板 2 列，手机 1 列 */
@media (max-width: 980px) {
  .hero { height: 300px; }
  .team-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
}
@media (max-width: 640px) {
  .hero { height: 240px; }
  .team-grid { grid-template-columns: 1fr; }
}
</style>
