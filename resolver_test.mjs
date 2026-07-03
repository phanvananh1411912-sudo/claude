// resolver_test.mjs — test cho resolver (chạy: node resolver_test.mjs)
import { resolveComponent, analyzeCharacter, topOperands, pickIconLayer } from "./resolver.mjs";
import { SAMPLE_DICT } from "./data.mjs";

const dictByChar = {}; SAMPLE_DICT.forEach(e => dictByChar[e.character] = e);
let pass = 0, fail = 0;
function eq(got, exp, name){ if (got === exp){ pass++; } else { fail++; console.error(`✗ ${name}\n   got: ${got}\n   exp: ${exp}`); } }
const A = g => analyzeCharacter(dictByChar[g], dictByChar);

// --- resolveComponent (mục 3) ---
eq(resolveComponent("氵","left",{hint:"water"}).emoji, "💧", "氵 → 水 💧 (江/河/清)");
eq(resolveComponent("忄","left",{hint:"heart"}).emoji, "❤️", "忄 → 心 ❤️ (情/忙)");
eq(resolveComponent("灬","bottom",{hint:"fire"}).emoji, "🔥", "灬 → 火 🔥 (热/照)");
eq(resolveComponent("阝","left",{}).emoji, "🏔️", "阝 trái → 阜 🏔️ (阿)");
eq(resolveComponent("阝","right",{}).emoji, "🏘️", "阝 phải → 邑 🏘️ (都)");
eq(resolveComponent("月","left",{hint:"flesh"}).emoji, "🥩", "月 flesh → 肉 🥩 (腿/肝)");
eq(resolveComponent("月","right",{}).emoji, "🌙", "月 thường → 🌙 (明)");
eq(resolveComponent("王","left",{hint:"jade"}).emoji, "💎", "王 trái → 玉 💎 (玩/球)");
eq(resolveComponent("彳","left",{}).found, false, "彳 fallback (không emoji) (很)");

// --- analyzeCharacter (nghiệm thu) ---
eq(A("清").type, "hình thanh", "清 badge Hình thanh");
eq(A("清").parts[0].res.emoji + "+" + A("清").parts[1].glyph, "💧+青", "清 = 💧 + 青");
eq(A("清").parts[1].pinyin, "qīng", "清 âm 青 = qīng");
eq(A("木").type, "tượng hình", "木 badge Tượng hình");
eq(A("木").pictoEmoji, "🌳", "木 emoji 🌳");
eq(A("上").type, "chỉ sự", "上 badge Chỉ sự");
eq(A("妈").parts[0].res.emoji, "👩", "妈 nghĩa 女 👩");
eq(A("妈").parts[1].glyph + " " + A("妈").parts[1].pinyin, "马 mǎ", "妈 âm 马 mǎ");
eq(A("妈").parts[1].fade, "🐴", "妈 âm 马 có emoji mờ 🐴");
eq(A("明").parts.map(p=>p.role==="semantic"?p.res.emoji:p.glyph).join("+"), "☀️+🌙", "明 = ☀️ + 🌙");

// --- topOperands (IDS) ---
eq(JSON.stringify(topOperands("⿰氵青")), JSON.stringify([{glyph:"氵",pos:"left"},{glyph:"青",pos:"right"}]), "IDS ⿰氵青 vị trí trái/phải");

// --- bổ sung: ideographic có decomposition, pictoEmoji, PINYIN_FB ---
eq(A("好").parts.length, 2, "好 (hội ý có decomposition) → 2 phần");
eq(A("好").parts[0].res.emoji, "👩", "好 phần 女 → 👩");
eq(A("好").parts[1].res.emoji, "👶", "好 phần 子 → 👶");
eq(A("青").pictoEmoji, "🌿", "青 (bản thân là bộ) → pictoEmoji 🌿");
eq(A("都").parts[1].glyph + " " + A("都").parts[1].pinyin, "者 zhě", "都 âm 者 = zhě (PINYIN_FB)");

// --- bổ sung: topOperands với toán tử bao ⿴ và ba phần ⿲ ---
eq(JSON.stringify(topOperands("⿴囗口")), JSON.stringify([{glyph:"囗",pos:"outer"},{glyph:"口",pos:"inner"}]), "IDS ⿴ outer/inner");
eq(JSON.stringify(topOperands("⿲彳言正")), JSON.stringify([{glyph:"彳",pos:"left"},{glyph:"言",pos:"middle"},{glyph:"正",pos:"right"}]), "IDS ⿲ left/middle/right");

// --- bổ sung: 王 bên phải giữ nguyên 王 (không thành 玉) ---
eq(resolveComponent("王","right",{}).base, "王", "王 phải → giữ 王");

// --- bổ sung: pickIconLayer (tầng icon3d, thuần không DOM) ---
eq(pickIconLayer("水", true), "icon3d", "水 + chế độ 3D → icon3d");
eq(pickIconLayer("水", false), "svg", "水 + chế độ Nét → svg");
eq(pickIconLayer("口", false), "seal", "口 (icon seal) → seal");
eq(pickIconLayer("彳", false), "text", "彳 (không icon/emoji) → text");

console.log(`\n[resolver_test] ${pass} pass, ${fail} fail`);
process.exit(fail ? 1 : 0);
