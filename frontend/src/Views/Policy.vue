<template>
  <div class="policy-page">
    <h1 class="title">PBA LEAGUE POLICY</h1>

    <!-- 中文版 PDF -->
    <section class="pdf-section">
      <h2>
        2025联赛规章制度（中文）
        <a
          class="download-link"
          href="/static/policies/2025联赛规章制度.pdf"
          download="2025联赛规章制度.pdf"
        >
          Download
        </a>
      </h2>
      <iframe
        class="pdf-frame"
        src="/static/policies/2025联赛规章制度.pdf"
      ></iframe>
    </section>

    <!-- 英文版 PDF -->
    <section class="pdf-section">
      <h2>
        PBA League Rules 2025 (English)
        <a
          class="download-link"
          href="/static/policies/2025联赛规章制度英文版.pdf"
          download="PBA_League_Rules_2025_English.pdf"
        >
          Download
        </a>
      </h2>
      <iframe
        class="pdf-frame"
        src="/static/policies/2025联赛规章制度英文版.pdf"
      ></iframe>
    </section>
  </div>
</template>

<script>
export default {
  name: "Policy",
};
</script>

<style scoped>
.policy-page {
  max-width: 1000px;
  margin: 0 auto;
  padding: 30px 15px;
}

.title {
  text-align: center;
  margin-bottom: 40px;
  font-size: 2rem;
  font-weight: bold;
}

.pdf-section {
  margin-bottom: 50px;
}

.pdf-section h2 {
  margin-bottom: 10px;
  font-size: 1.2rem;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 10px;
}

.download-link {
  font-size: 0.9rem;
  color: #e53935;
  text-decoration: none;
  font-weight: 500;
}
.download-link:hover {
  text-decoration: underline;
}

.pdf-frame {
  display: block;
  margin: 0 auto;
  width: 100%;
  max-width: 800px;   /* 限制最大宽度 */
  height: 500px;      /* 控制高度 */
  border: none;
  box-shadow: 0 0 10px rgba(0,0,0,0.15);
  border-radius: 6px;
}
</style>
