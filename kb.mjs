// kb.mjs — tầng dữ liệu BIÊN SOẠN TAY (curated), tách khỏi dữ liệu máy (data.mjs).
// Cấu trúc theo đặc tả Semantic KB Viewer. Chữ chưa soạn -> màn hình hiện "Chưa biên soạn".
// LƯU Ý: repo tham chiếu (Hanzi_Explorer/src/data/kb.ts) chưa được đính kèm phiên làm việc;
// nội dung 吃/吃醋 dưới đây do biên soạn lại theo đúng schema — thay bằng bản gốc khi có file.

export const CURATED = {
  "吃": {
    hanViet: "ngật",
    pinyin: "chī",
    hsk: 1,
    radical: "口",
    conceptCore: "Đưa vào miệng và nuốt — rồi mở rộng thành TIẾP NHẬN / CHỊU ĐỰNG / TIÊU HAO bất cứ thứ gì: thức ăn, sức lực, nỗi khổ, thiệt thòi, thậm chí cả… ghen tuông.",
    mnemonic: "Miệng 口 (BIỂU Ý) + 乞 xin (BIỂU ÂM, gợi âm chī) → cái miệng đang “xin” thức ăn. Mọi nghĩa của 吃 đều đi qua ẩn dụ NUỐT VÀO TRONG NGƯỜI.",
    branches: [
      { level: 1, title: "Nghĩa đen — ăn, đưa vào miệng", type: "literal", words: [
        { hanzi: "吃饭", pinyin: "chīfàn", hanViet: "ngật phạn", hsk: 1, meaning: "Ăn cơm / dùng bữa",
          bridge: [
            { kind: "root",      text: "吃 nuốt + 饭 cơm: hành động ăn cụ thể nhất" },
            { kind: "extension", text: "Chỉ chung việc dùng bữa, không nhất thiết là cơm" },
            { kind: "modern",    text: "吃饭了吗? — câu chào hỏi xã giao kinh điển" } ] },
        { hanzi: "吃药", pinyin: "chīyào", hanViet: "ngật dược", hsk: 2, meaning: "Uống thuốc",
          bridge: [
            { kind: "root",      text: "Thuốc viên/bột được ĐƯA VÀO MIỆNG như thức ăn" },
            { kind: "extension", text: "Tiếng Trung dùng 吃 (ăn) chứ không dùng 喝 (uống) cho thuốc" },
            { kind: "modern",    text: "按时吃药 — uống thuốc đúng giờ" } ] },
        { hanzi: "好吃", pinyin: "hǎochī", hanViet: "hảo ngật", hsk: 1, meaning: "Ngon (đồ ăn)",
          bridge: [
            { kind: "root",      text: "好 tốt + 吃 ăn: “ăn thấy tốt”" },
            { kind: "extension", text: "Mẫu 好+V = đáng để V: 好看 đẹp, 好听 hay" },
            { kind: "modern",    text: "这个菜很好吃 — món này rất ngon" } ] } ] },
      { level: 2, title: "Nghĩa chuyển — chịu đựng, hấp thụ, tiêu hao", type: "metaphor", words: [
        { hanzi: "吃苦", pinyin: "chīkǔ", hanViet: "ngật khổ", hsk: 4, meaning: "Chịu khổ, chịu đựng gian nan",
          bridge: [
            { kind: "root",      text: "“Nuốt vị đắng” 苦 — vị giác làm ẩn dụ cho trải nghiệm" },
            { kind: "extension", text: "Nuốt cái đắng = cam chịu nghịch cảnh mà không kêu ca" },
            { kind: "modern",    text: "能吃苦 — chịu khó, phẩm chất được khen trong tuyển dụng" } ] },
        { hanzi: "吃力", pinyin: "chīlì", hanViet: "ngật lực", hsk: 5, meaning: "Tốn sức, vất vả",
          bridge: [
            { kind: "root",      text: "Việc nặng “ăn” 力 sức lực của người làm" },
            { kind: "extension", text: "Chủ thể đảo: việc tiêu hao người, như máy “ăn” xăng" },
            { kind: "modern",    text: "学得很吃力 — học rất chật vật" } ] },
        { hanzi: "吃亏", pinyin: "chīkuī", hanViet: "ngật khuy", hsk: 5, meaning: "Chịu thiệt, bị thiệt thòi",
          bridge: [
            { kind: "root",      text: "亏 hao hụt — “nuốt” phần thiệt về mình" },
            { kind: "extension", text: "Thiệt hại vô hình cũng phải “nuốt xuống”" },
            { kind: "modern",    text: "吃亏是福 — chịu thiệt là phúc (tục ngữ)" } ] } ] },
      { level: 3, title: "Nghĩa bóng xa — thành ngữ & khẩu ngữ", type: "idiom", words: [
        { hanzi: "吃惊", pinyin: "chījīng", hanViet: "ngật kinh", hsk: 4, meaning: "Kinh ngạc, giật mình",
          bridge: [
            { kind: "root",      text: "“Nuốt” 惊 một cú sốc vào người" },
            { kind: "extension", text: "Cảm xúc ập đến được xử lý như vật nuốt phải" },
            { kind: "modern",    text: "大吃一惊 — giật nảy mình" } ] },
        { hanzi: "吃醋", pinyin: "chīcù", hanViet: "ngật thố", hsk: 6, meaning: "Ghen (tình cảm)",
          bridge: [
            { kind: "root",      text: "Nghĩa đen: uống giấm 醋 — chua gắt" },
            { kind: "extension", text: "Điển tích Đường Thái Tông: phu nhân tể tướng thà uống “rượu độc” (thực ra là giấm) chứ không cho chồng nạp thiếp" },
            { kind: "modern",    text: "Vị chua = cảm giác ghen; 醋坛子 “hũ giấm” = người hay ghen" } ] },
        { hanzi: "吃香", pinyin: "chīxiāng", hanViet: "ngật hương", hsk: 6, meaning: "Được ưa chuộng, đắt giá",
          bridge: [
            { kind: "root",      text: "“Ăn” được mùi thơm 香 — hưởng phần thơm ngon" },
            { kind: "extension", text: "Được hưởng ưu ái của thị trường / tập thể" },
            { kind: "modern",    text: "这个专业很吃香 — ngành này đang rất hot" } ] } ] }
    ],
    compounds: [
      { id: "chicu", hanzi: "吃醋", pinyin: "chīcù", hanViet: "ngật thố", hsk: 6,
        meaning: "Ghen — đặc biệt trong quan hệ tình cảm",
        conceptCore: "Từ vị giác (chua gắt của giấm) sang cảm xúc (ghen tuông): một trong những ẩn dụ vị giác nổi tiếng nhất tiếng Trung.",
        bridge: [
          { step: "Gốc",         text: "醋 = giấm. 吃醋 nghĩa đen là “uống giấm” — vị CHUA xộc lên mũi." },
          { step: "Chuyển nghĩa", text: "Điển tích đời Đường: vợ tể tướng Phòng Huyền Linh thà uống chén “rượu độc” vua ban (thực chất là giấm) chứ nhất quyết không cho chồng lấy thiếp. Từ đó “uống giấm” = ghen." },
          { step: "Hiện đại",     text: "Nghĩa ghen tuông chiếm trọn: 你吃醋了? “anh/em ghen đấy à?”. Nói về giấm thật, người ta tránh nói 吃醋 mà nói 放醋 (cho giấm)." } ],
        collocations: [
          { hanzi: "吃醋了", pinyin: "chīcù le", meaning: "ghen rồi (trêu chọc)" },
          { hanzi: "爱吃醋", pinyin: "ài chīcù", meaning: "hay ghen" },
          { hanzi: "醋坛子", pinyin: "cùtánzi", meaning: "“hũ giấm” — người ghen kinh niên" },
          { hanzi: "醋意", pinyin: "cùyì", meaning: "cơn ghen, ý ghen" } ],
        usageNotes: [
          "Chỉ dùng cho ghen TÌNH CẢM; ghen tị thành tích dùng 羡慕 (ngưỡng mộ) hoặc 嫉妒 (đố kỵ).",
          "Sắc thái nhẹ, thường trêu đùa; 嫉妒 nặng và tiêu cực hơn hẳn.",
          "Động tân tách được: 吃了一点醋 — “ghen một chút”." ],
        examples: [
          { hanzi: "看到她和别人聊天，他就吃醋了。", pinyin: "Kàndào tā hé biérén liáotiān, tā jiù chīcù le.", meaning: "Thấy cô ấy trò chuyện với người khác là anh ta ghen ngay." },
          { hanzi: "别吃醋，他只是我同事。", pinyin: "Bié chīcù, tā zhǐshì wǒ tóngshì.", meaning: "Đừng ghen, anh ấy chỉ là đồng nghiệp của em thôi." } ] }
    ]
  }
};

// Entry định dạng makemeahanzi cho chữ curated CHƯA có trong SAMPLE_DICT (chỉ đọc, không trộn vào DICT
// để không làm đổi ngân hàng câu hỏi của các game).
export const KB_ENTRIES = {
  "吃": { character: "吃", pinyin: ["chī"], definition: "to eat", decomposition: "⿰口乞",
          radical: "口", etymology: { type: "pictophonetic", semantic: "口", hint: "mouth", phonetic: "乞" } },
  "醋": { character: "醋", pinyin: ["cù"], definition: "vinegar", decomposition: "⿰酉昔",
          radical: "酉", etymology: { type: "pictophonetic", semantic: "酉", hint: "wine", phonetic: "昔" } }
};

// pinyin bổ sung cho thành phần âm của các entry curated (không đụng PINYIN_FB của data.mjs)
export const KB_PINYIN = { "乞": "qǐ", "昔": "xī" };
