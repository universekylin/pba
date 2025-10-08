<!-- src/views/EnrolIndividual.vue -->
<template>
  <!-- 顶部导航 -->
  <NavBar />

  <div class="page">
    <form class="form" @submit.prevent="onSubmit">
      <h1 class="title">PBA 2024 S6 Individual Player Registration Form</h1>

      <!-- 1. Your Name * -->
      <div class="row">
        <label class="label">1. Your Name <span>*</span></label>
        <div class="grid-2">
          <input v-model="form.firstName" required placeholder="First Name" />
          <input v-model="form.lastName" required placeholder="Last Name" />
        </div>
      </div>

      <!-- 2. Team name * -->
      <div class="row">
        <label class="label">2. Team name <span>*</span></label>
        <small class="hint">If you don't have a team name, please enter PBA</small>
        <textarea v-model="form.teamName" required rows="5"></textarea>
      </div>

      <!-- 3. DOB * -->
      <div class="row">
        <label class="label">3. Date Of Birth <span>*</span></label>
        <input
          v-model="form.dob"
          required
          type="date"
          min="1900-01-01"
          max="2025-12-31"
          @input="limitYear"
        />
      </div>

      <!-- 4. Wechat / Email * -->
      <div class="row">
        <label class="label">4. Wechat number or Email Address <span>*</span></label>
        <input v-model="form.contact" required placeholder="Wechat ID or Email" />
      </div>

      <!-- 5. Residential Address * -->
      <div class="row">
        <label class="label">5. Residential Address <span>*</span></label>
        <input v-model="form.address.street" required placeholder="Street Address" />
        <div class="grid-addr">
          <input v-model="form.address.city" required placeholder="City" />
          <input v-model="form.address.state" required placeholder="State" />
          <input v-model="form.address.postal" required placeholder="Postal Code" />
          <select v-model="form.address.country">
            <option value="Australia">Australia</option>
            <option value="New Zealand">New Zealand</option>
            <option value="China">China</option>
            <option value="Other">Other</option>
          </select>
        </div>
      </div>

      <!-- 6. Phone -->
      <div class="row">
        <label class="label">6. Phone number</label>
        <input v-model="form.phone" placeholder="+61 …" />
      </div>

      <!-- 7. Team Captain -->
      <div class="row">
        <label class="label">7. Team Captain's name</label>
        <input v-model="form.captain" placeholder="Captain name" />
      </div>

      <!-- 8. Emergency Contact * -->
      <div class="row">
        <label class="label">8. Emergency Contact <span>*</span></label>
        <input v-model="form.emergency" required placeholder="Emergency phone number" />
      </div>

      <!-- 9. Division preference * -->
      <div class="row">
        <label class="label">9. Choose your division preference <span>*</span></label>
        <select v-model="form.division" required>
          <option disabled value="">choose</option>
          <option value="Championship">Championship</option>
          <option value="Division 1">Division 1</option>
          <option value="Division 2">Division 2</option>
        </select>
      </div>

      <!-- 10. Registration & Jersey -->
      <div class="row">
        <label class="label">10. PBA 2024 S6 REGISTRATION AND JERSEY <span>*</span></label>

        <!-- 购物车状态：总金额 + 购物车图标 -->
        <div class="cart-status">
          <p>总金额： <span class="total">${{ totalAmount.toFixed(2) }}</span></p>
          <button type="button" class="cart-icon" @click="openCart">
            <span class="badge" v-if="totalCount > 0">{{ totalCount }}</span>
            🛒
          </button>
        </div>

        <!-- 列出产品按钮 -->
        <button type="button" class="list-btn" @click="toggleProducts">
          {{ showProducts ? '收起产品列表' : `列出${products.length}产品` }}
        </button>

        <!-- 产品展示区域（图片来自 /public/images） -->
        <div class="product-grid" v-if="showProducts">
          <div
            v-for="item in products"
            :key="item.id"
            class="product-card"
            @click="openDetail(item)"
          >
            <img :src="item.image" alt="" class="product-img" />
            <div class="product-info">
              <h3>{{ item.name }}</h3>
              <p class="desc">{{ item.desc }}</p>
              <p class="price">per person: <span>${{ item.price.toFixed(2) }}</span></p>
            </div>
          </div>
        </div>

        <!-- 商品详情弹窗 -->
        <div v-if="detailVisible" class="modal">
          <div class="modal-panel">
            <button class="modal-close" @click="detailVisible=false" type="button">×</button>
            <div class="detail-body">
              <img :src="detailProduct.image" class="detail-img" alt=""/>
              <div class="detail-info">
                <h3 class="detail-title">{{ detailProduct.name }}</h3>
                <p class="detail-desc">{{ detailProduct.desc }}</p>
                <div class="detail-price-line">
                  <span>per person</span>
                  <strong class="detail-price">${{ detailProduct.price?.toFixed(2) }}</strong>
                </div>

                <div class="qty-line">
                  <button type="button" class="qty-btn" @click="detailQty = Math.max(1, detailQty-1)">-</button>
                  <input class="qty-input" type="number" min="1" v-model.number="detailQty"/>
                  <button type="button" class="qty-btn" @click="detailQty++">+</button>
                </div>

                <div class="detail-actions">
                  <button class="btn ghost" @click="detailVisible=false" type="button">取消</button>
                  <button class="btn primary" type="button" @click="addDetailToCart">
                    添加到购物篮
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 购物车弹窗 -->
        <div v-if="cartVisible" class="modal">
          <div class="modal-panel wide">
            <button class="modal-close" @click="cartVisible=false" type="button">×</button>
            <div class="cart-table">
              <div class="thead">
                <div>产品</div><div>单价</div><div>量</div><div>总</div><div></div>
              </div>

              <div class="trow" v-for="row in cartList" :key="row.id">
                <div class="c-name">{{ row.name }}</div>
                <div class="c-price">${{ row.price.toFixed(2) }}</div>
                <div class="c-qty">
                  <button type="button" class="qty-btn" @click="decQty(row.id)">-</button>
                  <input class="qty-input" type="number" min="1" :value="row.qty" @input="setQty(row.id, $event.target.value)" />
                  <button type="button" class="qty-btn" @click="incQty(row.id)">+</button>
                </div>
                <div class="c-sub">${{ (row.price*row.qty).toFixed(2) }}</div>
                <div class="c-del">
                  <button type="button" class="icon-btn" @click="removeFromCart(row.id)">🗑️</button>
                </div>
              </div>

              <div class="tfoot">
                <div>小计：</div>
                <div class="tfoot-val">${{ totalAmount.toFixed(2) }}</div>
              </div>

              <div class="cart-actions">
                <button class="btn ghost" type="button" @click="cartVisible=false">继续购物</button>
                <button class="btn primary" type="button" @click="cartVisible=false">完成购物</button>
              </div>
            </div>
          </div>
        </div>

        <!-- 产品声明 -->
        <div class="product-declare">
          <h4>Product Declaration</h4>
          <p><strong>Individual Registration fee is compulsory</strong> for playing in Season 6, it will contain:</p>
          <ul>
            <li>Public Liability insurance</li>
            <li>Ability to join the PBA Season 5 games</li>
            <li>Having a discount for joining selected PBA events</li>
            <li>Having personal statistics for every game</li>
            <li>Having professional photographers and videographers</li>
          </ul>
          <p>
            <strong>Our customer service</strong> will contact the team captain about jersey customization via WeChat.
            If you don't have WeChat, we will contact you via phone message.
          </p>
        </div>

        <!-- 联赛政策 -->
        <div class="policy">
          <h4>PBA Policy For Season 6</h4>
          <p>Each team may <strong>only</strong> register at most 10 players, and at least 5 players.</p>
          <p>Players <strong>MUST NOT</strong> play for more than 1 team.</p>
          <p>Players are <strong>NOT</strong> permitted to transfer teams during the season without league approval.</p>
          <p>All players <strong>MUST</strong> wear uniforms purchased from PBA during the competition.</p>
          <p>Each team's division will be allocated via levels at the time of team formation.</p>
          <p>Each team can have a coach, the coach is <strong>not allowed</strong> to participate in the game.</p>
          <p>
            Only if any team member becomes severely injured during the game and will not participate
            for the rest of the season can the captain decide to substitute one player without paying the registration fee.
            However, a registration form and jersey purchase <strong>are required.</strong>
          </p>
          <p>
            Fill-in players are allowed only when the team has less than 6 players. The team captain must inform PBA in advance,
            otherwise, <strong>penalties will be given.</strong>
          </p>
          <p>Fill-in players must also <strong>satisfy</strong> other player's rules.</p>
          <p>Adding players after the regular season will be prohibited when the team has a sufficient number of players.</p>
          <p>Players who are being rude and having physical conflict <strong>are not allowed</strong></p>
          <p>
            Players will get punishments of facing <strong>suspension from future games</strong> if they violate any policy.
          </p>
          <p>
            Division 1 & 2 players deemed a <strong>"Non-Asian Background Player"</strong> will fall into the PBA 'Special' player category
            and each team is restricted to having 2 'Special' players to form the team.
          </p>
        </div>
      </div>

      <!-- 11. Terms & Conditions -->
      <div class="row">
        <label class="label">
          11. Make sure you click and read the "Term and Condition" <span>*</span>
        </label>

        <div class="agree-list">
          <label class="agree-item" :class="{ checked: agree.truth }">
            <input type="checkbox" v-model="agree.truth" />
            <span class="box" aria-hidden="true"></span>
            <span class="text">The information I have provided above is true and valid.</span>
          </label>

          <label class="agree-item" :class="{ checked: agree.media }">
            <input type="checkbox" v-model="agree.media" />
            <span class="box" aria-hidden="true"></span>
            <span class="text">I grant permission to use photos/videos of me taken during PBA events in media releases.</span>
          </label>

          <label class="agree-item" :class="{ checked: agree.liability }">
            <input type="checkbox" v-model="agree.liability" />
            <span class="box" aria-hidden="true"></span>
            <span class="text">I acknowledge that PBA is not liable for property loss/damage and/or player injury.</span>
          </label>

          <label class="agree-item" :class="{ checked: agree.rules }">
            <input type="checkbox" v-model="agree.rules" />
            <span class="box" aria-hidden="true"></span>
            <span class="text">I acknowledge and agree to the registration rules and Policy.</span>
          </label>
        </div>
      </div>

      <!-- 12. Payment Upload（只允许图片） -->
      <div class="row">
        <label class="label">12. Payment Upload <span>*</span></label>
        <small class="hint">Please upload the Screenshots of your payment.</small>

        <!-- 拖拽区域 -->
        <div
          class="uploader"
          :class="{ 'is-dragover': dragOver }"
          @dragover.prevent="dragOver = true"
          @dragleave.prevent="dragOver = false"
          @drop.prevent="onDrop"
          @click="fileInput?.click()"
        >
          <div class="uploader-inner">
            <div class="uploader-icon">⤴︎</div>
            <div class="uploader-text">单击此处 / 将文件放在此处</div>
            <div class="uploader-sub">支持 JPG · PNG（最多 10 张，单张 ≤ 10MB）</div>
          </div>
          <input
            ref="fileInput"
            class="uploader-input"
            type="file"
            multiple
            accept="image/*"
            @change="onSelect"
          />
        </div>

        <!-- 预览列表（仅图片） -->
        <div v-if="uploads.length" class="uploader-list">
          <div v-for="f in uploads" :key="f.id" class="uploader-item">
            <div class="thumb">
              <img v-if="f.preview" :src="f.preview" alt="" />
            </div>

            <div class="meta">
              <div class="name" :title="f.file.name">{{ f.file.name }}</div>
              <div class="size">{{ (f.file.size/1024/1024).toFixed(2) }} MB</div>
            </div>

            <button type="button" class="remove" @click="removeUpload(f.id)">✕</button>
          </div>
        </div>

        <!-- 错误消息 -->
        <p v-if="uploadError" class="uploader-error">{{ uploadError }}</p>
      </div>

      <!-- 提交按钮 -->
      <div class="actions">
        <button type="submit" class="btn-submit" :disabled="submitting">
          {{ submitting ? 'Submitting…' : 'Submit' }}
        </button>
      </div>
    </form>
  </div>
