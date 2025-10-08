<!-- src/views/EnrolTeam.vue -->
<template>
  <NavBar />

  <div class="page">
    <form class="form" @submit.prevent="onSubmit">
      <h1 class="title">PBA 2024 S6 Team Registration Form  (1)</h1>

      <!-- 1. Team Name -->
      <div class="row">
        <label class="label">1. Team Name <span>*</span></label>
        <small class="hint">Your Team Name will be recorded during season 6</small>
        <div class="input-wrap">
          <input
            v-model.trim="form.teamName"
            :class="{ 'is-invalid': teamNameInvalid }"
            placeholder="3–15 characters"
            @input="limitTeamName"
            required
          />
          <span class="count">{{ form.teamName.length }}/15</span>
        </div>
        <p v-if="teamNameInvalid" class="err">Team name must be 3–15 characters.</p>
      </div>

      <!-- 2. Division preference -->
      <div class="row">
        <label class="label">2. Choose your division preference <span>*</span></label>
        <div class="check-cards">
          <label class="check-card" :class="{ checked: hasDiv('Championship') }">
            <input type="checkbox" value="Championship" v-model="form.divisions" />
            <span class="box" aria-hidden="true"></span><span class="text">Championship</span>
          </label>
          <label class="check-card" :class="{ checked: hasDiv('Division 1') }">
            <input type="checkbox" value="Division 1" v-model="form.divisions" />
            <span class="box" aria-hidden="true"></span><span class="text">Division 1</span>
          </label>
          <label class="check-card" :class="{ checked: hasDiv('Division 2') }">
            <input type="checkbox" value="Division 2" v-model="form.divisions" />
            <span class="box" aria-hidden="true"></span><span class="text">Division 2</span>
          </label>
        </div>
        <p v-if="divisionInvalid" class="err">Please choose at least one division.</p>
      </div>

      <!-- 3. Team Size -->
      <div class="row">
        <label class="label">3. How many People in Your Team <span>*</span></label>
        <div class="select-wrap">
          <select v-model="form.teamSize" required>
            <option disabled value="">choose</option>
            <option v-for="n in teamSizeOptions" :key="n" :value="n">{{ n }}</option>
          </select>
          <span class="select-caret">▾</span>
        </div>
      </div>

      <!-- 4. Personal Details -->
      <div class="row">
        <label class="label">
          4. Personal Details (Full Name + Date Of Birth + Phone Number +Email) <span>*</span>
        </label>
        <small class="hint">
          To ensure the insurance is assigned properly, All team members' details are required
        </small>
        <textarea
          v-model.trim="form.personalDetails"
          rows="5"
          placeholder="E.g Thomas, 1988/12/29, 0488888888, 123@gmail.com"
          required
        />
      </div>

      <!-- 5. Captain's name -->
      <div class="row">
        <label class="label">5. Captain's name <span>*</span></label>
        <small class="hint">The member representing your team to communicate with PBA</small>
        <input v-model.trim="form.captainName" required placeholder="T" />
      </div>

      <!-- 6. Captain's Email -->
      <div class="row">
        <label class="label">6. Captain's E-mail <span>*</span></label>
        <div class="grid-2">
          <input
            v-model.trim="form.captainEmail"
            type="email"
            placeholder="email"
            :class="{ 'is-invalid': emailInvalid }"
            required
          />
          <input
            v-model.trim="form.captainEmail2"
            type="email"
            placeholder="确认邮件"
            :class="{ 'is-invalid': email2Invalid }"
            required
          />
        </div>
        <p v-if="emailInvalid" class="err">Please enter a valid email.</p>
        <p v-if="email2Invalid" class="err">Emails do not match.</p>
      </div>

      <!-- 7. Captain's WeChat -->
      <div class="row">
        <label class="label">7. Captain's WeChat Number</label>
        <small class="hint">Make sure your number is correct</small>
        <input v-model.trim="form.captainWeChat" placeholder="T" />
      </div>

      <!-- 8. Products -->
      <div class="row">
        <label class="label">8. PBA × Golden Age S6 REGISTRATION AND JERSEY <span>*</span></label>
        <small class="hint">Two options of PBA Jersey can be chosen.</small>

        <!-- cart status -->
        <div class="cart-status">
          <p>总金额： <span class="total">${{ totalAmount.toFixed(2) }}</span></p>
          <button type="button" class="cart-icon" @click="openCart">
            <span class="badge" v-if="totalCount > 0">{{ totalCount }}</span> 🛒
          </button>
        </div>

        <button type="button" class="list-btn" @click="toggleProducts">
          {{ showProducts ? '收起产品列表' : `列出${products.length}产品` }}
        </button>

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
              <p class="desc" v-if="item.desc">{{ item.desc }}</p>
              <p class="price">
                <template v-if="item.unit === 'team'">Per team:</template>
                <template v-else>Per person:</template>
                <span> ${{ item.price.toFixed(2) }}</span>
              </p>
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
                  <span>{{ detailProduct.unit === 'team' ? 'per team' : 'per person' }}</span>
                  <strong class="detail-price">${{ detailProduct.price?.toFixed(2) }}</strong>
                </div>

                <div class="qty-line" v-if="detailProduct.unit !== 'team'">
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
                <div class="c-qty" v-if="row.unit !== 'team'">
                  <button type="button" class="qty-btn" @click="decQty(row.id)">-</button>
                  <input class="qty-input" type="number" min="1" :value="row.qty" @input="setQty(row.id, $event.target.value)" />
                  <button type="button" class="qty-btn" @click="incQty(row.id)">+</button>
                </div>
                <div class="c-qty" v-else>—</div>
                <div class="c-sub">${{ (row.price * (row.qty || 1)).toFixed(2) }}</div>
                <div class="c-del"><button type="button" class="icon-btn" @click="removeFromCart(row.id)">🗑️</button></div>
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
          <p><strong>Team Registration fee is compulsory</strong> for playing in Season 6, it will contain:</p>
          <ul>
            <li>Every group member's insurance</li>
            <li>Ability to join the PBA Season 5 games</li>
            <li>Having a discount for joining selected PBA event</li>
            <li>Having personal statistics for every game</li>
            <li>Having professional photographers and videographers for Championship</li>
          </ul>
          <p>
            <strong>Our customer service</strong> will contact the team captain regards the jersey customize via WeChat,
            if you don't have WeChat, we will contact you via phone message
          </p>
        </div>
      </div>

      <!-- 9. Terms -->
      <div class="row">
        <label class="label">9. Make Sure You Accept The "Term and Condition",  <span>*</span></label>
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
            <span class="text">I acknowledge and agree to the registration rules and policy.</span>
          </label>
        </div>
      </div>

      <!-- Payment Info -->
      <div class="row">
        <label class="label">Payment:</label>
        <div class="payment">
          <p>Please use Bank Transfer to pay your team registration fee and Jerseys, the price is show on the product menu, follow that price to make this payment.</p>
          <p>Please remember use your team name as Bank Transfer Reference and take a screenshot.</p>
          <p>Transfer details shows below:</p>
          <p><strong>Name:</strong> PBA</p>
          <p><strong>BSB:</strong> 063 238</p>
          <p><strong>Account Number:</strong> 1133 7308</p>
          <p><strong>Reference:</strong> Team Name + Captain Name</p>
        </div>
      </div>

      <!-- 10. Payment Upload（仅图片） -->
      <div class="row">
        <label class="label">10. Payment Upload <span>*</span></label>
        <small class="hint">Please upload the Screenshots of your payment.</small>

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
          <input ref="fileInput" class="uploader-input" type="file" multiple accept="image/*" @change="onSelect" />
        </div>

        <div v-if="uploads.length" class="uploader-list">
          <div v-for="f in uploads" :key="f.id" class="uploader-item">
            <div class="thumb"><img v-if="f.preview" :src="f.preview" alt="" /></div>
            <div class="meta">
              <div class="name" :title="f.file.name">{{ f.file.name }}</div>
              <div class="size">{{ (f.file.size/1024/1024).toFixed(2) }} MB</div>
            </div>
            <button type="button" class="remove" @click="removeUpload(f.id)">✕</button>
          </div>
        </div>
        <p v-if="uploadError" class="uploader-error">{{ uploadError }}</p>
      </div>

      <!-- Submit -->
      <div class="actions">
        <button type="submit" class="btn-submit" :disabled="submitting">
          {{ submitting ? 'Submitting…' : 'Submit' }}
        </button>
      </div>
    </form>
  </div>
