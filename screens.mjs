// screens.mjs — router + AppShell + 6 màn hình (sinh vào index.html qua build.mjs)
/* ================= FEEDBACK ================= */
let _ac=null;
function beep(f=880,d=90,t="sine",g=0.06){try{_ac=_ac||new (window.AudioContext||window.webkitAudioContext)();const c=_ac,o=c.createOscillator(),ga=c.createGain();o.type=t;o.frequency.value=f;ga.gain.setValueAtTime(g,c.currentTime);ga.gain.exponentialRampToValueAtTime(0.0001,c.currentTime+d/1000);o.connect(ga).connect(c.destination);o.start();o.stop(c.currentTime+d/1000);}catch(e){}}
function buzz(p=25){try{navigator.vibrate&&navigator.vibrate(p);}catch(e){}}
function esc(s){return String(s).replace(/[&<>"]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));}
function shuffle(a){a=a.slice();for(let i=a.length-1;i>0;i--){const j=Math.floor(Math.random()*(i+1));[a[i],a[j]]=[a[j],a[i]];}return a;}
function toneless(s){return (s||"").normalize("NFD").replace(/[̀-ͯ]/g,"").toLowerCase();}

/* ================= INDEX ================= */
let DICT_BY_CHAR={},CHARS=[],CHAR_BY_GLYPH={},COMPOUNDS=[],SEM_INDEX=new Map(),PHON_INDEX=new Map();
function rebuildIndex(){
  DICT_BY_CHAR={};DICT.forEach(e=>DICT_BY_CHAR[e.character]=e);
  CHARS=DICT.map(analyzeChar);CHAR_BY_GLYPH={};CHARS.forEach(c=>CHAR_BY_GLYPH[c.glyph]=c);
  COMPOUNDS=CHARS.filter(c=>c.kind==="pictophonetic");
  SEM_INDEX=new Map();PHON_INDEX=new Map();
  for(const c of CHARS){
    if(!c.parts)continue;
    for(const p of c.parts){
      if(p.role==="semantic"){const b=p.res.base;if(!SEM_INDEX.has(b))SEM_INDEX.set(b,[]);SEM_INDEX.get(b).push(c.glyph);}
      if(p.role==="phonetic"){const g=p.glyph;if(!PHON_INDEX.has(g))PHON_INDEX.set(g,[]);PHON_INDEX.get(g).push(c.glyph);}
    }
  }
  const el=document.getElementById("dictCount");if(el)el.textContent=DICT.length+" chữ";
}
function partKey(p){return p.role==="semantic"?p.res.base:baseOf(p.glyph);}
function compInfo(base){const r=RAD_RADICALS[base];return {base,emoji:r?r[0]:null,pinyin:r?r[1]:(PINYIN_FB[base]||""),vi:r?r[2]:""};}
function searchByComponents(bases){return COMPOUNDS.filter(c=>bases.every(b=>c.parts.some(p=>partKey(p)===b)));}

/* ================= HELPER HIỂN THỊ ================= */
const TYPE_BADGE={"hình thanh":["🧩","Hình thanh"],"tượng hình":["🖼","Tượng hình"],"chỉ sự":["💡","Chỉ sự"],"hội ý":["💡","Hội ý"]};
function typeBadge(t){const b=TYPE_BADGE[t]||["❓","Chưa phân loại"];return `<span class="type-badge">${b[0]} ${b[1]}</span>`;}
function formulaChip(p){
  if(p.role==="semantic"){
    const r=p.res;
    if(r.emoji||RAD_ICON[r.base]) return `<span class="fchip nghia"><span class="fe">${semIconHTML(r.base,34)}</span><span class="fvi">${esc(r.vi||"")}</span><small>NGHĨA</small></span>`;
    return `<span class="fchip plain"><span class="fc font-cjk">${esc(p.glyph)}</span><small>NGHĨA</small></span>`;
  }
  return `<span class="fchip am"><span class="fc font-cjk">${esc(p.glyph)}</span>${p.pinyin?`<span class="fpy">${p.pinyin}</span>`:""}<small>ÂM</small>${p.fade?`<span class="ffade">${p.fade}</span>`:""}</span>`;
}
function renderFormula(ch){
  const eq=`<span class="feq">=</span><span class="fbig-wrap"><span class="fbig font-cjk">${ch.glyph}</span><span class="fpy">${ch.pinyin}</span></span>`;
  if(ch.pictoEmoji) return `<div class="formula"><span class="fchip picto"><span class="fe">${ch.pictoEmoji}</span><small>${ch.type}</small></span>${eq}</div>`;
  if(ch.parts&&ch.parts.length){return `<div class="formula">${ch.parts.map(formulaChip).join('<span class="feq">+</span>')}${eq}</div>`;}
  return `<div class="formula"><span class="fchip plain"><span class="fc font-cjk">${ch.glyph}</span><small>${ch.type}</small></span>${eq}</div>`;
}
function Tianzige(parts,dimComp){
  const cells=parts.map(p=>{const color=p.role==="phonetic"?"var(--am)":"var(--nghia)";const dim=(dimComp&&p.glyph!==dimComp)?"dim":"";return `<div class="tz-cell ${p.pos} ${dim}"><span class="tz-glyph" style="color:${color}">${esc(p.glyph)}</span></div>`;}).join("");
  return `<div class="tianzige lg"><div class="tz-hline"></div><div class="tz-vline"></div>${cells}</div>`;
}
/* Hiển thị thành phần NGHĨA theo chuỗi ưu tiên: icon3d (PNG) → icon SVG → emoji → chữ.
   Tầng chọn bởi pickIconLayer (resolver.mjs — thuần, test được).
   "seal" = placeholder chữ Hán trong khung tròn xanh.
   TODO: thay placeholder seal bằng SVG chữ TIỂU TRIỆN tải từ GlyphWiki (glyphwiki.org). */
let ICON_MODE="svg";      // "3d" | "svg" — probe icons3d/1f4a7_水.png quyết định mặc định
let ICON3D_OK=false;
function semIconSvgLayer(base,px){
  const ic=RAD_ICON[base];
  if(ic==="seal") return `<span class="seal-ph" style="width:${px+8}px;height:${px+8}px;font-size:${Math.round(px*0.58)}px">${esc(base)}</span>`;
  if(ic&&ICONS[ic]) return `<span class="svgicon" style="font-size:${px}px">${ICONS[ic]}</span>`;
  const emo=emojiForHan(base);
  if(emo) return `<span style="font-size:${px}px;line-height:1">${emo}</span>`;
  return `<span class="seal-ph" style="width:${px+8}px;height:${px+8}px;font-size:${Math.round(px*0.58)}px;border-color:var(--ink-soft);color:var(--ink-soft);background:var(--sand)">${esc(base)}</span>`;
}
function semIconHTML(base,px){
  if(pickIconLayer(base,ICON_MODE==="3d")==="icon3d"){
    const d=Math.max(56,px+22);
    // ảnh 3D không nhuộm màu được -> khung tròn nền xanh nhạt + viền xanh; lỗi tải -> rơi về tầng SVG
    return `<span class="sem3d"><span class="icon3d-frame" style="width:${d}px;height:${d}px"><img src="icons3d/${RAD_ICON3D[base]}.png" alt="${esc(base)}" onerror="var s=this.closest('.sem3d');this.remove();s.firstElementChild.style.display='none';s.lastElementChild.style.display=''"></span><span class="fb" style="display:none">${semIconSvgLayer(base,px)}</span></span>`;
  }
  return semIconSvgLayer(base,px);
}
/* Badge Cilin 同义词词林: [G · Tâm lý] hoặc [F · Động tác | B · Sự vật] */
function cilinBadge(base){
  const s=SHUOWEN[base];if(!s||!s[6])return "";
  const main=s[6],phu=s[7],mien=s[8];
  const seg=(c)=>`${c} · ${CILIN_NAMES[c]||c}`;
  const label=phu?`${seg(main)}<span class="sep"> | </span>${seg(phu)}`:seg(main);
  return `<span class="cilin-badge" style="background:${CILIN_COLORS[main]||"#999"}" title="${esc(mien||"")}">${label}</span>`;
}
/* Khối Thuyết Văn Giải Tự (nghia_den + nghia_phai_sinh + badge Cilin + mở rộng nguyên văn) */
function shuowenBlock(base){
  const s=SHUOWEN[base];
  if(!s) return `<div class="sub">Thành phần tạo NGHĨA, hiển thị bằng emoji.</div>`;
  const [den,phai,nguyen,dich,vd,kc]=s;
  const star=kc?` <span class="kc" title="nguyên văn đang chờ đối chiếu với swjz.xml">(*)</span>`:"";
  const detail=nguyen?`<details class="shuowen"><summary>說文解字 · Xem Thuyết văn${star}</summary>
    <div class="body"><div class="sw-lbl">Nguyên văn 說文解字</div><div class="sw-han">${esc(nguyen)}</div>
    <div class="sw-dich">${esc(dich)}</div>${vd?`<div class="sw-vd">Ví dụ: ${esc(vd)}</div>`:""}${kc?`<div class="kc" style="margin-top:8px">(*) Nguyên văn soạn từ tri thức, đang chờ đối chiếu swjz.xml/ctext.org.</div>`:""}</div></details>`:"";
  return `<div class="swblock"><div class="den"><b>Nghĩa đen:</b> ${esc(den)}${cilinBadge(base)}</div><div class="phai"><b>Vai trò khi ghép:</b> ${esc(phai)}</div>${detail}</div>`;
}
function PartCard(p,idx){
  if(p.role==="semantic"){
    const r=p.res;
    if(r.emoji){
      const note=r.isVariant?`<div class="vnote">${esc(p.glyph)} là dạng biến thể (${p.pos==="left"?"đứng bên trái":p.pos}) của <b class="font-cjk">${esc(r.base)}</b> ${r.emoji}</div>`:"";
      return `<div class="part-card nghia" data-g="${esc(p.glyph)}"><div class="row"><div class="role-visual nghia">${semIconHTML(r.base,32)}</div>
        <div class="meta"><div class="head">Bộ <b class="font-cjk">${esc(r.base)}</b> · <b>${r.pinyin||""}</b> — ${esc(r.vi||"")}</div>${shuowenBlock(r.base)}</div></div>
        <div class="tags"><span class="tag nghia">tạo NGHĨA</span><span class="tag neutral">${esc(p.pos)}</span></div>${note}</div>`;
    }
    return `<div class="part-card plain" data-g="${esc(p.glyph)}"><div class="row"><div class="role-visual plain"><span class="rv-char font-cjk">${esc(p.glyph)}</span></div>
      <div class="meta"><div class="head">Thành phần <b class="font-cjk">${esc(p.glyph)}</b>${p.res&&p.res.pinyin?` · <b>${p.res.pinyin}</b>`:""}</div><div class="sub">Chưa có emoji — hiển thị nguyên chữ trong khung xám.</div></div></div>
      <div class="tags"><span class="tag neutral">tạo NGHĨA</span><span class="tag neutral">${esc(p.pos)}</span></div></div>`;
  }
  return `<div class="part-card am" data-g="${esc(p.glyph)}"><div class="row"><div class="role-visual am"><span class="rv-char font-cjk">${esc(p.glyph)}</span>${p.fade?`<span class="rv-fade">${p.fade}</span>`:""}</div>
    <div class="meta"><div class="head">Chữ <b class="font-cjk">${esc(p.glyph)}</b>${p.pinyin?` · <b>${p.pinyin}</b>`:""} — gợi ÂM đọc</div><div class="sub">Thành phần tạo ÂM: giữ nguyên chữ Hán + pinyin${p.fade?`, có emoji riêng ${p.fade} (mờ)`:""}.</div></div></div>
    <div class="tags"><span class="tag am">tạo ÂM</span><span class="tag neutral">${esc(p.pos)}</span></div></div>`;
}

/* ---------- BỘ THỦ (duyệt 84 bộ · lọc Cilin · lọc HSK1) ---------- */
let radicals=null;
function charsOfRadical(base){
  return CHARS.filter(c=>
    (c.parts&&c.parts.some(p=>(p.role==="semantic"?p.res.base:baseOf(p.glyph))===base)) ||
    baseOf(c.radical)===base || baseOf(c.glyph)===base ||
    (c.radical==="阝"&&(base==="阜"||base==="邑")) );
}
function renderRadicals(){
  if(!radicals) radicals={cat:"all",sel:null,hskOnly:true};
  const R=radicals;
  const cats=Object.keys(CILIN_NAMES);
  const filterPills=`<div class="cfilter">
    <button class="pill ${R.cat==="all"?"active":""}" data-c="all">Tất cả (84)</button>
    ${cats.map(c=>{const n=Object.keys(RAD_RADICALS).filter(b=>SHUOWEN[b]&&(SHUOWEN[b][6]===c||SHUOWEN[b][7]===c)).length;return n?`<button class="pill ${R.cat===c?"active":""}" data-c="${c}"><span class="dot" style="background:${CILIN_COLORS[c]}"></span>${c} · ${CILIN_NAMES[c]} (${n})</button>`:"";}).join("")}
  </div>`;
  const bases=Object.keys(RAD_RADICALS).filter(b=>R.cat==="all"||(SHUOWEN[b]&&(SHUOWEN[b][6]===R.cat||SHUOWEN[b][7]===R.cat)));
  const grid=`<div class="radgrid">${bases.map(b=>{const r=RAD_RADICALS[b];const cl=SHUOWEN[b]?SHUOWEN[b][6]:"";
    return `<div class="radcell ${R.sel===b?"active":""}" data-b="${esc(b)}" title="${esc(SHUOWEN[b]?SHUOWEN[b][8]||"":"")}">
      ${cl?`<span class="cdot cilin-mini" style="background:${CILIN_COLORS[cl]}">${cl}</span>`:""}
      <div class="re">${r[0]}</div><div class="rg">${esc(b)}</div><div class="rv">${esc(r[2])}</div></div>`;}).join("")}</div>`;
  let detail="";
  if(R.sel&&RAD_RADICALS[R.sel]){
    const r=RAD_RADICALS[R.sel];
    let list=charsOfRadical(R.sel);
    const total=list.length;
    if(R.hskOnly) list=list.filter(c=>HSK1.has(c.glyph));
    detail=`<div style="margin-top:22px">
      <div class="char-head"><span style="font-size:34px">${r[0]}</span><span class="big font-cjk" style="font-size:28px;font-weight:700">${esc(R.sel)}</span><span class="info">${r[1]} — ${esc(r[2])}</span></div>
      ${shuowenBlock(R.sel)}
      <div class="util-row" style="margin-top:14px">
        <span class="muted" style="font-size:13px">Chữ chứa bộ này trong từ điển: <b style="color:var(--ink)">${list.length}</b>${R.hskOnly?` / ${total} (đang lọc HSK1)`:` / ${total}`}</span>
        <label class="hsk-toggle"><input type="checkbox" id="hskToggle" ${R.hskOnly?"checked":""}> Chỉ HSK1</label>
      </div>
      ${list.length?`<div class="result-grid" style="margin-top:12px">${list.map(ch=>`<div class="result-card" style="cursor:pointer" data-open="${ch.glyph}"><div class="rc-glyph font-cjk">${ch.glyph}</div><div class="rc-py">${ch.pinyin}</div><div class="rc-mean">${esc(ch.def)}</div></div>`).join("")}</div>`
        :`<p class="muted" style="font-size:14px;margin-top:12px">Không có chữ nào${R.hskOnly?" thuộc HSK1":""} chứa bộ này trong dữ liệu hiện tại${R.hskOnly?" — thử tắt lọc HSK1":""}. Nạp dictionary.txt đầy đủ để có nhiều chữ hơn.</p>`}
    </div>`;
  }
  return {html:`<div>
    <p class="muted" style="font-size:14px;margin:0 0 14px">84 bộ thủ nhóm theo đại loại <b>同义词词林 Cilin</b>. Bấm một bộ để xem Thuyết văn và lọc các chữ chứa bộ đó.</p>
    ${filterPills}${grid}${detail}
  </div>`,wire(){
    document.querySelectorAll(".cfilter .pill").forEach(b=>b.onclick=()=>{R.cat=b.dataset.c;beep(700,50,"sine",0.04);mountMode();});
    document.querySelectorAll(".radcell").forEach(el=>el.onclick=()=>{R.sel=(R.sel===el.dataset.b?null:el.dataset.b);beep(760,60,"sine",0.04);mountMode();if(R.sel){const d=document.querySelector(".char-head");if(d)d.scrollIntoView({behavior:"smooth",block:"center"});}});
    const ht=document.getElementById("hskToggle");if(ht)ht.onchange=()=>{R.hskOnly=ht.checked;mountMode();};
    document.querySelectorAll("[data-open]").forEach(el=>el.onclick=()=>{beep(880,70,"triangle");location.hash="#/analysis/"+encodeURIComponent(el.dataset.open);});
  }};
}

/* ---------- HỌC CHỮ ---------- */
let learn=null;
function learnInit(idx){
  const ch=COMPOUNDS[idx%COMPOUNDS.length];
  const correct=[...new Set(ch.parts.map(partKey))];
  const pool=Object.keys(RAD_RADICALS).filter(b=>!correct.includes(b));
  learn={idx,chips:shuffle([...correct,...shuffle(pool).slice(0,3)]),selected:new Set(),status:"idle",bad:new Set()};
}
function renderLearn(){
  if(!COMPOUNDS.length) return {html:`<p class="muted">Cần chữ hình thanh trong từ điển.</p>`,wire(){}};
  if(!learn) learnInit(0);
  const ch=COMPOUNDS[learn.idx%COMPOUNDS.length];
  const correct=new Set(ch.parts.map(partKey));
  if(learn.status==="done"){
    return {html:`<div class="split"><div>${Tianzige(ch.parts)}<p class="center muted" style="margin-top:14px;font-size:14px"><span class="font-cjk" style="font-size:20px;color:var(--ink);font-weight:600">${ch.glyph}</span> · ${ch.pinyin} · ${esc(ch.def)}</p></div>
      <div><div class="char-head"><span class="info">Loại chữ:</span>${typeBadge(ch.type)}</div>${renderFormula(ch)}
        <div style="display:flex;flex-direction:column;gap:12px">${ch.parts.map((p,i)=>PartCard(p,i)).join("")}</div>
        <div class="memory"><div class="k">Ghi nhớ</div><p>${esc(ch.hint||ch.def)}</p></div>
        <button class="btn-primary" id="learnNext" style="margin-top:18px">Chữ tiếp theo →</button></div></div>`,wire(){document.getElementById("learnNext").onclick=()=>{learnInit(learn.idx+1);mountMode();beep(1046,90,"triangle");};}};
  }
  return {html:`<div>
    <div class="center" style="margin-bottom:24px"><div style="font-size:11px;text-transform:uppercase;letter-spacing:.2em;font-weight:700;color:var(--clay)">Nghĩa của chữ</div>
      <div style="font-size:30px;font-weight:700;margin-top:8px">${esc(ch.def)}</div>
      <div class="muted" style="font-size:14px;margin-top:4px">âm đọc: ${ch.pinyin} · gồm ${correct.size} thành phần</div></div>
    <p class="center" style="font-size:15px;margin-bottom:18px;font-weight:500">Chọn <b>tất cả</b> thành phần tạo nên chữ này:</p>
    <div class="chip-grid" style="max-width:560px;margin:0 auto">${learn.chips.map(b=>{const ci=compInfo(b),on=learn.selected.has(b),bad=learn.bad.has(b);const st=bad?"is-wrong":on?"is-selected":"";return `<button class="radical-chip ${st}" data-b="${esc(b)}"><div class="emoji">${ci.emoji||"🔸"}</div><div class="glyph font-cjk">${esc(ci.base)}</div><div class="cap">${esc(ci.vi||"")}</div></button>`;}).join("")}</div>
    <div class="center" style="margin-top:24px"><button class="btn-primary" id="learnCheck">Kiểm tra</button>${learn.status==="wrong"?`<p style="color:var(--danger);margin-top:16px;font-size:14px;font-weight:500">Chưa đúng — bỏ mảnh viền đỏ và chọn lại nhé.</p>`:""}</div>
  </div>`,wire(){
    document.querySelectorAll(".radical-chip").forEach(b=>b.onclick=()=>{const id=b.dataset.b;learn.selected.has(id)?learn.selected.delete(id):learn.selected.add(id);if(learn.bad.has(id))learn.bad.delete(id);if(learn.status!=="idle")learn.status="idle";beep(660,50,"sine",0.04);mountMode();});
    document.getElementById("learnCheck").onclick=()=>{if(!learn.selected.size)return;const extra=[...learn.selected].filter(id=>!correct.has(id));const missing=[...correct].filter(id=>!learn.selected.has(id));if(!extra.length&&!missing.length){learn.status="done";beep(1175,110,"triangle");setTimeout(()=>beep(1568,160,"triangle"),110);buzz([40,60,90]);}else{learn.status="wrong";learn.bad=new Set(extra);beep(220,140,"square",0.05);buzz([15,30,15]);}mountMode();};
  }};
}

/* ---------- GHÉP CHỮ ---------- */
let assemble=null;
function asmTargets(){const t=["清","情","妈"].filter(g=>CHAR_BY_GLYPH[g]&&CHAR_BY_GLYPH[g].kind==="pictophonetic");return t.length?t:COMPOUNDS.slice(0,3).map(c=>c.glyph);}
function assembleInit(t){const T=asmTargets();const target=t||T[0];const ch=CHAR_BY_GLYPH[target];const correct=ch.parts.map(p=>p.glyph);const pool=[...new Set(COMPOUNDS.flatMap(c=>c.parts.map(p=>p.glyph)).filter(g=>!correct.includes(g)))];assemble={target,tray:shuffle([...correct,...shuffle(pool).slice(0,3)]),placed:{},picked:null,over:null,shake:null,done:false,attempts:0};}
function posStyle(pos){const i="8%";if(pos==="left")return `left:${i};top:${i};bottom:${i};width:calc(50% - ${i})`;if(pos==="right")return `right:${i};top:${i};bottom:${i};width:calc(50% - ${i})`;if(pos==="top")return `left:${i};right:${i};top:${i};height:calc(50% - ${i})`;if(pos==="bottom")return `left:${i};right:${i};bottom:${i};height:calc(50% - ${i})`;return `inset:${i}`;}
function pieceInfo(g){const c=COMPOUNDS.flatMap(x=>x.parts).find(p=>p.glyph===g);if(c&&c.role==="semantic"&&c.res.emoji)return {emoji:c.res.emoji,label:c.res.base};if(c&&c.role==="phonetic")return {emoji:emojiForHan(g),label:c.pinyin||""};return {emoji:emojiForHan(g),label:""};}
function renderAssemble(){
  if(!COMPOUNDS.length) return {html:`<p class="muted">Cần chữ hình thanh.</p>`,wire(){}};
  if(!assemble) assembleInit();
  const A=assemble,ch=CHAR_BY_GLYPH[A.target],T=asmTargets();
  const slots=ch.parts.map((p,i)=>{const placed=!!A.placed[i];const glyph=placed?A.placed[i]:"";const color=p.role==="phonetic"?"var(--am)":"var(--nghia)";const cls=`puzzle-slot ${A.over===i?"is-over":""} ${A.shake===i?"is-shake":""} ${placed?"is-locked":""}`;const inner=placed?`<span class="tz-glyph font-cjk" style="color:${color}">${esc(glyph)}</span>`:`<span class="slot-hint">${esc(p.pos)}</span>`;return `<div class="${cls}" style="${posStyle(p.pos)}" data-slot="${i}">${inner}</div>`;}).join("");
  return {html:`<div class="split"><div><div style="transition:transform .5s;${A.done?"transform:scale(1.04)":""}"><div class="puzzle-board"><div class="tz-hline"></div><div class="tz-vline"></div>${slots}${A.done?`<div class="type-badge" style="position:absolute;right:-8px;bottom:-8px;background:var(--semantic);color:#fff;border:none">✓ xong</div>`:""}</div></div>
    <p class="center muted" style="margin-top:14px;font-size:14px">Kéo / chạm mảnh vào ô đúng để tạo <b class="font-cjk" style="font-size:18px;color:var(--ink)">${A.target}</b> (${ch.pinyin} — ${esc(ch.def)})</p></div>
    <div><div style="display:flex;flex-wrap:wrap;gap:8px;margin-bottom:18px">${T.map(g=>{const c=CHAR_BY_GLYPH[g];return `<button class="pill ${g===A.target?"active":""}" data-t="${g}">Mục tiêu: <span class="cjk font-cjk">${g}</span> ${c.pinyin}</button>`;}).join("")}</div>
      <div class="step"><span class="num">1</span><h3>Kho mảnh ghép</h3></div>
      <p class="muted" style="font-size:14px;margin-bottom:12px">Kéo mảnh vào khung, hoặc chạm 1 mảnh rồi chạm ô đích. Ghép sai không bị phạt.</p>
      <div class="tray">${A.tray.map(g=>{const info=pieceInfo(g),used=Object.values(A.placed).includes(g),sel=A.picked===g;return `<div class="puzzle-piece ${used?"is-used":""} ${sel?"is-selected":""}" data-piece="${esc(g)}" ${used?"":'draggable="true"'} title="${esc(info.label)}"><div class="em">${info.emoji||"🔸"}</div><div class="g" style="color:${info.emoji?"var(--nghia)":"var(--am)"}">${esc(g)}</div><div class="c">${esc(info.label)}</div></div>`;}).join("")}</div>
      <div class="util-row"><button class="btn-ghost" id="asmReset">Làm lại</button><span class="muted" style="font-size:12px">Đã ghép: <b style="color:var(--ink)">${Object.keys(A.placed).length}/${ch.parts.length}</b></span></div>
      ${A.done?`<div class="done-box"><div class="k">Hoàn thành!</div><p style="font-size:15px;margin:0">✓ Bạn đã ghép ra <span class="font-cjk" style="font-size:24px;font-weight:600">${A.target}</span> — ${ch.pinyin} · ${esc(ch.def)}.</p><div style="margin-top:12px;display:flex;gap:12px"><button class="btn-primary" id="asmNext">Chữ tiếp theo →</button><button class="btn-ghost" id="asmAgain">Ghép lại</button></div></div>`:""}
    </div></div>`,wire(){
    function tryPlace(slot,g){if(A.placed[slot])return;if(g===ch.parts[slot].glyph){A.placed[slot]=g;A.picked=null;beep(880,90,"triangle");buzz(30);if(Object.keys(A.placed).length===ch.parts.length)setTimeout(()=>{A.done=true;beep(1175,110,"triangle");setTimeout(()=>beep(1568,160,"triangle"),110);buzz([40,60,90]);mountMode();},220);mountMode();}else{A.attempts++;A.shake=slot;A.picked=null;beep(220,140,"square",0.05);buzz([15,30,15]);mountMode();setTimeout(()=>{A.shake=null;mountMode();},450);}}
    document.querySelectorAll(".puzzle-piece").forEach(el=>{const g=el.dataset.piece;el.ondragstart=e=>{e.dataTransfer.setData("text/plain",g);e.dataTransfer.effectAllowed="move";A.picked=g;};el.onclick=()=>{if(el.classList.contains("is-used"))return;A.picked=(A.picked===g?null:g);mountMode();};});
    document.querySelectorAll(".puzzle-slot").forEach(el=>{const slot=+el.dataset.slot;el.ondragover=e=>{if(!A.placed[slot]){e.preventDefault();el.classList.add("is-over");A.over=slot;}};el.ondragleave=()=>{if(A.over===slot){A.over=null;el.classList.remove("is-over");}};el.ondrop=e=>{e.preventDefault();A.over=null;const id=e.dataTransfer.getData("text/plain");if(id)tryPlace(slot,id);};el.onclick=()=>{if(A.picked&&!A.placed[slot])tryPlace(slot,A.picked);};});
    document.getElementById("asmReset").onclick=()=>{assembleInit(A.target);mountMode();};
    document.querySelectorAll(".pill[data-t]").forEach(b=>b.onclick=()=>{assembleInit(b.dataset.t);mountMode();});
    const nx=document.getElementById("asmNext");if(nx)nx.onclick=()=>{const i=T.indexOf(A.target);assembleInit(T[(i+1)%T.length]);mountMode();};
    const ag=document.getElementById("asmAgain");if(ag)ag.onclick=()=>{assembleInit(A.target);mountMode();};
  }};
}

/* ---------- SÁNG TẠO ---------- */
const PALETTE=["忄","氵","扌","灬","女","青","可","马","日","月","王"];
let create=null;
function renderCreate(){
  if(!create) create={picked:[],results:null};
  const C=create;
  return {html:`<div>
    <p class="muted" style="font-size:14px;margin:0 0 16px">Chọn ≥ 2 mảnh (biến thể tự quy về gốc: 忄→心, 氵→水…) → tìm chữ chứa đủ các mảnh đó.</p>
    <div class="chip-grid" style="justify-content:flex-start;gap:24px 14px">${PALETTE.map(g=>{const active=C.picked.includes(g),b=resolveComponent(g,"left",{}).base,emo=emojiForHan(g);return `<div style="position:relative"><button class="radical-chip ${active?"is-selected":""}" data-g="${esc(g)}" style="width:70px;padding:8px"><div class="emoji" style="font-size:20px">${emo||"🔸"}</div><div class="glyph font-cjk" style="font-size:22px;margin-top:4px">${esc(g)}</div></button><small style="position:absolute;left:0;right:0;bottom:-19px;text-align:center;font-size:10px;font-weight:600;color:var(--ink-soft)">→ ${esc(b)}</small></div>`;}).join("")}</div>
    <div class="muted" style="margin-top:42px;min-height:2.5rem;font-size:14px">${C.picked.length?`Đã chọn: ${C.picked.map(g=>`<span style="margin-right:12px"><b class="font-cjk" style="color:var(--ink)">${esc(g)}</b> <span style="color:var(--clay)">→</span> ${esc(resolveComponent(g,"left",{}).base)}</span>`).join("")}`:"Chưa chọn mảnh nào."}</div>
    <div style="display:flex;gap:12px;margin-top:12px"><button class="btn-primary" id="crRun">Tìm chữ</button><button class="btn-ghost" id="crClear">Xoá chọn</button></div>
    ${C.results!==null?`<div style="margin-top:24px">${C.results.length===0?`<p class="muted" style="font-size:14px">${C.picked.length<2?"Hãy chọn ít nhất 2 mảnh.":"Không có chữ nào (trong dữ liệu hiện tại) chứa đủ các mảnh này."}</p>`:`<div class="result-grid">${C.results.map(ch=>`<div class="result-card"><div class="rc-glyph font-cjk">${ch.glyph}</div><div class="rc-py">${ch.pinyin}</div><div class="rc-mean">${esc(ch.def)}</div><div class="rc-parts">${ch.parts.map((p,i)=>`${i>0?'<span style="color:var(--clay)"> + </span>':""}<span class="g ${p.role==="semantic"?"nghia":"am"} font-cjk">${esc(p.glyph)}</span>`).join("")}</div></div>`).join("")}</div>`}</div>`:""}
  </div>`,wire(){
    document.querySelectorAll(".radical-chip[data-g]").forEach(b=>b.onclick=()=>{const g=b.dataset.g,i=C.picked.indexOf(g);C.picked=i>=0?C.picked.filter((_,k)=>k!==i):[...C.picked,g];C.results=null;beep(660,50,"sine",0.04);mountMode();});
    document.getElementById("crRun").onclick=()=>{if(C.picked.length<2)C.results=[];else{C.results=searchByComponents([...new Set(C.picked.map(g=>resolveComponent(g,"left",{}).base))]);beep(880,90,"triangle");}mountMode();};
    document.getElementById("crClear").onclick=()=>{C.picked=[];C.results=null;mountMode();};
  }};
}

/* ---------- ĐỐ BỘ THỦ (5 dạng câu hỏi) ---------- */
let quiz=null;
const QUIZ_KINDS=[
  {id:"all",label:"🎲 Trộn tất cả"},
  {id:"sem",label:"Bộ của chữ"},
  {id:"type",label:"Loại chữ"},
  {id:"type_rev",label:"Tìm chữ theo loại"},
  {id:"mean",label:"Nghĩa bộ thủ"},
  {id:"mean_rev",label:"Nghĩa → Bộ"},
];
const ALL_TYPES=["tượng hình","chỉ sự","hội ý","hình thanh"];
function radPick(n,excl){return shuffle(Object.keys(RAD_RADICALS).filter(b=>!excl||!excl.has(b))).slice(0,n);}
function radChipBody(b){const c=compInfo(b);return `<div class="emoji" style="font-size:30px">${c.emoji||"🔸"}</div><div class="cap" style="min-height:24px;margin-top:6px">${esc(c.vi||b)}</div>`;}

/* Dạng 1: chữ hình thanh → bộ thủ tạo NGHĨA */
function qSem(){
  const ch=COMPOUNDS[Math.floor(Math.random()*COMPOUNDS.length)];
  const sem=ch.parts.find(p=>p.role==="semantic");const ans=partKey(sem);
  const used=new Set(ch.parts.map(partKey));
  const opts=shuffle([ans,...radPick(3,used)]);
  const ci=compInfo(ans);
  return {kind:"sem",glyph:ch.glyph,
    prompt:`Chữ <b class="font-cjk" style="font-size:18px">${ch.glyph}</b> (${ch.pinyin} — ${esc(ch.def)}) được tạo NGHĨA từ bộ thủ nào?`,
    options:opts.map(b=>({key:b,body:radChipBody(b)})),ans,
    explain:`Bộ <span class="font-cjk" style="color:var(--ink)">${ci.base}</span> ${ci.emoji||""}${sem.res&&sem.res.isVariant?` (viết là <span class="font-cjk" style="color:var(--ink)">${esc(sem.glyph)}</span> khi ghép)`:""} tạo nghĩa cho <span class="font-cjk" style="color:var(--ink)">${ch.glyph}</span>.`};
}
/* Dạng 2: chữ → loại chữ (lục thư) */
function qType(){
  const pool=CHARS.filter(c=>c.type);
  const ch=pool[Math.floor(Math.random()*pool.length)];
  const opts=shuffle(ALL_TYPES.slice());
  return {kind:"type",glyph:ch.glyph,
    prompt:`Chữ <b class="font-cjk" style="font-size:18px">${ch.glyph}</b> (${ch.pinyin} — ${esc(ch.def)}) thuộc loại chữ nào?`,
    options:opts.map(t=>{const b=TYPE_BADGE[t]||["❓",t];return {key:t,body:`<div class="emoji" style="font-size:26px">${b[0]}</div><div class="cap" style="min-height:24px;margin-top:6px">${b[1]}</div>`};}),
    ans:ch.type,
    explain:`<span class="font-cjk" style="color:var(--ink)">${ch.glyph}</span> là chữ <b>${ch.type}</b>${ch.kind==="pictophonetic"?` — ghép thành phần NGHĨA + thành phần ÂM`:ch.type==="tượng hình"?` — vẽ lại hình dáng sự vật`:` — biểu ý bằng ký hiệu / ghép ý`}.`};
}
/* Dạng 3 (đố ngược): loại chữ → tìm chữ */
function qTypeRev(){
  const byType={};CHARS.filter(c=>c.type).forEach(c=>{(byType[c.type]=byType[c.type]||[]).push(c);});
  const types=Object.keys(byType).filter(t=>byType[t].length>0);
  if(types.length<2)return null;
  const target=types[Math.floor(Math.random()*types.length)];
  const correct=byType[target][Math.floor(Math.random()*byType[target].length)];
  const others=shuffle(CHARS.filter(c=>c.type&&c.type!==target)).slice(0,3);
  if(others.length<3)return null;
  const b=TYPE_BADGE[target]||["❓",target];
  const opts=shuffle([correct,...others]);
  return {kind:"type_rev",glyph:null,
    prompt:`Chữ nào dưới đây là chữ <b>${b[0]} ${b[1]}</b>?`,
    options:opts.map(c=>({key:c.glyph,body:`<div class="font-cjk" style="font-size:34px;font-weight:600">${c.glyph}</div><div class="cap" style="min-height:24px;margin-top:4px">${c.pinyin}</div>`})),
    ans:correct.glyph,
    explain:`<span class="font-cjk" style="color:var(--ink)">${correct.glyph}</span> (${correct.pinyin} — ${esc(correct.def)}) là chữ <b>${target}</b>. ${opts.filter(c=>c.glyph!==correct.glyph).map(c=>`<span class="font-cjk">${c.glyph}</span>: ${c.type}`).join(" · ")}.`};
}
/* Dạng 4: bộ thủ → ý nghĩa */
function qMean(){
  const ans=radPick(1)[0];
  const others=radPick(3,new Set([ans]));
  const c=compInfo(ans);const s=SHUOWEN[ans];
  const opts=shuffle([ans,...others]);
  return {kind:"mean",glyph:null,
    glyphHtml:`<div class="quiz-glyph" style="gap:8px;flex-direction:column;display:flex;align-items:center;justify-content:center"><span class="font-cjk" style="font-size:64px;font-weight:600;line-height:1">${esc(ans)}</span><span style="font-size:14px;color:var(--ink-soft)">${c.pinyin||""}</span></div>`,
    prompt:`Bộ <b class="font-cjk" style="font-size:18px">${esc(ans)}</b> có ý nghĩa là gì?`,
    options:opts.map(b=>{const ci=compInfo(b);return {key:b,body:`<div class="cap" style="min-height:40px;display:flex;align-items:center;justify-content:center;font-size:13px;color:var(--ink)">${esc(ci.vi||b)}</div>`};}),
    ans,
    explain:`Bộ <span class="font-cjk" style="color:var(--ink)">${esc(ans)}</span> ${c.emoji||""} nghĩa là <b>${esc(c.vi||"")}</b>.${s?` Nghĩa đen: ${esc(s[0])}. Vai trò khi ghép: ${esc(s[1])}.`:""}`};
}
/* Dạng 5 (đố ngược): ý nghĩa → bộ thủ */
function qMeanRev(){
  const ans=radPick(1)[0];
  const others=radPick(3,new Set([ans]));
  const c=compInfo(ans);const s=SHUOWEN[ans];
  const opts=shuffle([ans,...others]);
  return {kind:"mean_rev",glyph:null,
    prompt:`Ý nghĩa <b>“${esc(c.vi||ans)}”</b>${s&&s[8]?` <span class="muted">(${esc(s[8])})</span>`:""} tương ứng với bộ thủ nào?`,
    options:opts.map(b=>({key:b,body:`<div class="font-cjk" style="font-size:32px;font-weight:600">${esc(b)}</div><div class="cap" style="min-height:20px;margin-top:4px">${compInfo(b).pinyin||""}</div>`})),
    ans,
    explain:`“${esc(c.vi||"")}” = bộ <span class="font-cjk" style="color:var(--ink)">${esc(ans)}</span> ${c.emoji||""} (${c.pinyin||""}).${s?` ${esc(s[0])}.`:""}`};
}
const QUIZ_GEN={sem:qSem,type:qType,type_rev:qTypeRev,mean:qMean,mean_rev:qMeanRev};
function quizAvailable(id){
  if(id==="sem")return COMPOUNDS.length>0;
  if(id==="type")return CHARS.some(c=>c.type);
  if(id==="type_rev"){const t=new Set(CHARS.filter(c=>c.type).map(c=>c.type));return t.size>=2&&CHARS.length>=4;}
  return true;
}
function quizNew(cat){
  let pool=(cat&&cat!=="all")?[cat]:QUIZ_KINDS.slice(1).map(k=>k.id);
  pool=pool.filter(quizAvailable);
  for(const id of shuffle(pool)){const q=QUIZ_GEN[id]();if(q)return q;}
  return qMean(); // luôn khả dụng
}
function renderQuiz(){
  if(!quiz) quiz={cat:"all",q:quizNew("all"),score:{correct:0,total:0},answered:null};
  const Q=quiz,q=Q.q;
  const pills=`<div style="display:flex;flex-wrap:wrap;gap:6px;justify-content:center;margin:14px 0 4px">${QUIZ_KINDS.map(k=>`<button class="pill ${Q.cat===k.id?"active":""}" data-qc="${k.id}" ${k.id!=="all"&&!quizAvailable(k.id)?"disabled style=\"opacity:.4;pointer-events:none\"":""} style="font-size:12px;padding:6px 12px">${k.label}</button>`).join("")}</div>`;
  const glyphBox=q.glyph?`<div class="quiz-glyph">${q.glyph}</div>`:(q.glyphHtml||"");
  return {html:`<div class="center">
    <div class="muted" style="font-size:14px;font-weight:600">Điểm: <b style="color:var(--primary);font-size:16px">${Q.score.correct}</b> / ${Q.score.total}</div>
    ${pills}
    ${glyphBox}
    <p style="margin-top:18px;font-size:15px">${q.prompt}</p>
    <div class="chip-grid" style="max-width:560px;margin:18px auto 0">${q.options.map(o=>{
      const ok=o.key===q.ans,sel=Q.answered===o.key,show=Q.answered!==null;
      const st=show&&ok?"is-correct":show&&sel?"is-wrong":"";
      return `<button class="radical-chip ${st}" data-k="${esc(o.key)}" ${Q.answered?"disabled":""} style="width:118px">${o.body}</button>`;}).join("")}</div>
    ${Q.answered?`<p style="margin-top:20px;font-size:14px;font-weight:500;max-width:500px;margin-left:auto;margin-right:auto;color:${Q.answered===q.ans?"var(--nghia)":"var(--danger)"}">${Q.answered===q.ans?"✓ Đúng!":"✗ Chưa đúng."} ${q.explain}</p><button class="btn-primary" id="quizNext" style="margin-top:20px">Câu tiếp theo</button>`:""}
  </div>`,wire(){
    document.querySelectorAll(".pill[data-qc]").forEach(b=>b.onclick=()=>{Q.cat=b.dataset.qc;Q.q=quizNew(Q.cat);Q.answered=null;beep(700,50,"sine",0.04);mountMode();});
    document.querySelectorAll(".radical-chip[data-k]").forEach(b=>b.onclick=()=>{
      if(Q.answered)return;const k=b.dataset.k,ok=k===q.ans;
      Q.answered=k;Q.score={correct:Q.score.correct+(ok?1:0),total:Q.score.total+1};
      if(ok){beep(1175,110,"triangle");buzz(30);}else{beep(220,140,"square",0.05);buzz([15,30,15]);}
      mountMode();});
    const nx=document.getElementById("quizNext");if(nx)nx.onclick=()=>{Q.q=quizNew(Q.cat);Q.answered=null;mountMode();};
  }};
}

(function(){const im=new Image();im.onload=()=>{ICON3D_OK=true;setIconMode("3d");};im.onerror=()=>{ICON3D_OK=false;};im.src="icons3d/1f4a7_水.png";})();

function runResolverTests(){
  const T=[];const eq=(a,b,name)=>T.push({name,pass:a===b,got:a,exp:b});
  eq(resolveComponent("氵","left",{hint:"water"}).emoji,"💧","江/清 氵→水 💧");
  eq(resolveComponent("忄","left",{hint:"heart"}).emoji,"❤️","情 忄→心 ❤️");
  eq(resolveComponent("灬","bottom",{hint:"fire"}).emoji,"🔥","热/照 灬→火 🔥");
  eq(resolveComponent("阝","left",{}).emoji,"🏔️","阿 阝(trái)→阜 🏔️");
  eq(resolveComponent("阝","right",{}).emoji,"🏘️","都 阝(phải)→邑 🏘️");
  eq(resolveComponent("月","left",{hint:"flesh"}).emoji,"🥩","腿/肝 月(flesh)→肉 🥩");
  eq(resolveComponent("月","right",{hint:"the sun and moon"}).emoji,"🌙","明 月→🌙");
  eq(resolveComponent("王","left",{hint:"jade"}).emoji,"💎","玩/球 王(trái)→玉 💎");
  eq(resolveComponent("彳","left",{}).found,false,"很 彳 fallback (không emoji)");
  const a清=analyzeChar(DICT_BY_CHAR["清"]);eq(a清.parts[0].res.emoji+"+"+a清.parts[1].glyph,"💧+青","清 = 💧 + 青");
  const a木=analyzeChar(DICT_BY_CHAR["木"]);eq(a木.pictoEmoji,"🌳","木 tượng hình 🌳");
  const pass=T.filter(t=>t.pass).length;
  console.log(`[resolver tests] ${pass}/${T.length} pass`);T.filter(t=>!t.pass).forEach(t=>console.warn("FAIL:",t.name,"got",t.got,"exp",t.exp));
  const flag=document.getElementById("testFlag");if(flag)flag.textContent=`resolver ${pass}/${T.length} ✓`;
  return {pass,total:T.length};
}


/* ================= KB HELPERS ================= */
function getEntry(g){return DICT_BY_CHAR[g]||KB_ENTRIES[g]||null;}
function anaOf(g){
  const e=getEntry(g);if(!e)return null;
  const a=CHAR_BY_GLYPH[g]||analyzeChar(e);
  if(a.parts)a.parts.forEach(p=>{if(p.role==="phonetic"&&!p.pinyin)p.pinyin=KB_PINYIN[p.glyph]||null;});
  return a;
}
function hanVietOf(g){const c=CURATED[g];return c?c.hanViet:null;}
const IDS_NAME={"⿰":"Trái – Phải","⿱":"Trên – Dưới","⿲":"Trái · Giữa · Phải","⿳":"Trên · Giữa · Dưới","⿴":"Bao quanh kín","⿵":"Bao trên","⿶":"Bao dưới","⿷":"Bao trái","⿸":"Bao trái-trên","⿹":"Bao phải-trên","⿺":"Bao trái-dưới","⿻":"Chồng lấp"};

/* ================= ROUTER ================= */
let route={name:"home",arg:null,params:{}};
function parseHash(){
  const h=(location.hash||"#/").replace(/^#/,"");
  const [path,qs]=h.split("?");
  const params={};if(qs)qs.split("&").forEach(kv=>{const[i,v]=kv.split("=");params[decodeURIComponent(i)]=decodeURIComponent(v||"");});
  const seg=path.split("/").filter(Boolean);
  if(seg.length===0)return {name:"home",arg:null,params};
  const map={analysis:"analysis",graph:"graph",compound:"compound",radicals:"radicals",practice:"practice"};
  const name=map[seg[0]]||"home";
  return {name,arg:seg[1]?decodeURIComponent(seg[1]):null,params};
}
function nav(h){location.hash=h;}
window.addEventListener("hashchange",()=>{route=parseHash();renderRoute();});

/* ================= APP SHELL ================= */
const NAV_ITEMS=[
  ["home","#/","Ngữ Nghĩa Chính"],["analysis","#/analysis/清","Phân Tích Chữ Hán"],
  ["graph","#/graph?mode=semantic&focus=水","Đồ Thị Quan Hệ"],["compound","#/compound/chicu","Tra Cứu Từ Ghép"],
  ["radicals","#/radicals","Bộ Thủ"],["practice","#/practice","Luyện Tập"]];
function renderShell(){
  document.getElementById("topnav").innerHTML=NAV_ITEMS.map(([id,href,label])=>
    `<a class="navlink ${route.name===id?"active":""}" href="${href}">${label}</a>`).join("");
}
/* Sidebar dùng chung */
let sideQ="";
function renderSidebar(){
  const el=document.getElementById("sidebar");
  const q=sideQ.trim().toLowerCase();
  let sug="";
  if(q){
    const hits=CHARS.filter(c=>c.glyph===sideQ.trim()||c.pinyin.toLowerCase().startsWith(q)||toneless(c.pinyin).startsWith(toneless(q))).slice(0,8);
    sug=hits.length?`<div class="side-sug">${hits.map(c=>`<a href="#/analysis/${encodeURIComponent(c.glyph)}" class="sug-item"><b class="font-cjk">${c.glyph}</b> ${c.pinyin} <span>${esc(c.def)}</span></a>`).join("")}</div>`:"";
  }
  const cats=Object.keys(CILIN_NAMES);
  el.innerHTML=`
    <div class="side-card">
      <input type="text" id="sideSearch" placeholder="Tìm chữ Hán / pinyin…" value="${esc(sideQ)}" autocomplete="off">${sug}
      <div class="loader" style="margin-top:10px"><label class="file">📄 Nạp dictionary.txt<input type="file" id="dictFile" accept=".txt"></label>
      <div class="muted" style="font-size:11px;margin-top:5px">Đang dùng <b id="sideCount">${DICT.length}</b> chữ</div></div>
    </div>
    <div class="side-card">
      <div class="side-title">84 bộ thủ <a href="#/radicals" style="font-size:11px;font-weight:600">mở đầy đủ →</a></div>
      <div class="side-cfilter">${cats.map(c=>`<button class="cchip ${sideCat===c?"on":""}" data-c="${c}" title="${CILIN_NAMES[c]}" style="--cc:${CILIN_COLORS[c]}">${c}</button>`).join("")}</div>
      <div class="side-radgrid">${Object.keys(RAD_RADICALS).filter(b=>!sideCat||(SHUOWEN[b]&&(SHUOWEN[b][6]===sideCat||SHUOWEN[b][7]===sideCat))).map(b=>{
        const r=RAD_RADICALS[b];return `<button class="side-rad" data-b="${esc(b)}" title="${r[1]} — ${esc(r[2])}"><span>${r[0]}</span><b class="font-cjk">${esc(b)}</b></button>`;}).join("")}</div>
      <label class="hsk-toggle" style="margin-top:8px"><input type="checkbox" id="sideHsk" ${sideHsk?"checked":""}> Chỉ HSK1 (áp dụng ở màn Bộ Thủ)</label>
    </div>`;
  const si=document.getElementById("sideSearch");
  si.oninput=()=>{sideQ=si.value;renderSidebar();document.getElementById("sideSearch").focus();const v=document.getElementById("sideSearch");v.setSelectionRange(v.value.length,v.value.length);};
  si.onkeydown=e=>{if(e.key==="Enter"){const g=si.value.trim();if(getEntry(g))nav("#/analysis/"+encodeURIComponent(g));}};
  el.querySelectorAll(".cchip").forEach(b=>b.onclick=()=>{sideCat=(sideCat===b.dataset.c?null:b.dataset.c);renderSidebar();});
  el.querySelectorAll(".side-rad").forEach(b=>b.onclick=()=>{radicals={cat:"all",sel:b.dataset.b,hskOnly:sideHsk};nav("#/radicals");if(route.name==="radicals")renderRoute();});
  const sh=document.getElementById("sideHsk");if(sh)sh.onchange=()=>{sideHsk=sh.checked;if(radicals)radicals.hskOnly=sideHsk;if(route.name==="radicals")renderRoute();};
  const df=document.getElementById("dictFile");if(df)df.onchange=e=>{const f=e.target.files[0];if(!f)return;const rd=new FileReader();rd.onload=()=>{try{const lines=rd.result.split("\n").map(l=>l.trim()).filter(Boolean);DICT=lines.map(l=>JSON.parse(l));rebuildIndex();beep(1046,90,"triangle");renderSidebar();renderRoute();}catch(err){alert("Không đọc được file: "+err.message);}};rd.readAsText(f);};
}
let sideCat=null,sideHsk=true;

/* ================= MÀN 1: NGỮ NGHĨA CHÍNH (#/) ================= */
const BR_SOFT={literal:"var(--teal-soft)",metaphor:"var(--clay-soft)",idiom:"var(--violet-soft)"};
const BR_INK={literal:"var(--teal)",metaphor:"var(--clay)",idiom:"var(--violet)"};
function wordPill(w){
  return `<div class="word-pill" data-w="${esc(w.hanzi)}">
    <div class="wp-head"><b class="font-cjk-serif">${esc(w.hanzi)}</b><span class="wp-py">${esc(w.pinyin)}</span>${w.hsk?`<span class="wp-hsk">HSK${w.hsk}</span>`:""}</div>
    <div class="wp-mean">${esc(w.hanViet)} · ${esc(w.meaning)}</div>
    <div class="wp-bridge" style="display:none">${(w.bridge||[]).map(b=>{
      const lbl={root:"Gốc",extension:"Chuyển",modern:"Nay"}[b.kind]||b.kind;
      return `<div class="wp-step"><span class="wp-k">${lbl}</span>${esc(b.text)}</div>`;}).join("")}</div></div>`;
}
function screenHome(){
  const g="吃",cu=CURATED[g];
  const a=anaOf(g);
  const main=`
    <div class="hero-root card">
      <div class="hero-glyph font-cjk-serif">${g}</div>
      <div class="hero-info">
        <div class="hero-title">${g} · <span class="hv">${esc(cu.hanViet)}</span>
          <span class="chip chip-clay">${esc(cu.pinyin)}</span><span class="chip chip-teal">HSK ${cu.hsk}</span><span class="chip">bộ ${esc(cu.radical)}</span></div>
        <p class="hero-core">${esc(cu.conceptCore)}</p>
        ${a?`<div class="hero-formula">${renderFormula(a)}</div>`:""}
        <div class="hero-cta">
          <a class="btn-primary" href="#/analysis/${g}">Phân tích chi tiết</a>
          <a class="btn-ghost" href="#/graph?mode=structure&focus=${g}">Khám phá đồ thị</a>
        </div>
      </div>
    </div>
    <div class="card branch-card">
      <h3 class="card-title">Cây ngữ nghĩa · 3 tầng nghĩa</h3>
      ${cu.branches.map(br=>`
        <div class="branch">
          <div class="br-chip" style="background:${BR_SOFT[br.type]};color:${BR_INK[br.type]}">L${br.level} · ${esc(br.title)}</div>
          <div class="br-line"></div>
          <div class="br-words">${br.words.map(wordPill).join("")}</div>
        </div>`).join("")}
      <div class="muted" style="font-size:12px;margin-top:6px">Bấm một từ để xem cầu nghĩa Gốc → Chuyển → Nay.</div>
    </div>
    <div class="card"><h3 class="card-title">💡 Mẹo ghi nhớ</h3><p style="margin:0;font-size:14px;line-height:1.7">${esc(cu.mnemonic)}</p></div>`;
  const right=`
    <div class="card"><h3 class="card-title">Từ ghép biên soạn</h3>
      ${cu.compounds.map(cp=>`<a class="cmp-item" href="#/compound/${cp.id}"><b class="font-cjk-serif">${esc(cp.hanzi)}</b><span>${esc(cp.pinyin)} · ${esc(cp.meaning)}</span></a>`).join("")}
    </div>
    <div class="card"><h3 class="card-title">Trạng thái biên soạn</h3>
      <p class="muted" style="font-size:13px;margin:0">Đã soạn tay: <b style="color:var(--ink)">${Object.keys(CURATED).length}</b> chữ (${Object.keys(CURATED).join(", ")}). Các chữ khác hiển thị dữ liệu máy ở màn Phân tích.</p></div>`;
  return {main,right,wire(){
    document.querySelectorAll(".word-pill").forEach(el=>el.onclick=()=>{const b=el.querySelector(".wp-bridge");b.style.display=b.style.display==="none"?"":"none";});
  }};
}

/* ================= MÀN 2: PHÂN TÍCH (#/analysis/<chữ>) ================= */
function constructionDiagram(a){
  if(!a.parts||!a.parts.length)return "";
  const sem=a.parts.find(p=>p.role==="semantic"),pho=a.parts.find(p=>p.role==="phonetic");
  const semBox=sem?`<a class="cd-box cd-sem" href="#/graph?mode=semantic&focus=${encodeURIComponent(sem.res.base)}">
      <div class="cd-k">BIỂU Ý</div><div class="cd-vis">${semIconHTML(sem.res.base,40)}</div>
      <div class="cd-g font-cjk">${esc(sem.glyph)}</div>
      <div class="cd-sub">${SHUOWEN[sem.res.base]?esc(SHUOWEN[sem.res.base][0]):""}</div>
      ${cilinBadge(sem.res.base)}</a>`:"";
  const phoBox=pho?`<a class="cd-box cd-pho" href="#/graph?mode=phonetic&focus=${encodeURIComponent(pho.glyph)}">
      <div class="cd-k">BIỂU ÂM</div>
      <div class="cd-pg font-cjk-serif">${esc(pho.glyph)}${pho.fade?`<span class="cd-fade">${pho.fade}</span>`:""}</div>
      <div class="cd-sub">${esc(pho.pinyin||"")}</div></a>`:"";
  const others=(!sem&&!pho)?a.parts.map(p=>`<div class="cd-box cd-sem"><div class="cd-k">${POS_LABEL_VN(p.pos)}</div><div class="cd-vis">${semIconHTML(p.res.base,36)}</div><div class="cd-g font-cjk">${esc(p.glyph)}</div></div>`).join("<div class='cd-plus'>+</div>"):"";
  return `<div class="cd">
    <div class="cd-box cd-product"><div class="cd-k">CHỮ THÀNH PHẨM</div><div class="cd-big font-cjk-serif">${a.glyph}</div><div class="cd-sub">${esc(a.pinyin)}</div></div>
    <div class="cd-arrow">›</div>${semBox||others}${sem&&pho?`<div class="cd-plus">+</div>`:""}${phoBox}
  </div>`;
}
function POS_LABEL_VN(p){return ({left:"TRÁI",right:"PHẢI",top:"TRÊN",bottom:"DƯỚI",middle:"GIỮA",outer:"NGOÀI",inner:"TRONG",whole:"TOÀN"})[p]||p;}
function screenAnalysis(g){
  g=g||"清";
  const e=getEntry(g);
  if(!e){
    return {main:`<div class="card center" style="padding:50px"><div class="font-cjk-serif" style="font-size:80px">${esc(g)}</div>
      <p class="muted">Chữ này chưa có trong từ điển đang nạp (${DICT.length} chữ). Nạp <b>dictionary.txt</b> đầy đủ ở cột trái để tra mọi chữ.</p></div>`,right:"",wire(){}};
  }
  const a=anaOf(g);
  const cu=CURATED[g];
  const hv=cu?cu.hanViet:null;
  const cp=g.codePointAt(0).toString(16).toUpperCase();
  const hsk=cu&&cu.hsk?("HSK "+cu.hsk):(HSK1.has(g)?"HSK 1":"—");
  const idsOp=e.decomposition?Array.from(e.decomposition)[0]:null;
  const struct=idsOp&&IDS_NAME[idsOp]?`${idsOp} ${IDS_NAME[idsOp]}`:"đơn thể";
  const sem=a.parts&&a.parts.find(p=>p.role==="semantic");
  const parts=a.parts?a.parts.map(p=>({...p,glyph:p.glyph})):[];
  // họ âm học
  let phonFam="";
  const pho=a.parts&&a.parts.find(p=>p.role==="phonetic");
  if(pho){
    const fam=(PHON_INDEX.get(pho.glyph)||[]).filter(x=>x!==g).slice(0,8);
    phonFam=fam.length?`<div class="fam-grid">${fam.map(x=>{const c=CHAR_BY_GLYPH[x];return `<a class="fam-item" href="#/analysis/${encodeURIComponent(x)}"><b class="font-cjk-serif">${x}</b><span>${c?c.pinyin:""}</span></a>`;}).join("")}</div>`
      :`<p class="muted" style="font-size:13px">Chưa thấy chữ khác cùng âm <b class="font-cjk">${esc(pho.glyph)}</b> trong ${DICT.length} chữ đang nạp — nạp từ điển đầy đủ để mở rộng.</p>`;
  } else phonFam=`<p class="muted" style="font-size:13px">Chữ này không phải hình thanh nên không có họ âm.</p>`;
  // cây ngữ nghĩa curated
  const tree=cu?`<div>${cu.branches.map(br=>`<div class="mini-branch"><span class="br-chip sm" style="background:${BR_SOFT[br.type]};color:${BR_INK[br.type]}">L${br.level}</span> ${br.words.map(w=>`<span class="mini-word font-cjk">${esc(w.hanzi)}</span>`).join(" ")}</div>`).join("")}
      <a class="btn-ghost sm" href="#/" style="margin-top:8px">Mở cây đầy đủ →</a></div>`
    :`<p class="muted" style="font-size:13px">「${esc(g)}」<b>chưa biên soạn</b> cây ngữ nghĩa. Hiện mới soạn: ${Object.keys(CURATED).map(x=>`<a href="#/analysis/${x}" class="font-cjk">${x}</a>`).join(" ")}</p>`;
  const main=`
    <div class="ana-row">
      <div class="card ana-glyph">
        <div class="tz-wrap">${Tianzige(parts,null)}</div>
        <div class="center" style="margin-top:8px"><b style="font-size:20px">${esc(a.pinyin)}</b>${hv?` · <span class="hv">${esc(hv)}</span>`:""}<div class="muted" style="font-size:13px">${esc(a.def)}</div></div>
        <div class="center" style="margin-top:10px;display:flex;gap:8px;justify-content:center">
          <a class="btn-ghost sm" href="#/graph?mode=structure&focus=${encodeURIComponent(g)}">Đồ thị</a>
          <a class="btn-ghost sm" href="#/compound/chicu">Từ ghép</a></div>
      </div>
      <div class="card">
        <h3 class="card-title">Thông số nhanh</h3>
        <div class="specs">
          <div><span>Unicode</span><b>U+${cp}</b></div>
          <div><span>Bộ thủ</span><b class="font-cjk">${esc(e.radical||"—")}</b></div>
          <div><span>HSK</span><b>${hsk}</b></div>
          <div><span>Pinyin</span><b>${(e.pinyin||[]).join(", ")}</b></div>
        </div>
      </div>
      <div class="card">
        <h3 class="card-title">Cấu trúc & Loại hình</h3>
        <div style="margin-bottom:8px">${typeBadge(a.type)}</div>
        <div class="specs"><div><span>Cấu trúc IDS</span><b>${struct}</b></div>
        <div><span>Phân rã</span><b class="font-cjk">${esc(e.decomposition||"—")}</b></div></div>
        ${a.hint?`<p class="muted" style="font-size:12px;margin:8px 0 0">Gợi ý: ${esc(a.hint)}</p>`:""}
      </div>
    </div>
    ${a.parts&&a.parts.length?`<div class="card"><h3 class="card-title">Sơ đồ cấu tạo · Construction</h3>${constructionDiagram(a)}
      ${sem?`<details class="shuowen" style="margin-top:12px"><summary>Xem Thuyết Văn Giải Tự 說文解字 — bộ ${esc(sem.res.base)}</summary><div class="body">${shuowenBlock(sem.res.base)}</div></details>`:""}</div>`
      :`<div class="card center"><h3 class="card-title">Chữ ${a.type}</h3><div style="font-size:76px">${a.pictoEmoji||`<span class='font-cjk-serif'>${a.glyph}</span>`}</div>${a.hint?`<p class="muted">${esc(a.hint)}</p>`:""}</div>`}
    <div class="two-col">
      <div class="card"><h3 class="card-title">🌳 Cây ngữ nghĩa</h3>${tree}</div>
      <div class="card"><h3 class="card-title">🔊 Họ âm học${pho?` — thành phần <b class="font-cjk">${esc(pho.glyph)}</b>`:""}</h3>${phonFam}</div>
    </div>`;
  const right=sem?`<div class="card"><h3 class="card-title">Bộ ${esc(sem.res.base)} · 4 tầng nghĩa</h3>${shuowenBlock(sem.res.base)}
      <a class="btn-ghost sm" href="#/radicals" style="margin-top:10px" id="openRad">Mở màn Bộ Thủ →</a></div>`
    :`<div class="card"><h3 class="card-title">Ghi chú</h3><p class="muted" style="font-size:13px">Chữ đơn thể — xem bộ thủ gốc ở màn Bộ Thủ.</p></div>`;
  return {main,right,wire(){
    const or_=document.getElementById("openRad");if(or_&&sem)or_.onclick=()=>{radicals={cat:"all",sel:sem.res.base,hskOnly:sideHsk};};
  }};
}

/* ================= MÀN 3: ĐỒ THỊ (#/graph) ================= */
function graphData(mode,focus){
  const nodes=[];
  if(mode==="semantic"){
    const base=RAD_RADICALS[focus]?focus:(anaOf(focus)&&anaOf(focus).parts?anaOf(focus).parts.find(p=>p.role==="semantic")?.res.base:null)||"水";
    (SEM_INDEX.get(base)||[]).slice(0,12).forEach(g=>nodes.push({g,py:CHAR_BY_GLYPH[g]?.pinyin||"",link:"#/analysis/"+encodeURIComponent(g)}));
    return {center:{g:base,py:RAD_RADICALS[base]?RAD_RADICALS[base][1]:""},nodes,centerIsRad:!!RAD_RADICALS[base],base};
  }
  if(mode==="phonetic"){
    (PHON_INDEX.get(focus)||[]).slice(0,12).forEach(g=>nodes.push({g,py:CHAR_BY_GLYPH[g]?.pinyin||"",link:"#/analysis/"+encodeURIComponent(g)}));
    return {center:{g:focus,py:lookupPinyin(focus)||KB_PINYIN[focus]||""},nodes,centerIsRad:!!RAD_RADICALS[baseOf(focus)],base:baseOf(focus)};
  }
  // structure
  const e=getEntry(focus);
  if(e&&e.decomposition){
    topOperands(e.decomposition).forEach(o=>{
      const b=resolveComponent(o.glyph,o.pos,{}).base;
      nodes.push({g:o.glyph,py:POS_LABEL_VN(o.pos),link:RAD_RADICALS[b]?"#/graph?mode=semantic&focus="+encodeURIComponent(b):(getEntry(o.glyph)?"#/analysis/"+encodeURIComponent(o.glyph):null)});
    });
  }
  return {center:{g:focus,py:CHAR_BY_GLYPH[focus]?.pinyin||""},nodes,centerIsRad:!!RAD_RADICALS[baseOf(focus)],base:baseOf(focus)};
}
function graphSVG(d){
  const W=560,H=440,cx=W/2,cy=H/2;
  const n=d.nodes.length;
  const items=d.nodes.map((nd,i)=>{
    const ang=-Math.PI/2+i*(2*Math.PI/Math.max(n,1));
    const r=150;
    const x=cx+r*Math.cos(ang),y=cy+r*Math.sin(ang);
    const mx=cx+(r*0.5)*Math.cos(ang+0.25),my=cy+(r*0.5)*Math.sin(ang+0.25);
    return `<path d="M${cx} ${cy} Q${mx} ${my} ${x} ${y}" fill="none" stroke="var(--border)" stroke-width="2"/>
      <g class="gnode" data-link="${nd.link||""}" transform="translate(${x},${y})" style="cursor:${nd.link?"pointer":"default"}">
      <circle r="34" fill="var(--card)" stroke="var(--teal)" stroke-width="2"/>
      <text y="2" text-anchor="middle" style="font-size:24px;font-family:'Noto Serif SC',serif;fill:var(--ink)">${nd.g}</text>
      <text y="20" text-anchor="middle" style="font-size:9px;fill:var(--ink-soft)">${nd.py}</text></g>`;
  }).join("");
  return `<svg viewBox="0 0 ${W} ${H}" class="graph-svg">
    ${items}
    <g><circle cx="${cx}" cy="${cy}" r="46" fill="var(--teal-soft)" stroke="var(--teal)" stroke-width="3"/>
    <text x="${cx}" y="${cy+6}" text-anchor="middle" style="font-size:34px;font-family:'Noto Serif SC',serif;fill:var(--ink)">${d.center.g}</text>
    <text x="${cx}" y="${cy+26}" text-anchor="middle" style="font-size:10px;fill:var(--ink-soft)">${d.center.py}</text></g>
  </svg>`;
}
function screenGraph(params){
  const mode=params.mode||"semantic";
  const focus=params.focus||(mode==="phonetic"?"青":"水");
  const d=graphData(mode,focus);
  const modes=[["semantic","Biểu Ý","cùng bộ nghĩa","teal"],["structure","Cấu tạo","cây thành phần IDS","clay"],["phonetic","Biểu Âm","cùng thành phần âm","violet"]];
  const main=`
    <div class="graph-wrap">
      <div class="graph-modes">
        ${modes.map(([id,lbl,hint,tone])=>`<a class="gmode ${mode===id?"on":""}" style="--tone:var(--${tone});--tone-soft:var(--${tone}-soft)" href="#/graph?mode=${id}&focus=${encodeURIComponent(focus)}"><b>${lbl}</b><span>${hint}</span></a>`).join("")}
        <div class="card" style="padding:10px;font-size:11px;color:var(--ink-soft)">Chú giải: node giữa = focus · node quanh = ${mode==="structure"?"thành phần cấp 1":"chữ liên quan"} (tối đa 12) · bấm node để đi tiếp.${DICT.length<100?" Nạp từ điển đầy đủ để đồ thị giàu hơn.":""}</div>
      </div>
      <div class="card graph-stage">${d.nodes.length?graphSVG(d):`<div class="center muted" style="padding:60px 20px">Chưa có node nào cho <b class="font-cjk">${esc(focus)}</b> ở chế độ này trong ${DICT.length} chữ đang nạp.</div>`}</div>
    </div>`;
  const sw=RAD_RADICALS[d.base]?SHUOWEN[d.base]:null;
  const right=`<div class="card"><h3 class="card-title">Node focus: <span class="font-cjk-serif" style="font-size:24px">${esc(focus)}</span></h3>
    ${sw?`<p style="font-size:13px;margin:4px 0"><b>Ý nghĩa cốt lõi:</b> ${esc(sw[0])}</p><p class="muted" style="font-size:12px">${esc(sw[1])}</p>${cilinBadge(d.base)}`
        :`<p class="muted" style="font-size:13px">${CHAR_BY_GLYPH[focus]?esc(CHAR_BY_GLYPH[focus].def):"—"}</p>`}
    ${getEntry(focus)?`<a class="btn-primary sm" href="#/analysis/${encodeURIComponent(focus)}" style="margin-top:10px">Xem phân tích chi tiết</a>`:""}
  </div>`;
  return {main,right,wire(){
    document.querySelectorAll(".gnode").forEach(el=>el.onclick=()=>{const l=el.dataset.link;if(l)nav(l);});
  }};
}

/* ================= MÀN 4: TỪ GHÉP (#/compound/<id>) ================= */
function allCompounds(){const out=[];for(const [g,cu] of Object.entries(CURATED))(cu.compounds||[]).forEach(c=>out.push({...c,parent:g}));return out;}
function miniFormula(g){
  const a=anaOf(g);
  if(!a||!a.parts)return "";
  const sem=a.parts.find(p=>p.role==="semantic"),pho=a.parts.find(p=>p.role==="phonetic");
  return `<div class="mini-f">${sem?semIconHTML(sem.res.base,18):""}${pho?`<span class="mini-am font-cjk">${esc(pho.glyph)}</span>`:""}</div>`;
}
function screenCompound(id){
  const list=allCompounds();
  const cp=list.find(c=>c.id===id)||list[0];
  if(!cp)return {main:`<div class="card center" style="padding:40px"><p class="muted">Chưa biên soạn từ ghép nào.</p></div>`,right:"",wire(){}};
  const glyphs=Array.from(cp.hanzi);
  const main=`
    <div class="card cmp-list-inline">${list.map(c=>`<a class="pill ${c.id===cp.id?"active":""}" href="#/compound/${c.id}"><span class="font-cjk">${esc(c.hanzi)}</span> ${esc(c.pinyin)}</a>`).join("")}</div>
    <div class="card center">
      <div class="cmp-hero">${glyphs.map(g=>`<div class="cmp-g"><div class="font-cjk-serif big-g">${g}</div>
        <div class="chip">${hanVietOf(g)||(CURATED[cp.parent]&&g===cp.parent?CURATED[cp.parent].hanViet:"")||(SHUOWEN[baseOf(g)]?RAD_RADICALS[baseOf(g)][2]:"")}</div>${miniFormula(g)}</div>`).join('<div class="cmp-plus">+</div>')}</div>
      <div style="font-size:20px;font-weight:700;margin-top:8px">${esc(cp.pinyin)}</div>
      <div class="muted">${esc(cp.hanViet)} — ${esc(cp.meaning)}</div>
    </div>
    <div class="card"><h3 class="card-title">Ý niệm cốt lõi</h3><p style="margin:0;font-size:14px;line-height:1.7">${esc(cp.conceptCore)}</p></div>
    <div class="card"><h3 class="card-title">Cầu ngữ nghĩa · Semantic Bridge</h3>
      <div class="bridge">${cp.bridge.map((b,i)=>`
        <div class="b-step"><div class="b-num">0${i+1}</div><div><div class="b-k">${esc(b.step)}</div><p>${esc(b.text)}</p></div></div>
        ${i<cp.bridge.length-1?'<div class="b-arrow">↓</div>':""}`).join("")}</div></div>
    <div class="card"><h3 class="card-title">Cụm hay gặp · Collocations</h3>
      <div class="colloc">${cp.collocations.map(c=>`<div class="col-item"><b class="font-cjk">${esc(c.hanzi)}</b><span>${esc(c.pinyin)}</span><small>${esc(c.meaning)}</small></div>`).join("")}</div></div>`;
  const right=`
    <div class="card"><h3 class="card-title">⚠️ Lưu ý sử dụng</h3><ul class="notes">${cp.usageNotes.map(n=>`<li>${esc(n)}</li>`).join("")}</ul></div>
    <div class="card"><h3 class="card-title">Ví dụ</h3>${cp.examples.map(ex=>`<div class="example"><div class="font-cjk" style="font-size:16px">${esc(ex.hanzi)}</div><div class="muted" style="font-size:12px">${esc(ex.pinyin)}</div><div style="font-size:13px">${esc(ex.meaning)}</div></div>`).join("")}</div>`;
  return {main,right,wire(){}};
}

/* ================= MÀN 5+6: BỘ THỦ & LUYỆN TẬP (bảo toàn) ================= */
function screenRadicals(){
  if(!radicals)radicals={cat:"all",sel:null,hskOnly:sideHsk};
  currentMode="radicals";
  return {main:`<main class="panel" style="padding:26px"><div id="panel"></div></main>`,
    right:`<div class="card"><h3 class="card-title">Về màn này</h3><p class="muted" style="font-size:13px;margin:0">Lưới 84 bộ Khang Hy rút gọn, nhóm theo 9 đại loại <b>同义词词林 Cilin</b>. Bấm một bộ để xem đủ 4 tầng nghĩa (nghĩa đen · vai trò ghép · nguyên văn 說文解字 + dịch · ví dụ) và mọi chữ chứa bộ đó trong từ điển đang nạp.</p></div>`,
    wire(){mountMode();}};
}
const GAME_MODES=[{id:"learn",label:"Học chữ",hint:"Đoán từ nghĩa"},{id:"assemble",label:"Ghép chữ",hint:"Kéo-thả"},{id:"create",label:"Sáng tạo",hint:"Tìm chữ từ mảnh"},{id:"quiz",label:"Đố bộ thủ",hint:"5 dạng câu hỏi"}];
const MODE_GRAD={learn:"linear-gradient(135deg,#0E7C6B,#4aa3d8)",assemble:"linear-gradient(135deg,#C97A3B,#e0a651)",create:"linear-gradient(135deg,#7C6BD8,#d183a2)",quiz:"linear-gradient(135deg,#4aa3d8,#7C6BD8)",radicals:"linear-gradient(135deg,#7ba86f,#6f9fc4)",analyze:"linear-gradient(135deg,#0E7C6B,#7C6BD8)"};
function screenPractice(){
  if(!GAME_MODES.some(m=>m.id===currentMode))currentMode="learn";
  return {main:`
    <nav class="modes" id="modeNav"></nav>
    <main class="panel"><div class="panel-bar" id="panelBar"></div><div id="panel"></div></main>`,
    right:`<div class="card"><h3 class="card-title">4 trò luyện tập</h3><p class="muted" style="font-size:13px;margin:0">Học chữ (đoán thành phần từ nghĩa) · Ghép chữ (kéo-thả, có âm thanh &amp; rung) · Sáng tạo (tìm chữ từ mảnh) · Đố bộ thủ (5 dạng trắc nghiệm, tính điểm). Toàn bộ luồng chơi giữ nguyên từ bản trước, chỉ đổi tông màu.</p></div>`,
    wire(){buildNav();document.getElementById("panelBar").style.background=MODE_GRAD[currentMode];mountMode();}};
}

/* ================= SHELL CŨ (mountMode cho radicals + games) ================= */
let currentMode="learn";
const RENDERERS={radicals:renderRadicals,learn:renderLearn,assemble:renderAssemble,create:renderCreate,quiz:renderQuiz};
function mountMode(){const r=RENDERERS[currentMode];if(!r)return;const {html,wire}=r();const panel=document.getElementById("panel");if(!panel)return;panel.innerHTML=html;if(wire)wire();}
function buildNav(){
  const nav=document.getElementById("modeNav");if(!nav)return;
  nav.innerHTML=GAME_MODES.map(m=>`<button class="mode-btn ${m.id===currentMode?"active":""}" data-mode="${m.id}"><span class="bar" style="background:${MODE_GRAD[m.id]}"></span><span class="lbl">${m.label}<span class="hint">· ${m.hint}</span></span></button>`).join("");
  nav.querySelectorAll(".mode-btn").forEach(b=>b.onclick=()=>{currentMode=b.dataset.mode;if(currentMode==="learn")learn=null;if(currentMode==="assemble")assemble=null;if(currentMode==="create")create=null;if(currentMode==="quiz")quiz=null;nav.querySelectorAll(".mode-btn").forEach(x=>x.classList.toggle("active",x.dataset.mode===currentMode));document.getElementById("panelBar").style.background=MODE_GRAD[currentMode];beep(740,60,"sine",0.04);mountMode();});
}

/* ================= RENDER ROUTE ================= */
const SCREENS={home:()=>screenHome(),analysis:()=>screenAnalysis(route.arg),graph:()=>screenGraph(route.params),compound:()=>screenCompound(route.arg),radicals:()=>screenRadicals(),practice:()=>screenPractice()};
function renderRoute(){
  renderShell();
  const s=SCREENS[route.name]();
  document.getElementById("main").innerHTML=s.main;
  document.getElementById("detail").innerHTML=s.right||"";
  if(s.wire)s.wire();
  window.scrollTo(0,0);
}

/* ================= ICON TOGGLE + PROBE ================= */
function setIconMode(m){ICON_MODE=m;document.querySelectorAll("#iconToggle button").forEach(b=>b.classList.toggle("active",b.dataset.m===m));renderRoute();}
document.querySelectorAll("#iconToggle button").forEach(b=>b.onclick=()=>{setIconMode(b.dataset.m);beep(700,50,"sine",0.04);});
(function(){const im=new Image();im.onload=()=>{ICON3D_OK=true;setIconMode("3d");};im.onerror=()=>{ICON3D_OK=false;};im.src="icons3d/1f4a7_水.png";})();


/* ================= KHỞI ĐỘNG ================= */
rebuildIndex();
route=parseHash();
renderSidebar();
renderRoute();
runResolverTests();