</template>

<script setup>
import jsPDF from 'jspdf'             // ✅ 默认导入
import autoTable from 'jspdf-autotable' // ✅ 函数式调用
import { reactive, ref, computed, watch } from 'vue'
import NavBar from '@/components/NavBar.vue'

/* ===== 小工具 ===== */
const fmt = (n) => `$ ${Number(n).toFixed(2)}`
const genOrderId = () => 'PBA-' + Date.now().toString(36).toUpperCase()

/* ===== 表单数据 ===== */
const form = reactive({
  firstName: '',
  lastName: '',
  teamName: '',
  dob: '',
  contact: '',
  address: { street: '', city: '', state: '', postal: '', country: 'Australia' },
  phone: '',
  captain: '',
  emergency: '',
  division: ''
})

/* ===== 产品列表（图片来自 public/images） ===== */
const products = [
  { id: 1, name: 'S6 Individual player registration fee', desc: 'Every player has to choose this item', price: 229, image: '/images/registration.jpg' },
  { id: 2, name: 'PBA Jersey', desc: 'Players must wear a PBA jersey in order to play S6.', price: 68, image: '/images/jersey.jpg' },
  { id: 3, name: 'PBA Hoodie', desc: 'Optional', price: 88, image: '/images/hoodie.png' }
]

