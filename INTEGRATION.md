# Tích hợp resolver/data vào app khác (React / TypeScript)

`resolver.mjs` và `data.mjs` là ES module **thuần logic, không DOM** — import được thẳng vào mọi dự án bundler (Vite/Next/CRA) hoặc Node ≥ 16.

```ts
import { resolveComponent, analyzeCharacter, topOperands, pickIconLayer } from "./resolver.mjs";
import { RAD_RADICALS, RAD_ICON, RAD_ICON3D, SAMPLE_DICT } from "./data.mjs";
```

(TypeScript: thêm `// @ts-ignore` hoặc file `.d.ts` mỏng; các hàm đều nhận/trả object thuần.)

## API chính

| Hàm | Vào | Ra |
|---|---|---|
| `resolveComponent(comp, position, ctx?)` | thành phần (`"氵"`, `"阝"`…), vị trí (`"left"/"right"/…`), `{hint}` | `{found, base, emoji, pinyin, vi, isVariant}` — đã xử lý biến thể + nhập nhằng 阝/月/王 |
| `analyzeCharacter(entry, dictByChar?)` | 1 entry makemeahanzi | `{glyph, type, kind, parts[], pictoEmoji?, hint}` — parts có `role: "semantic"/"phonetic"` |
| `topOperands(idsString)` | chuỗi IDS `"⿰氵青"` | `[{glyph, pos}]` cấp cao nhất (left/right/top/bottom/middle/outer/inner) |
| `pickIconLayer(base, mode3d)` | bộ gốc + cờ 3D | `"icon3d" \| "svg" \| "seal" \| "emoji" \| "text"` — tầng hiển thị nên dùng |

## Ví dụ: ô BIỂU Ý trong Construction Diagram (Semantic KB Viewer)

```tsx
function SemanticCell({ comp, pos }: { comp: string; pos: string }) {
  const r = resolveComponent(comp, pos, {});
  const layer = pickIconLayer(r.base, mode3d);
  switch (layer) {
    case "icon3d": return <img src={`icons3d/${RAD_ICON3D[r.base]}.png`} className="frame-blue"
                               onError={fallbackToSvg} alt={r.base} />;
    case "svg":    return <SvgIcon name={RAD_ICON[r.base]} className="text-blue-600" />; // currentColor
    case "seal":   return <span className="seal-circle">{r.base}</span>;
    case "emoji":  return <span>{r.emoji}</span>;
    default:       return <span className="gray-circle">{r.base}</span>;
  }
}
```

- SVG: lấy body từ `embed/icons.mjs` (`ICONS[RAD_ICON[base]]`) hoặc import trực tiếp `lucide-react`… theo tên sau dấu `:`.
- Chuỗi fallback phải giữ đúng thứ tự **icon3d → svg → seal/emoji → chữ** để đồng nhất với app gốc.
- Dữ liệu Thuyết Văn + Cilin cho tooltip/badge: `embed/shuowen.mjs` (`SHUOWEN[base]` = `[nghia_den, nghia_phai_sinh, nguyen_van, dich, vi_du, kiem_chung, dai_loai, dai_loai_phu, mien_nghia, tu_khoa_tra]`).
