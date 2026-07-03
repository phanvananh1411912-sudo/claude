// resolver.mjs — logic phân giải thành phần chữ Hán (thuần, không DOM).
// Dùng chung cho app (index.html nhúng bản sao) và test độc lập (resolver.test.mjs).
import { RAD_RADICALS, RAD_VARIANTS, PINYIN_FB, RAD_ICON, RAD_ICON3D } from "./data.mjs";

export function baseOf(g){ return RAD_VARIANTS[g] || g; }
export function emojiForHan(g){ const r = RAD_RADICALS[baseOf(g)]; return r ? r[0] : null; }

export function radInfo(base, orig){
  const r = RAD_RADICALS[base];
  if (r) return { found:true, base, orig, emoji:r[0], pinyin:r[1], vi:r[2], isVariant: base !== orig };
  return { found:false, base, orig, emoji:null, pinyin: PINYIN_FB[orig] || null, vi:null, isVariant:false, text:orig };
}

// resolveComponent(comp, position, context{hint}) -> {found, emoji, pinyin, vi, base, isVariant}
export function resolveComponent(comp, position, context){
  context = context || {};
  if (comp === "阝") return radInfo(position === "right" ? "邑" : "阜", comp);   // vị trí trái=阜 / phải=邑
  if (comp === "月") return radInfo(context.hint === "flesh" ? "肉" : "月", comp); // ngữ cảnh thịt -> 肉
  if (comp === "王") return radInfo(position === "left" ? "玉" : "王", comp);      // trái -> 玉
  return radInfo(baseOf(comp), comp);                                             // biến thể -> gốc
}

// ---- Parser IDS ----
const BIN = new Set(["⿰","⿱","⿴","⿵","⿶","⿷","⿸","⿹","⿺","⿻"]);
const TER = new Set(["⿲","⿳"]);
const POS = {"⿰":["left","right"],"⿱":["top","bottom"],"⿲":["left","middle","right"],"⿳":["top","middle","bottom"],
  "⿴":["outer","inner"],"⿵":["outer","inner"],"⿶":["outer","inner"],"⿷":["outer","inner"],
  "⿸":["outer","inner"],"⿹":["outer","inner"],"⿺":["outer","inner"],"⿻":["outer","inner"]};
function parseNode(chars, i){
  const ch = chars[i];
  if (BIN.has(ch) || TER.has(ch)){
    const n = TER.has(ch) ? 3 : 2; let idx = i + 1; const kids = [];
    for (let k=0;k<n;k++){ const r = parseNode(chars, idx); kids.push(r[0]); idx = r[1]; }
    return [{ op:ch, kids }, idx];
  }
  return [{ leaf:ch }, i + 1];
}
function nodeGlyph(n){ return n.leaf ? n.leaf : (n.kids ? n.kids.map(nodeGlyph).join("") : ""); }
export function topOperands(decomp){
  if (!decomp) return [];
  const chars = Array.from(decomp);
  let root; try { root = parseNode(chars, 0)[0]; } catch(e){ return []; }
  if (!root.op) return [{ glyph: root.leaf, pos: "whole" }];
  const poss = POS[root.op] || [];
  return root.kids.map((k, idx) => ({ glyph: nodeGlyph(k), pos: poss[idx] || "part" }));
}

// analyzeCharacter(entry, dictByChar) -> đối tượng hiển thị chuẩn hoá
export function analyzeCharacter(entry, dictByChar){
  dictByChar = dictByChar || {};
  const ety = entry.etymology || {};
  const lookupPinyin = g => (dictByChar[g] ? dictByChar[g].pinyin[0] : (PINYIN_FB[g] || null));
  const base = { glyph: entry.character, pinyin: (entry.pinyin||[])[0]||"", def: entry.definition||"",
                 decomp: entry.decomposition||"", radical: entry.radical };
  const ops = topOperands(entry.decomposition);
  const posOf = g => { const o = ops.find(o => o.glyph === g); return o ? o.pos : null; };

  if (ety.type === "pictophonetic"){
    const sPos = posOf(ety.semantic) || "left";
    const sem = resolveComponent(ety.semantic, sPos, { hint: ety.hint });
    const pPos = posOf(ety.phonetic) || (sPos === "left" ? "right" : sPos === "top" ? "bottom" : "right");
    return { ...base, type:"hình thanh", kind:"pictophonetic", hint:ety.hint,
      parts:[{ role:"semantic", glyph:ety.semantic, pos:sPos, res:sem },
             { role:"phonetic", glyph:ety.phonetic, pos:pPos, pinyin:lookupPinyin(ety.phonetic), fade:emojiForHan(ety.phonetic) }] };
  }
  if (ety.type === "pictographic")
    return { ...base, type:"tượng hình", kind:"pictographic", hint:ety.hint, pictoEmoji:emojiForHan(entry.character) };
  // ideographic / chỉ sự / hội ý
  if (RAD_RADICALS[baseOf(entry.character)])
    return { ...base, type: entry.decomposition ? "hội ý" : "chỉ sự", kind:"ideographic", hint:ety.hint, pictoEmoji: RAD_RADICALS[baseOf(entry.character)][0] };
  if (entry.decomposition){
    const parts = ops.map(o => ({ role:"semantic", glyph:o.glyph, pos:o.pos, res: resolveComponent(o.glyph, o.pos, { hint: ety.hint }) }));
    return { ...base, type:"hội ý", kind:"ideographic", hint:ety.hint, parts };
  }
  return { ...base, type:"chỉ sự", kind:"ideographic", hint:ety.hint };
}


// pickIconLayer(base, mode3d) -> tầng hiển thị cho thành phần NGHĨA (thuần, không DOM).
// Chuỗi ưu tiên: icon3d (PNG, khi bật 3D và có tên ảnh) → svg → seal → emoji → text.
export function pickIconLayer(base, mode3d){
  if (mode3d && RAD_ICON3D[base]) return "icon3d";
  const ic = RAD_ICON[base];
  if (ic === "seal") return "seal";
  if (ic) return "svg";
  if (RAD_RADICALS[baseOf(base)]) return "emoji";
  return "text";
}