/* ===== 产品列表展开 ===== */
const showProducts = ref(false)
const toggleProducts = () => (showProducts.value = !showProducts.value)

/* ===== 商品详情弹窗 ===== */
const detailVisible = ref(false)
const detailProduct = reactive({})
const detailQty = ref(1)
function openDetail(item){ Object.assign(detailProduct, item); detailQty.value = 1; detailVisible.value = true }
function addDetailToCart(){ addToCart(detailProduct.id, detailQty.value); detailVisible.value = false }

/* ===== 购物车 ===== */
const cartMap = reactive(new Map())
const cartList = computed(() => Array.from(cartMap.values()))
const totalCount = computed(() => cartList.value.reduce((s,i)=>s+i.qty,0))
const totalAmount = computed(() => cartList.value.reduce((s,i)=>s+i.qty*i.price,0))

function addToCart(id, qty=1){
  const p = products.find(x=>x.id===id); if(!p) return
  const row = cartMap.get(id)
  if(row){ row.qty += qty; cartMap.set(id, {...row}) }
  else { cartMap.set(id, { id:p.id, name:p.name, price:p.price, image:p.image, qty }) }
}
function removeFromCart(id){ cartMap.delete(id) }
function setQty(id, v){
  let val = parseInt(v,10); if(isNaN(val) || val < 1) val = 1
  const row = cartMap.get(id); if(!row) return
  row.qty = val; cartMap.set(id, {...row})
}
function incQty(id){ const r=cartMap.get(id); if(!r) return; r.qty++; cartMap.set(id,{...r}) }
function decQty(id){ const r=cartMap.get(id); if(!r) return; r.qty=Math.max(1,r.qty-1); cartMap.set(id,{...r}) }
const cartVisible = ref(false)
function openCart(){ cartVisible.value = true }