</template>

<script setup>
import { reactive, ref, computed, watch } from 'vue'
import NavBar from '@/components/NavBar.vue'
import { jsPDF } from 'jspdf'
import defaultTeam from '@/assets/images/default-team.png'
import autoTable from 'jspdf-autotable'



/* ✅ 引入你前端目录中的本地图片 */
import logoDefault from '@/assets/images/default-team.png'
import jersey1Img  from '@/assets/images/球衣1.png'
import jersey2Img  from '@/assets/images/球衣2.png'
import jersey3Img  from '@/assets/images/球衣3.png'
import pba1Img     from '@/assets/images/pba1.jpg'
import pba2Img     from '@/assets/images/pba2.jpg'

const fmt = (n) => `$ ${Number(n).toFixed(2)}`
const genOrderId = () => 'PBA-TEAM-' + Date.now().toString(36).toUpperCase()

/* ===== 表单 ===== */
const form = reactive({
  teamName: '',
  divisions: [],
  teamSize: '',
  personalDetails: '',
  captainName: '',
  captainEmail: '',
  captainEmail2: '',
  captainWeChat: ''
})

const teamSizeOptions = [5,6,7,8,9,10]
const teamNameInvalid = computed(()=> form.teamName && (form.teamName.length<3 || form.teamName.length>15))
function limitTeamName(){ if(form.teamName.length>15) form.teamName = form.teamName.slice(0,15) }
const divisionInvalid = computed(()=> form.divisions.length===0)
const hasDiv = (v)=> form.divisions.includes(v)

