<template>
  <footer class="footer">
    <div class="footer-wrap">
      <section class="about">
        <h2>About Perfect Baller Association</h2>
        <p>
          After the 2021 lockdown, we noticed a real rise in loneliness and blues among our
          international student mates in Victoria. It hit us hard, so we decided to do something
          about it. Lockdown made things tougher, with less chit-chat and hangouts. That’s when we
          kicked off the PBA international student sporting initiative, centred around basketball
          and badminton. And guess what? We brought together a whopping 2,500 international
          students, building connections and friendships that really last.
        </p>
      </section>

      <section class="contact">
        <h2>Contact Details</h2>
        <p>📍 281 Darebin Rd, Thornbury VIC</p>
        <p>
          🌐 <a href="https://pba2024.com.au/" target="_blank" rel="noopener">https://www.pbaleague.com/</a>
        </p>
        <p>✉️ director@perfectballers.com</p>
      </section>
    </div>

    <div class="copyright">
      © Copyright 2023 Perfect Baller Association. All Rights Reserved
    </div>
  </footer>
</template>

<style scoped>
.footer {
  width: 100%;
  background: #1e1e1e;
  color: #fff;
  margin-top: 56px;
}

.footer-wrap {
  max-width: 1200px;
  margin: 0 auto;
  padding: 48px 24px 28px;
  display: grid;
  grid-template-columns: 1fr 420px;
  column-gap: 96px;
}

.about h2,
.contact h2 {
  font-size: 24px;
  font-weight: 800;
  margin: 0 0 16px;
}

.about p,
.contact p {
  font-size: 16px;
  line-height: 1.85;
  color: #fff; /* 全部纯白 */
  margin: 0 0 12px;
}

/* 链接也变成白色 */
.contact a {
  color: #fff !important;
  text-decoration: none;
}
.contact a:hover {
  text-decoration: underline;
  color: #f5f5f5; /* hover 时稍微浅一点 */
}

.copyright {
  text-align: center;
  font-size: 13px;
  color: #cfcfcf;
  padding: 16px 24px 24px;
  border-top: 1px solid #333;
}

@media (max-width: 980px) {
  .footer-wrap {
    grid-template-columns: 1fr;
    row-gap: 28px;
  }
}
</style>