/* ===== 弹窗打开时锁定 body 滚动，避免双滚轮与底部空白 ===== */
watch([detailVisible, cartVisible], ([d, c]) => {
  const open = d || c
  document.body.classList.toggle('modal-open', open)
})

/* ===== DOB 限 4 位年份 ===== */
function limitYear(e){
  let value = e.target.value.replace(/[^0-9-]/g, '')
  const [y,m,d] = value.split('-')
  const fixed = [(y||'').slice(0,4), m, d].filter(Boolean).join('-')
  e.target.value = fixed; form.dob = fixed
}

/* ===== 第 11 题状态 ===== */
const agree = reactive({ truth:false, media:false, liability:false, rules:false })

/* ===== 第 12 题：上传（仅图片） ===== */
const fileInput = ref(null)
const dragOver = ref(false)
const uploadError = ref('')
const uploads = reactive([]) // { id, file, type, preview }
const MAX_FILES = 10
const MAX_SIZE = 10 * 1024 * 1024
const ALLOW_TYPES = ['image/']  // ✅ 仅允许图片

function onSelect(e){ const files = Array.from(e.target.files || []); addFiles(files); e.target.value = '' }
function onDrop(e){ dragOver.value = false; const files = Array.from(e.dataTransfer?.files || []); addFiles(files) }

function addFiles(files){
  uploadError.value = ''
  if (uploads.length + files.length > MAX_FILES){ uploadError.value = `最多只能上传 ${MAX_FILES} 个文件`; return }
  files.forEach(async file=>{
    const okType = ALLOW_TYPES.some(t => file.type.startsWith(t))
    if(!okType){ uploadError.value = '仅支持图片文件（JPG/PNG）'; return }
    if(file.size > MAX_SIZE){ uploadError.value = '单个文件不能超过 10MB'; return }
    const id = `${file.name}-${file.size}-${Date.now()}`
    const item = { id, file, type:file.type, preview:'' }
    if(file.type.startsWith('image/')) item.preview = await fileToDataURL(file)
    uploads.push(item)
  })
}
function removeUpload(id){ const i=uploads.findIndex(x=>x.id===id); if(i!==-1) uploads.splice(i,1) }
function fileToDataURL(file){ return new Promise(res=>{ const r=new FileReader(); r.onload=()=>res(r.result); r.readAsDataURL(file) }) }

