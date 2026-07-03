// build.mjs — ghép template.html + data.mjs + embed/ + resolver.mjs thành index.html hoàn chỉnh.
// Chạy: node build.mjs   (không cần cài gói nào)
// Quy tắc: SỬA logic/dữ liệu ở data.mjs, resolver.mjs, embed/*.mjs — KHÔNG sửa trực tiếp index.html.
import { readFileSync, writeFileSync } from "node:fs";

const read = (p) => readFileSync(p, "utf8");

// Bỏ cú pháp module để nhúng vào <script> thường (chạy được qua file://):
// - xoá dòng import
// - xoá tiền tố "export " trước const/function
// - xoá dòng re-export dạng "export { ... };"
const strip = (src) =>
  src
    .replace(/^import[^\n]*\n/gm, "")
    .replace(/^export\s*\{[^}]*\}\s*;?\s*$/gm, "")
    .replace(/^export\s+/gm, "");

const DATA = [read("data.mjs"), read("embed/shuowen.mjs"), read("embed/icons.mjs")]
  .map(strip)
  .join("\n");
const RESOLVER = strip(read("resolver.mjs"));

let html = read("template.html");
for (const [ph, code] of [["/*__DATA__*/", DATA], ["/*__RESOLVER__*/", RESOLVER]]) {
  if (!html.includes(ph)) { console.error(`Thiếu placeholder ${ph} trong template.html`); process.exit(1); }
  html = html.replace(ph, () => code); // dùng hàm để "$" trong code không bị hiểu là pattern
}

writeFileSync("index.html", html);
console.log(`[build] index.html: ${(html.length / 1024).toFixed(1)} KB (data ${(DATA.length/1024).toFixed(1)} KB, resolver ${(RESOLVER.length/1024).toFixed(1)} KB)`);
