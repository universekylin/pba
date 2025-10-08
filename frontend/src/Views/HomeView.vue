<!-- src/views/HomeView.vue -->
<template>
  <div class="home-page">
    <HeroBanner />

    <main class="container">
      <!-- 活动宣传海报1 -->
      <section class="promo-section">
        <img src="@/assets/images/vissf-poster.jpg" alt="VISSF Poster" class="promo-image" />
      </section>

      <!-- 活动宣传海报2 -->
      <section class="promo-section">
        <img src="@/assets/images/vissf-poster2.jpg" alt="VISSF Poster 2" class="promo-image" />
      </section>

      <!-- 场地信息 -->
      <VenueSection />

      <!-- 合作伙伴 -->
      <PartnerSection />
    </main>
  </div>
</template>

<script setup>
import HeroBanner from '@/components/HeroBanner.vue'
import VenueSection from '@/components/VenueSection.vue'
import PartnerSection from '@/components/PartnerSection.vue'
</script>

<style scoped>
.home-page { padding-top: var(--header-h); }

.container {
  max-width: 100%;
  margin: 0 auto 24px;
}

.promo-section {
  display: flex;
  justify-content: center;
  margin: 40px auto;
  width: 100%;
}

.promo-image {
  max-width: 100%;
  height: auto;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}
</style>