/* ===== 生成 PDF（使用 autoTable 函数式 API） ===== */
async function generatePdf({ form, cart, total, agree, uploads, orderId }) {
  const doc = new jsPDF({ unit: 'pt', format: 'a4' });
  const margin = 48;
  const pageH = doc.internal.pageSize.getHeight();
  const pageW = doc.internal.pageSize.getWidth();

  let y = 56;
  const needPage = (h) => { if (y + h > pageH - 56) { doc.addPage(); y = 56; } };

  doc.setFont('helvetica', 'bold').setFontSize(18);
  doc.text('PBA 2024 S6 Individual Registration', margin, y);
  y += 20;
  doc.setFont('helvetica', 'normal').setFontSize(11);
  doc.text(`Order ID: ${orderId}`, margin, y);
  y += 16;
  doc.text(`Submitted at: ${new Date().toLocaleString()}`, margin, y);
  y += 20;

  doc.setFont('helvetica', 'bold').setFontSize(13);
  doc.text('Player Info', margin, y); y += 10;

  doc.setFont('helvetica', 'normal').setFontSize(11);
  const addr = `${form.address.street}, ${form.address.city}, ${form.address.state} ${form.address.postal}, ${form.address.country}`;
  const info = [
    ['First Name', form.firstName],
    ['Last Name',  form.lastName],
    ['Team Name',  form.teamName],
    ['DOB',        form.dob],
    ['Contact',    form.contact],
    ['Phone',      form.phone || '-'],
    ["Captain's Name", form.captain || '-'],
    ['Emergency',  form.emergency],
    ['Address',    addr]
  ];

  autoTable(doc, {
    startY: y,
    head: [['Field', 'Value']],
    body: info,
    theme: 'grid',
    styles: { fontSize: 10, cellPadding: 6 },
    headStyles: { fillColor: [20, 20, 20], textColor: 255 },
    margin: { left: margin, right: margin },
    tableWidth: pageW - margin * 2,
  });
  y = doc.lastAutoTable.finalY + 16;

  doc.setFont('helvetica', 'bold').setFontSize(13);
  doc.text('Products', margin, y); y += 8;

  const cartTbl = cart.map(i => [i.name, fmt(i.price), String(i.qty), fmt(i.price * i.qty)]);
  autoTable(doc, {
    startY: y,
    head: [['Product', 'Unit', 'Qty', 'Amount']],
    body: cartTbl,
    theme: 'grid',
    styles: { fontSize: 10, cellPadding: 6 },
    headStyles: { fillColor: [20, 20, 20], textColor: 255 },
    margin: { left: margin, right: margin },
    tableWidth: pageW - margin * 2,
  });
  y = doc.lastAutoTable.finalY + 10;

  doc.setFont('helvetica', 'bold').setFontSize(12);
  doc.text(`Total: ${fmt(total)}`, margin, y);
  y += 18;

  doc.setFont('helvetica', 'bold').setFontSize(13);
  doc.text('Agreements', margin, y); y += 10;

  doc.setFont('helvetica', 'normal').setFontSize(11);
  const yn = (b) => (b ? 'Yes' : 'No');
  const agreeLines = [
    `Info above is true & valid: ${yn(agree.truth)}`,
    `Grant media release permission: ${yn(agree.media)}`,
    `Not liable for loss/damage or injury: ${yn(agree.liability)}`,
    `Agree to registration rules & policy: ${yn(agree.rules)}`
  ];
  for (const line of agreeLines) {
    needPage(16);
    doc.text(line, margin, y);
    y += 16;
  }

  // 付款截图（仅图片，两列自动分页）
  if (uploads && uploads.length) {
    needPage(12);
    doc.setFont('helvetica', 'bold').setFontSize(13);
    doc.text('Payment Screenshots', margin, y);
    y += 12;

    const thumbW = (pageW - margin * 2 - 12) / 2;
    const thumbH = 160;
    let x = margin, col = 0;

    for (const u of uploads) {
      if (!u.type?.startsWith('image/') || !u.preview) continue;
      const fmtImg = u.type.includes('png') ? 'PNG' : 'JPEG';
      if (y + thumbH > pageH - 56) { doc.addPage(); y = 56; x = margin; col = 0; }
      doc.setDrawColor(70); doc.setLineWidth(0.5);
      doc.rect(x - 1, y - 1, thumbW + 2, thumbH + 2);
      doc.addImage(u.preview, fmtImg, x, y, thumbW, thumbH);
      col++;
      if (col % 2 === 0) { x = margin; y += thumbH + 12; }
      else { x = margin + thumbW + 12; }
    }
  }

  return doc.output('blob');
}

