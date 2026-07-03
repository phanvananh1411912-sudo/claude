// resolver.test.mjs — test tối thiểu cho resolver (chạy: node resolver.test.mjs)
import { resolveComponent, analyzeCharacter, topOperands } from "./resolver.mjs";
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

console.log(`\n[resolver.test] ${pass} pass, ${fail} fail`);
process.exit(fail ? 1 : 0);