const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
const emailInvalid  = computed(()=> form.captainEmail.length>0  && !emailRegex.test(form.captainEmail))
const email2Invalid = computed(()=> form.captainEmail2.length>0 && form.captainEmail2 !== form.captainEmail)

/* ===== 产品（改成本地 import 图片）===== */
const products = [
  { id: 101, name: 'Registration Fee', desc: 'S6 Championship Registration Fee',            price: 1599, unit:'team',    image: defaultTeam },
  { id: 102, name: 'Registration Fee', desc: 'S6 Division 1 or Division 2 Registration Fee', price: 1399, unit:'team',    image: defaultTeam },
  { id: 201, name: 'PBA Customize Jersey', desc: '-Optional, team must choose the same type-Players must wear a PBA jersey in order to play Season 6.', price: 68, unit:'person', image: jersey1Img },
  { id: 202, name: 'PBA S1 Jersey',       desc: '-Optional, team must choose the same type-Players must wear a PBA jersey in order to play Season 6.', price: 68, unit:'person', image: jersey2Img },
  { id: 301, name: 'PBA Customise Warm-up Shirt', desc: '-Optional', price: 88, unit:'person', image: jersey3Img },
]

const showProducts = ref(true)
const toggleProducts = ()=> showProducts.value = !showProducts.value

/* ===== 详情弹窗 + 购物车 ===== */
const detailVisible = ref(false)
const detailProduct = reactive({})
const detailQty = ref(1)
function openDetail(item){ Object.assign(detailProduct, item); detailQty.value=1; detailVisible.value=true }
function addDetailToCart(){
  addToCart(detailProduct.id, detailProduct.unit==='team' ? 1 : detailQty.value)
  detailVisible.value=false
}

const cartMap = reactive(new Map())
const cartList = computed(()=> Array.from(cartMap.values()))
const totalCount = computed(()=> cartList.value.reduce((s,i)=> s + (i.unit==='team'?1:i.qty), 0))
const totalAmount = computed(()=> cartList.value.reduce((s,i)=> s + i.price * (i.unit==='team'?1:i.qty), 0))