/* ===== 提交 ===== */
const submitting = ref(false)

async function onSubmit(){
  if(submitting.value) return
  const reg = cartMap.get(1)
  if(!reg || reg.qty < 1){ alert('The individual registration fee is compulsory!'); return }
  if(!(agree.truth && agree.media && agree.liability && agree.rules)){
    alert('Please read and accept all items in Question 11.')
    return
  }
  if(uploads.length === 0){ alert('Please upload payment screenshot(s).'); return }

  submitting.value = true
  try{
    const orderId = genOrderId()
    const cart = cartList.value
    const total = totalAmount.value

    const pdfBlob = await generatePdf({ form, cart, total, agree, uploads, orderId })

    // 本地直接下载一份
    const url = URL.createObjectURL(pdfBlob)
    const a = document.createElement('a')
    a.href = url; a.download = `${orderId}.pdf`; a.click()
    URL.revokeObjectURL(url)

    // 拼接邮件 FormData（走 /api 代理）
    const fd = new FormData()
    fd.append('orderId', orderId)
    fd.append('to', 'director@perfectballers.com') // ✅ 目标邮箱
    fd.append('subject', `PBA Registration - ${orderId}`)
    fd.append('text', [
      `Order ID: ${orderId}`,
      `Name: ${form.firstName} ${form.lastName}`,
      `Team: ${form.teamName}`,
      `Contact: ${form.contact}`,
      `Total: ${fmt(total)}`
    ].join('\n'))
    fd.append('attachments', new File([pdfBlob], `${orderId}.pdf`, { type:'application/pdf' }))
    uploads.forEach(u => fd.append('attachments', u.file, u.file.name))

    const res = await fetch('/api/send-registration', { method:'POST', body: fd })
    if(!res.ok) throw new Error('Email send failed')

    alert('Submitted successfully! Your PDF has been generated and sent by email. ✅')
  }catch(err){
    console.error(err)
    alert('Submission failed. Please try again later.')
  }finally{
    submitting.value = false
  }
}
</script>

<style scoped>
/* ✅ 全局关闭横向滚动 + 高度兜底 */
:global(html, body, #app) {
  height: auto;
  min-height: 100%;
  overflow-x: hidden !important;
}

/* ✅ 弹窗打开时锁定页面滚动 */
:global(body.modal-open) {
  overflow: hidden !important;
}