function addToCart(id, qty=1){
  const p = products.find(x=>x.id===id); if(!p) return
  if(p.unit==='team'){
    cartMap.set(p.id, { id:p.id, name:p.name, price:p.price, unit:'team', qty:1, image:p.image })
  }else{
    const row = cartMap.get(id)
    if(row){ row.qty += qty; cartMap.set(id, {...row}) }
    else { cartMap.set(id, { id:p.id, name:p.name, price:p.price, qty, unit:'person', image:p.image }) }
  }
}
function removeFromCart(id){ cartMap.delete(id) }
function setQty(id, v){ let val=parseInt(v,10); if(isNaN(val)||val<1) val=1; const row=cartMap.get(id); if(!row) return; row.qty=val; cartMap.set(id,{...row}) }
function incQty(id){ const r=cartMap.get(id); if(!r) return; r.qty++; cartMap.set(id,{...r}) }
function decQty(id){ const r=cartMap.get(id); if(!r) return; r.qty=Math.max(1, r.qty-1); cartMap.set(id,{...r}) }
const cartVisible = ref(false)
const openCart = ()=> cartVisible.value = true

watch([detailVisible, cartVisible], ([d,c])=>{
  document.body.classList.toggle('modal-open', d||c)
})

/* ===== 上传（仅图片） ===== */
const fileInput = ref(null)
const dragOver = ref(false)
const uploadError = ref('')
const uploads = reactive([]) // { id, file, type, preview }
const MAX_FILES = 10
const MAX_SIZE = 10 * 1024 * 1024
const ALLOW_TYPES = ['image/']

function onSelect(e){ const files = Array.from(e.target.files||[]); addFiles(files); e.target.value='' }
function onDrop(e){ dragOver.value=false; const files=Array.from(e.dataTransfer?.files||[]); addFiles(files) }

async function addFiles(files){
  uploadError.value=''
  if(uploads.length + files.length > MAX_FILES){ uploadError.value = `最多只能上传 ${MAX_FILES} 个文件`; return }
  for (const file of files){
    const okType = ALLOW_TYPES.some(t=> file.type.startsWith(t))
    if(!okType){ uploadError.value = '仅支持图片文件（JPG/PNG）'; continue }
    if(file.size > MAX_SIZE){ uploadError.value = '单个文件不能超过 10MB'; continue }
    const id = `${file.name}-${file.size}-${Date.now()}`
    const item = { id, file, type:file.type, preview: await fileToDataURL(file) }
    uploads.push(item)
  }
}
function removeUpload(id){ const i=uploads.findIndex(x=>x.id===id); if(i!==-1) uploads.splice(i,1) }
function fileToDataURL(file){ return new Promise(res=>{ const r=new FileReader(); r.onload=()=>res(r.result); r.readAsDataURL(file) }) }

/* ===== 协议 ===== */
const agree = reactive({ truth:false, media:false, liability:false, rules:false })

/* ===== PDF ===== */
async function generatePdf({ form, cart, total, agree, uploads, orderId }) {
  const doc = new jsPDF({ unit: 'pt', format: 'a4' });
  const margin = 48;
  const pageH = doc.internal.pageSize.getHeight();
  const pageW = doc.internal.pageSize.getWidth();

  let y = 56;
  const needPage = (h) => { if (y + h > pageH - 56) { doc.addPage(); y = 56; } };

  doc.setFont('helvetica', 'bold').setFontSize(18);
  doc.text('PBA 2024 S6 Team Registration', margin, y);
  y += 20;
  doc.setFont('helvetica', 'normal').setFontSize(11);
  doc.text(`Order ID: ${orderId}`, margin, y); y += 16;
  doc.text(`Submitted at: ${new Date().toLocaleString()}`, margin, y); y += 20;

  // —— Team Info 表格（改成 autoTable(doc, {...})）——
  doc.setFont('helvetica', 'bold').setFontSize(13);
  doc.text('Team Info', margin, y); y += 10;

  const info = [
    ['Team Name', form.teamName],
    ['Divisions', form.divisions.join(', ')],
    ['Team Size', String(form.teamSize)],
    ['Captain Name', form.captainName],
    ['Captain Email', form.captainEmail],
    ['Captain WeChat', form.captainWeChat || '-'],
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

  // —— Personal Details 原文 —— 
  doc.setFont('helvetica','bold').setFontSize(13);
  doc.text('Personal Details (raw)', margin, y); y += 8;
  doc.setFont('helvetica','normal').setFontSize(10);
  const lines = doc.splitTextToSize(form.personalDetails || '-', pageW - margin*2);
  for(const line of lines){ needPage(14); doc.text(line, margin, y); y+=14; }

  // —— Products 表格（也改成 autoTable(doc, {...})）——
  doc.setFont('helvetica','bold').setFontSize(13); y+=10;
  doc.text('Products', margin, y); y += 8;

  const cartTbl = cart.map(i => [
    i.name,
    i.unit==='team' ? 'per team' : 'per person',
    `$ ${Number(i.price).toFixed(2)}`,
    String(i.unit==='team' ? 1 : i.qty),
    `$ ${Number(i.price*(i.unit==='team'?1:i.qty)).toFixed(2)}`
  ]);

  autoTable(doc, {
    startY: y,
    head: [['Product','Unit','Unit Price','Qty','Amount']],
    body: cartTbl,
    theme: 'grid',
    styles: { fontSize: 10, cellPadding: 6 },
    headStyles: { fillColor: [20,20,20], textColor: 255 },
    margin: { left: margin, right: margin },
    tableWidth: pageW - margin * 2,
  });
  y = doc.lastAutoTable.finalY + 10;

  doc.setFont('helvetica','bold').setFontSize(12);
  doc.text(`Total: $ ${Number(total).toFixed(2)}`, margin, y); y += 18;

  // —— Agreements —— 
  doc.setFont('helvetica','bold').setFontSize(13);
  doc.text('Agreements', margin, y); y += 10;
  doc.setFont('helvetica','normal').setFontSize(11);
  const yn = (b)=> b?'Yes':'No'
  ;[
    `Info above is true & valid: ${yn(agree.truth)}`,
    `Grant media release permission: ${yn(agree.media)}`,
    `Not liable for loss/damage or injury: ${yn(agree.liability)}`,
    `Agree to registration rules & policy: ${yn(agree.rules)}`
  ].forEach(line=>{ needPage(16); doc.text(line, margin, y); y+=16 })

  // —— Payment Screenshots —— 
  if(uploads && uploads.length){
    needPage(12);
    doc.setFont('helvetica','bold').setFontSize(13);
    doc.text('Payment Screenshots', margin, y); y += 12;
    const thumbW = (pageW - margin*2 - 12)/2, thumbH = 160; let x=margin, col=0;
    for(const u of uploads){
      if(!u.type?.startsWith('image/') || !u.preview) continue;
      const fmtImg = u.type.includes('png') ? 'PNG' : 'JPEG';
      if(y + thumbH > pageH - 56){ doc.addPage(); y=56; x=margin; col=0; }
      doc.setDrawColor(70); doc.setLineWidth(0.5); doc.rect(x-1,y-1,thumbW+2,thumbH+2);
      doc.addImage(u.preview, fmtImg, x, y, thumbW, thumbH);
      col++; if(col%2===0){ x=margin; y+=thumbH+12 } else { x=margin+thumbW+12 }
    }
  }
  return doc.output('blob');
}

/* ===== 提交 ===== */
const submitting = ref(false)

async function onSubmit(){
  if(submitting.value) return

  // ✅ 前置校验（保持和你现在一致）
  if(teamNameInvalid.value || divisionInvalid.value || emailInvalid.value || email2Invalid.value){
    alert('Please complete required fields correctly.')
    return
  }
  const hasTeamReg = cartList.value.some(i => i.unit==='team')
  if(!hasTeamReg){
    alert('Team Registration fee is compulsory! Please add it in products.')
    return
  }
  if(!(agree.truth && agree.media && agree.liability && agree.rules)){
    alert('Please read and accept all items in Terms.')
    return
  }
  if(uploads.length === 0){
    alert('Please upload payment screenshot(s).')
    return
  }

  submitting.value = true
  try{
    const orderId = genOrderId()
    const cart = cartList.value
    const total = totalAmount.value

    // ✅ 生成并自动下载 PDF
    const pdfBlob = await generatePdf({ form, cart, total, agree, uploads, orderId })
    const url = URL.createObjectURL(pdfBlob)
    const a = document.createElement('a'); a.href = url; a.download = `${orderId}.pdf`; a.click()
    URL.revokeObjectURL(url)

    // ✅ 发送邮件
    const fd = new FormData()
    fd.append('orderId', orderId)
    fd.append('to', 'director@perfectballers.com') // 固定接收人
    fd.append('subject', `PBA Team Registration - ${orderId}`)
    fd.append('text', [
      `Order ID: ${orderId}`,
      `Team: ${form.teamName}`,
      `Divisions: ${form.divisions.join(', ')}`,
      `Team Size: ${form.teamSize}`,
      `Captain: ${form.captainName}`,
      `Email: ${form.captainEmail}`,
      `WeChat: ${form.captainWeChat || '-'}`,
      `Total: $ ${Number(total).toFixed(2)}`
    ].join('\n'))
    fd.append('attachments', new File([pdfBlob], `${orderId}.pdf`, { type:'application/pdf' }))
    uploads.forEach(u => fd.append('attachments', u.file, u.file.name))

    // ⚠️ 用和 Individual 完全一致的地址（可用 .env 配置），避免 127.0.0.1/localhost 不一致引发 CORS
    const API = import.meta.env.VITE_MAIL_API ?? 'http://127.0.0.1:3001/api/send-registration'

    const res = await fetch(API, { method:'POST', body: fd })
    const respText = await res.text().catch(()=> '')
    if(!res.ok){
      // 打印详细错误，定位更快（比如 404/413/500）
      console.error('MAIL API ERROR', res.status, res.statusText, respText)
      throw new Error(`${res.status} ${res.statusText} - ${respText || 'Email send failed'}`)
    }

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
:global(html, body, #app){ height:auto; min-height:100%; overflow-x:hidden!important; }
:global(body.modal-open){ overflow:hidden!important; }

.page{ background:#0f0f0f; color:#f2f2f2; padding:calc(var(--header-h,64px)+12px) 16px 24px; overflow-x:hidden; }
.form{ width:min(720px,100%); margin:0 auto; }
.title{ text-align:center; font-size:clamp(24px,2.3vw,34px); margin:8px 0 26px; font-weight:800; }
.row{ margin-bottom:26px; }
.label{ display:block; font-size:18px; font-weight:700; margin-bottom:10px; }
.label span{ color:#16a34a; }
.hint{ display:block; color:#9aa3a9; margin-bottom:10px; }

input,textarea,select{
  width:100%; background:#1a1a1a; border:1px solid #2a2a2a; border-radius:10px;
  padding:14px 16px; color:#f2f2f2;
}
input::placeholder,textarea::placeholder{ color:#8a8a8a; }
.grid-2{ display:grid; grid-template-columns:1fr 1fr; gap:50px; }
@media (max-width:780px){ .grid-2{ grid-template-columns:1fr; gap:20px; } }

.input-wrap{ position:relative; }
.count{ position:absolute; right:12px; bottom:-22px; font-size:12px; color:#7f8a90; }
.is-invalid{ border-color:#ff6b82; }
.err{ color:#ff6b82; font-size:13px; margin-top:8px; }

.select-wrap{ position:relative; }
.select-caret{ position:absolute; right:16px; top:50%; transform:translateY(-50%); pointer-events:none; opacity:.7; }

.check-cards{ display:flex; flex-direction:column; gap:12px; }
.check-card{
  display:flex; align-items:center; gap:14px; padding:14px 16px;
  background:#1a1a1a; border:1px solid #2a2a2a; border-radius:12px;
  cursor:pointer; user-select:none; transition:border-color .15s,box-shadow .15s,background .15s;
}
.check-card:hover,.check-card:focus-within{ border-color:#3a8ea3; }
.check-card.checked{ border-color:#00bcd4; box-shadow:0 0 0 1px #00bcd4 inset; }
.check-card input[type="checkbox"]{ appearance:none; -webkit-appearance:none; position:absolute; opacity:0; pointer-events:none; }
.check-card .box{ flex:0 0 22px; width:22px; height:22px; border-radius:6px; border:2px solid #555; background:#111; position:relative; transition:all .15s; }
.check-card input[type="checkbox"]:checked + .box{ border-color:#07c1d4; background:#07c1d4; }
.check-card input[type="checkbox"]:checked + .box::after{
  content:""; position:absolute; left:6px; top:2px; width:6px; height:12px; border:3px solid #001018;
  border-left:none; border-top:none; transform:rotate(45deg);
}
.check-card .text{ font-size:16px; color:#eaeaea; }

.cart-status{ display:flex; align-items:center; justify-content:space-between; background:#1a1a1a; border:1px solid #2a2a2a; border-radius:12px; padding:12px 16px; margin-bottom:12px; }
.total{ color:#00bfff; font-weight:700; }
.cart-icon{ position:relative; width:48px; height:48px; border-radius:999px; background:#07c1d4; color:#fff; font-size:22px; display:flex; align-items:center; justify-content:center; border:none; cursor:pointer; }
.cart-icon .badge{ position:absolute; right:-2px; top:-2px; min-width:20px; height:20px; padding:0 6px; border-radius:999px; background:#ef4444; color:#fff; font-size:12px; line-height:20px; text-align:center; }
.list-btn{ width:100%; background:#1a1a1a; border:1px solid #2a2a2a; border-radius:12px; color:#eaeaea; text-align:left; padding:12px 16px; margin-bottom:14px; cursor:pointer; }

.product-grid{ display:grid; grid-template-columns:1fr 1fr; gap:20px; margin-top:20px; }
@media (max-width:780px){ .product-grid{ grid-template-columns:1fr; } }
.product-card{ background:#1a1a1a; border:1px solid #2a2a2a; border-radius:10px; overflow:hidden; cursor:pointer; transition:all .2s; }
.product-card:hover{ border-color:#ff6b82; }
.product-img{ width:100%; height:200px; object-fit:contain; background:#0000; padding:5px; display:block; margin:0 auto; }
.product-info{ padding:12px; }
.product-info h3{ font-size:16px; margin-bottom:4px; }
.product-info .desc{ font-size:14px; color:#aaa; }
.product-info .price{ margin-top:8px; font-size:14px; }
.product-info .price span{ color:#00bfff; font-weight:700; }

.modal{ position:fixed; inset:0; background:rgba(0,0,0,.55); display:flex; align-items:center; justify-content:center; z-index:1000; }
.modal-panel{ width:min(860px, 92%); max-width:96vw; max-height:90vh; overflow:auto; background:#222; border-radius:16px; box-shadow:0 10px 40px rgba(0,0,0,.5); position:relative; padding:18px; }
.modal-panel.wide{ width:min(980px,96%); max-width:96vw; max-height:90vh; overflow:auto; }
.modal-close{ position:absolute; top:10px; right:14px; width:36px; height:36px; border:none; border-radius:8px; background:#333; color:#fff; font-size:22px; cursor:pointer; }
.btn{ border:none; border-radius:12px; padding:10px 16px; cursor:pointer; font-weight:700; }
.btn.primary{ background:#07c1d4; color:#001018; }
.btn.ghost{ background:#333; color:#fff; }
.detail-body{ display:grid; grid-template-columns:1fr 1fr; gap:18px; }
@media (max-width:780px){ .detail-body{ grid-template-columns:1fr; } }
.detail-img{ width:100%; height:320px; object-fit:contain; background:#2a2a2a; border-radius:12px; }
.detail-info{ display:flex; flex-direction:column; gap:12px; }
.detail-title{ font-size:22px; margin:0; }
.detail-desc{ color:#cfcfcf; }
.detail-price-line{ display:flex; align-items:center; gap:12px; margin-top:4px; }
.detail-price{ color:#00bfff; font-size:20px; }
.qty-line{ display:flex; align-items:center; gap:8px; }
.qty-btn{ width:36px; height:36px; border:none; border-radius:8px; background:#333; color:#fff; font-size:18px; cursor:pointer; }
.qty-input{ width:64px; height:36px; border:1px solid #444; border-radius:8px; background:#1a1a1a; color:#fff; text-align:center; }

.cart-table{ width:100%; overflow-x:auto; }
.thead,.trow{ display:grid; grid-template-columns:1fr 120px 140px 120px 60px; align-items:center; gap:8px; min-width:640px; }
.thead{ font-weight:800; margin:10px 0; }
.trow{ padding:10px 0; border-top:1px solid #333; }
.c-price,.c-sub{ font-weight:700; }
.c-qty{ display:flex; align-items:center; gap:8px; }
.icon-btn{ border:none; background:#333; color:#fff; border-radius:8px; padding:6px 8px; cursor:pointer; }
.tfoot{ display:flex; justify-content:flex-end; align-items:center; gap:12px; font-size:18px; font-weight:800; padding:12px 0; border-top:1px solid #333; }
.tfoot-val{ color:#00bfff; }
.cart-actions{ display:flex; justify-content:flex-end; gap:10px; margin-top:8px; }

.product-declare, .payment, .policy{
  margin-top:20px; padding:16px; background:#1a1a1a; border-radius:10px; font-size:14px; line-height:1.6;
}

.agree-list{ display:flex; flex-direction:column; gap:16px; }
.agree-item{
  display:flex; align-items:flex-start; gap:14px; padding:16px 18px; background:#1a1a1a; border:1px solid #2a2a2a; border-radius:14px;
  cursor:pointer; user-select:none; transition:border-color .15s,box-shadow .15s,background .15s;
}
.agree-item:hover,.agree-item:focus-within{ border-color:#3a8ea3; }
.agree-item.checked{ border-color:#00bcd4; box-shadow:0 0 0 1px #00bcd4 inset; }
.agree-item input[type="checkbox"]{ appearance:none; -webkit-appearance:none; position:absolute; opacity:0; pointer-events:none; }
.agree-item .box{ flex:0 0 22px; width:22px; height:22px; border-radius:6px; border:2px solid #555; background:#111; margin-top:2px; position:relative; transition:all .15s; }
.agree-item input[type="checkbox"]:checked + .box{ border-color:#07c1d4; background:#07c1d4; }
.agree-item input[type="checkbox"]:checked + .box::after{
  content:""; position:absolute; left:6px; top:2px; width:6px; height:12px; border:3px solid #001018; border-left:none; border-top:none; transform:rotate(45deg);
}
.agree-item .text{ font-size:clamp(15px,2vw,20px); line-height:1.55; color:#eaeaea; }

.uploader{ position:relative; margin-top:10px; background:#1a1a1a; border:2px dashed #3a3a3a; border-radius:14px; padding:28px 16px; text-align:center; cursor:pointer; transition:border-color .15s,background .15s; }
.uploader:hover{ border-color:#4a4a4a; }
.uploader.is-dragover{ border-color:#00bcd4; background:#181e21; }
.uploader-inner{ pointer-events:none; }
.uploader-icon{ font-size:28px; opacity:.9; }
.uploader-text{ margin-top:8px; font-size:18px; color:#eaeaea; }
.uploader-sub{ margin-top:4px; font-size:13px; color:#a9a9a9; }
.uploader-input{ position:absolute; inset:0; opacity:0; pointer-events:none; }
.uploader-list{ margin-top:12px; display:grid; grid-template-columns:1fr; gap:10px; }
.uploader-item{ display:flex; align-items:center; gap:12px; background:#151515; border:1px solid #2a2a2a; border-radius:12px; padding:10px; }
.thumb{ width:56px; height:56px; border-radius:10px; overflow:hidden; background:#2a2a2a; display:flex; align-items:center; justify-content:center; color:#ddd; font-weight:700; }
.thumb img{ width:100%; height:100%; object-fit:cover; }
.meta{ flex:1; min-width:0; }
.name{ white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
.size{ font-size:12px; color:#9c9c9c; margin-top:2px; }
.remove{ border:none; background:#333; color:#fff; border-radius:8px; padding:6px 10px; cursor:pointer; }
.uploader-error{ color:#ff6b82; margin-top:8px; }

.actions{ text-align:center; margin-top:28px; }
.btn-submit{
  appearance:none; border:none; background:#07c1d4; color:#fff; font-weight:800; font-size:18px;
  padding:14px 32px; border-radius:14px; cursor:pointer; box-shadow:0 6px 16px rgba(7,193,212,.25);
  transition:transform .12s, box-shadow .12s, filter .12s;
}
.btn-submit:hover{ transform:translateY(-1px); box-shadow:0 10px 22px rgba(7,193,212,.35); filter:brightness(1.02); }
.btn-submit:active{ transform:translateY(0); box-shadow:0 6px 16px rgba(7,193,212,.25); }
.btn-submit:focus-visible{ outline:none; box-shadow:0 0 0 3px rgba(7,193,212,.6); }
.btn-submit:disabled{ opacity:.55; cursor:not-allowed; filter:grayscale(10%); }
</style>