/* 页面与表单 */
.page{
  background:#0f0f0f;
  color:#f2f2f2;
  padding:calc(var(--header-h, 64px) + 12px) 16px 24px;
  overflow-x: hidden;
}
.form{width:min(720px,100%);margin:0 auto;}
.title{text-align:center;font-size:clamp(24px,2.3vw,34px);margin:8px 0 26px;font-weight:800;}
.row{margin-bottom:22px;}
.label{display:block;font-size:18px;font-weight:700;margin-bottom:10px;}
.label span{color:#ff6b82;}
input,textarea,select{width:100%;background:#1a1a1a;border:1px solid #2a2a2a;border-radius:10px;padding:14px 16px;color:#f2f2f2;}
input::placeholder,textarea::placeholder{color:#8a8a8a;}
.grid-2{display:grid;grid-template-columns:1fr 1fr;gap:50px;}
.grid-addr{display:grid;grid-template-columns:1fr 1fr 1fr 1fr;gap:50px;margin-top:10px;}

/* 购物车与产品 */
.cart-status{display:flex;align-items:center;justify-content:space-between;background:#1a1a1a;border:1px solid #2a2a2a;border-radius:12px;padding:12px 16px;margin-bottom:12px;}
.total{color:#00bfff;font-weight:700;}
.cart-icon{position:relative;width:48px;height:48px;border-radius:999px;background:#07c1d4;color:#fff;font-size:22px;display:flex;align-items:center;justify-content:center;border:none;cursor:pointer;}
.cart-icon .badge{position:absolute;right:-2px;top:-2px;min-width:20px;height:20px;padding:0 6px;border-radius:999px;background:#ef4444;color:#fff;font-size:12px;line-height:20px;text-align:center;}
.list-btn{width:100%;background:#1a1a1a;border:1px solid #2a2a2a;border-radius:12px;color:#eaeaea;text-align:left;padding:12px 16px;margin-bottom:14px;cursor:pointer;}

.product-grid{display:grid;grid-template-columns:1fr 1fr;gap:20px;margin-top:20px;}
.product-card{background:#1a1a1a;border:1px solid #2a2a2a;border-radius:10px;overflow:hidden;cursor:pointer;transition:all .2s;}
.product-card:hover{border-color:#ff6b82;}
.product-img{width:100%;height:200px;object-fit:contain;background:#0000;padding:5px;display:block;margin:0 auto;}
.product-info{padding:12px;}
.product-info h3{font-size:16px;margin-bottom:4px;}
.product-info .desc{font-size:14px;color:#aaa;}
.product-info .price{margin-top:8px;font-size:14px;}
.product-info .price span{color:#00bfff;font-weight:700;}

/* 弹窗 */
.modal{position:fixed;inset:0;background:rgba(0,0,0,.55);display:flex;align-items:center;justify-content:center;z-index:1000;}
.modal-panel{width:min(860px, 92%);max-width:96vw;max-height:90vh;overflow:auto;background:#222;border-radius:16px;box-shadow:0 10px 40px rgba(0,0,0,.5);position:relative;padding:18px;}
.modal-panel.wide{width:min(980px,96%);max-width:96vw;max-height:90vh;overflow:auto;}
.modal-close{position:absolute;top:10px;right:14px;width:36px;height:36px;border:none;border-radius:8px;background:#333;color:#fff;font-size:22px;cursor:pointer;}
.btn{border:none;border-radius:12px;padding:10px 16px;cursor:pointer;font-weight:700;}
.btn.primary{background:#07c1d4;color:#001018;}
.btn.ghost{background:#333;color:#fff;}

.detail-body{display:grid;grid-template-columns:1fr 1fr;gap:18px;}
.detail-img{width:100%;height:320px;object-fit:contain;background:#2a2a2a;border-radius:12px;}
.detail-info{display:flex;flex-direction:column;gap:12px;}
.detail-title{font-size:22px;margin:0;}
.detail-desc{color:#cfcfcf;}
.detail-price-line{display:flex;align-items:center;gap:12px;margin-top:4px;}
.detail-price{color:#00bfff;font-size:20px;}
.qty-line{display:flex;align-items:center;gap:8px;}
.qty-btn{width:36px;height:36px;border:none;border-radius:8px;background:#333;color:#fff;font-size:18px;cursor:pointer;}
.qty-input{width:64px;height:36px;border:1px solid #444;border-radius:8px;background:#1a1a1a;color:#fff;text-align:center;}

/* 购物车表 */
.cart-table{width:100%;overflow-x:auto;}
.thead,.trow{display:grid;grid-template-columns:1fr 120px 140px 120px 60px;align-items:center;gap:8px;min-width:640px;}
.thead{font-weight:800;margin:10px 0;}
.trow{padding:10px 0;border-top:1px solid #333;}
.c-price,.c-sub{font-weight:700;}
.c-qty{display:flex;align-items:center;gap:8px;}
.icon-btn{border:none;background:#333;color:#fff;border-radius:8px;padding:6px 8px;cursor:pointer;}
.tfoot{display:flex;justify-content:flex-end;align-items:center;gap:12px;font-size:18px;font-weight:800;padding:12px 0;border-top:1px solid #333;}
.tfoot-val{color:#00bfff;}
.cart-actions{display:flex;justify-content:flex-end;gap:10px;margin-top:8px;}

/* 说明与政策 */
.product-declare{margin-top:20px;padding:16px;background:#1a1a1a;border-radius:10px;font-size:14px;line-height:1.5;}
.policy{margin-top:20px;padding:16px;background:#1a1a1a;border-radius:10px;font-size:14px;line-height:1.6;}

/* 响应式 */
@media (max-width:1200px){
  .grid-2{gap:24px;}
  .grid-addr{gap:24px;}
}
@media (max-width:780px){
  .grid-2{grid-template-columns:1fr;gap:20px;}
  .grid-addr{grid-template-columns:1fr 1fr;gap:20px;}
  .product-grid{grid-template-columns:1fr;}
  .detail-body{grid-template-columns:1fr;}
}

/* 11：卡片式复选框 */
.agree-list{display:flex;flex-direction:column;gap:16px;}
.agree-item{display:flex;align-items:flex-start;gap:14px;padding:16px 18px;background:#1a1a1a;border:1px solid #2a2a2a;border-radius:14px;cursor:pointer;user-select:none;transition:border-color .15s,box-shadow .15s,background .15s;}
.agree-item:hover,.agree-item:focus-within{border-color:#3a8ea3;}
.agree-item.checked{border-color:#00bcd4;box-shadow:0 0 0 1px #00bcd4 inset;}
.agree-item input[type="checkbox"]{appearance:none;-webkit-appearance:none;position:absolute;opacity:0;pointer-events:none;}
.agree-item .box{flex:0 0 22px;width:22px;height:22px;border-radius:6px;border:2px solid #555;background:#111;margin-top:2px;position:relative;transition:all .15s;}
.agree-item input[type="checkbox"]:checked + .box{border-color:#07c1d4;background:#07c1d4;}
.agree-item input[type="checkbox"]:checked + .box::after{content:"";position:absolute;left:6px;top:2px;width:6px;height:12px;border:3px solid #001018;border-left:none;border-top:none;transform:rotate(45deg);}
.agree-item .text{font-size:clamp(15px,2vw,20px);line-height:1.55;color:#eaeaea;}

/* 12：上传（仅图片） */
.uploader{position:relative;margin-top:10px;background:#1a1a1a;border:2px dashed #3a3a3a;border-radius:14px;padding:28px 16px;text-align:center;cursor:pointer;transition:border-color .15s,background .15s;}
.uploader:hover{border-color:#4a4a4a;}
.uploader.is-dragover{border-color:#00bcd4;background:#181e21;}
.uploader-inner{pointer-events:none;}
.uploader-icon{font-size:28px;opacity:.9;}
.uploader-text{margin-top:8px;font-size:18px;color:#eaeaea;}
.uploader-sub{margin-top:4px;font-size:13px;color:#a9a9a9;}
.uploader-input{position:absolute;inset:0;opacity:0;pointer-events:none;}
.uploader-list{margin-top:12px;display:grid;grid-template-columns:1fr;gap:10px;}
.uploader-item{display:flex;align-items:center;gap:12px;background:#151515;border:1px solid #2a2a2a;border-radius:12px;padding:10px;}
.thumb{width:56px;height:56px;border-radius:10px;overflow:hidden;background:#2a2a2a;display:flex;align-items:center;justify-content:center;color:#ddd;font-weight:700;}
.thumb img{width:100%;height:100%;object-fit:cover;}
.meta{flex:1;min-width:0;}
.name{white-space:nowrap;overflow:hidden;text-overflow:ellipsis;}
.size{font-size:12px;color:#9c9c9c;margin-top:2px;}
.remove{border:none;background:#333;color:#fff;border-radius:8px;padding:6px 10px;cursor:pointer;}
.remove:hover{filter:brightness(1.1);}
.uploader-error{color:#ff6b82;margin-top:8px;}

/* 提交按钮 */
.actions{text-align:center;margin-top:28px;}
.btn-submit{appearance:none;border:none;background:#07c1d4;color:#fff;font-weight:800;font-size:18px;padding:14px 32px;border-radius:14px;cursor:pointer;box-shadow:0 6px 16px rgba(7,193,212,.25);transition:transform .12s, box-shadow .12s, filter .12s;}
.btn-submit:hover{transform:translateY(-1px);box-shadow:0 10px 22px rgba(7,193,212,.35);filter:brightness(1.02);}
.btn-submit:active{transform:translateY(0);box-shadow:0 6px 16px rgba(7,193,212,.25);}
.btn-submit:focus-visible{outline:none;box-shadow:0 0 0 3px rgba(7,193,212,.6);}
.btn-submit:disabled{opacity:.55;cursor:not-allowed;filter:grayscale(10%);}
</style>
