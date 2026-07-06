-- ============================================================
-- SCHEMA 15 BẢNG + 2 CỘT MỞ RỘNG CHO NỘI DUNG TIẾNG TRUNG
-- FILE FINAL v6: 349 situations, pinyin + text_vi đã điền đầy đủ,
-- attitude_marker_id đã rà soát lại (dựa trên full_349_scenes.sql)
-- ============================================================

CREATE TABLE domains (id TEXT PRIMARY KEY, name TEXT NOT NULL, icon TEXT);
CREATE TABLE subdomains (id TEXT PRIMARY KEY, domain_id TEXT NOT NULL REFERENCES domains(id), name TEXT NOT NULL);
CREATE TABLE situations (id TEXT PRIMARY KEY, subdomain_id TEXT NOT NULL REFERENCES subdomains(id), name TEXT NOT NULL, description TEXT, difficulty_level TEXT);
CREATE TABLE personas (id TEXT PRIMARY KEY, name TEXT NOT NULL, age INTEGER, background TEXT, personality_traits TEXT);
CREATE TABLE attitude_markers (id TEXT PRIMARY KEY, marker TEXT NOT NULL, meaning TEXT);
CREATE TABLE dialogue_variants (
  id TEXT PRIMARY KEY,
  situation_id TEXT NOT NULL REFERENCES situations(id),
  persona_id TEXT NOT NULL REFERENCES personas(id),
  outcome_type TEXT NOT NULL,
  register_level TEXT NOT NULL,
  context_note TEXT,
  cultural_note TEXT
);
CREATE TABLE dialogue_lines (
  id TEXT PRIMARY KEY,
  variant_id TEXT NOT NULL REFERENCES dialogue_variants(id),
  speaker TEXT NOT NULL,
  order_index INTEGER NOT NULL,
  text_zh TEXT NOT NULL,
  pinyin TEXT,
  text_vi TEXT,
  attitude_marker_id TEXT REFERENCES attitude_markers(id)
);
CREATE TABLE functions (id TEXT PRIMARY KEY, group_name TEXT NOT NULL, name TEXT NOT NULL);
CREATE TABLE situation_function (situation_id TEXT NOT NULL REFERENCES situations(id), function_id TEXT NOT NULL REFERENCES functions(id), PRIMARY KEY (situation_id, function_id));
CREATE TABLE cultural_patterns (id TEXT PRIMARY KEY, pattern_name TEXT NOT NULL, description TEXT);
CREATE TABLE situation_cultural_pattern (situation_id TEXT NOT NULL REFERENCES situations(id), cultural_pattern_id TEXT NOT NULL REFERENCES cultural_patterns(id), PRIMARY KEY (situation_id, cultural_pattern_id));
CREATE TABLE grammar_points (id TEXT PRIMARY KEY, name TEXT NOT NULL, description TEXT);
CREATE TABLE situation_grammar (situation_id TEXT NOT NULL REFERENCES situations(id), grammar_id TEXT NOT NULL REFERENCES grammar_points(id), PRIMARY KEY (situation_id, grammar_id));
CREATE TABLE journeys (id TEXT PRIMARY KEY, name TEXT NOT NULL, target_persona TEXT, description TEXT);
CREATE TABLE journey_steps (id TEXT PRIMARY KEY, journey_id TEXT NOT NULL REFERENCES journeys(id), situation_id TEXT NOT NULL REFERENCES situations(id), step_order INTEGER NOT NULL);

INSERT INTO domains (id,name,icon) VALUES ('D1','Di chuyển','🚍') ON CONFLICT DO NOTHING;
INSERT INTO domains (id,name,icon) VALUES ('D2','Mua sắm','🛒') ON CONFLICT DO NOTHING;
INSERT INTO domains (id,name,icon) VALUES ('D3','Dịch vụ công','🏛') ON CONFLICT DO NOTHING;
INSERT INTO domains (id,name,icon) VALUES ('D4','Công nghệ','🌐') ON CONFLICT DO NOTHING;
INSERT INTO domains (id,name,icon) VALUES ('D5','Nhà & Sinh hoạt','🏠') ON CONFLICT DO NOTHING;
INSERT INTO domains (id,name,icon) VALUES ('D6','Tài chính','🏦') ON CONFLICT DO NOTHING;
INSERT INTO domains (id,name,icon) VALUES ('D7','Học tập','🏫') ON CONFLICT DO NOTHING;
INSERT INTO domains (id,name,icon) VALUES ('D8','Sức khỏe','🏥') ON CONFLICT DO NOTHING;
INSERT INTO domains (id,name,icon) VALUES ('D9','Cá nhân & Xã hội','👤') ON CONFLICT DO NOTHING;
INSERT INTO domains (id,name,icon) VALUES ('D10','Ăn uống','🍜') ON CONFLICT DO NOTHING;
INSERT INTO subdomains (id,domain_id,name) VALUES ('S1','D1','Trên máy bay & sân bay') ON CONFLICT DO NOTHING;
INSERT INTO subdomains (id,domain_id,name) VALUES ('S2','D1','Đặt & đi taxi/xe công nghệ') ON CONFLICT DO NOTHING;
INSERT INTO subdomains (id,domain_id,name) VALUES ('S3','D1','Giao thông công cộng') ON CONFLICT DO NOTHING;
INSERT INTO subdomains (id,domain_id,name) VALUES ('S4','D3','Nhập cảnh & hải quan') ON CONFLICT DO NOTHING;
INSERT INTO subdomains (id,domain_id,name) VALUES ('S5','D4','Viễn thông & ứng dụng') ON CONFLICT DO NOTHING;
INSERT INTO subdomains (id,domain_id,name) VALUES ('S6','D6','Đổi tiền & ngân hàng') ON CONFLICT DO NOTHING;
INSERT INTO subdomains (id,domain_id,name) VALUES ('S7','D5','Ký túc xá') ON CONFLICT DO NOTHING;
INSERT INTO subdomains (id,domain_id,name) VALUES ('S8','D7','Nhập học & hành chính trường') ON CONFLICT DO NOTHING;
INSERT INTO subdomains (id,domain_id,name) VALUES ('S9','D7','Học vụ & thư viện') ON CONFLICT DO NOTHING;
INSERT INTO subdomains (id,domain_id,name) VALUES ('S10','D8','Bảo hiểm & sức khỏe') ON CONFLICT DO NOTHING;
INSERT INTO subdomains (id,domain_id,name) VALUES ('S11','D2','Siêu thị & giao hàng') ON CONFLICT DO NOTHING;
INSERT INTO subdomains (id,domain_id,name) VALUES ('S12','D10','Ăn uống') ON CONFLICT DO NOTHING;
INSERT INTO subdomains (id,domain_id,name) VALUES ('S13','D9','Đời sống & xã hội ký túc') ON CONFLICT DO NOTHING;
INSERT INTO subdomains (id,domain_id,name) VALUES ('S101','D2','Siêu thị') ON CONFLICT DO NOTHING;
INSERT INTO subdomains (id,domain_id,name) VALUES ('S102','D2','Mua đồ gia dụng') ON CONFLICT DO NOTHING;
INSERT INTO subdomains (id,domain_id,name) VALUES ('S103','D5','Giặt đồ') ON CONFLICT DO NOTHING;
INSERT INTO subdomains (id,domain_id,name) VALUES ('S104','D10','Ăn uống') ON CONFLICT DO NOTHING;
INSERT INTO subdomains (id,domain_id,name) VALUES ('S105','D5','Nhà & sinh hoạt') ON CONFLICT DO NOTHING;
INSERT INTO subdomains (id,domain_id,name) VALUES ('S106','D7','Lớp học') ON CONFLICT DO NOTHING;
INSERT INTO subdomains (id,domain_id,name) VALUES ('S107','D7','Bài tập') ON CONFLICT DO NOTHING;
INSERT INTO subdomains (id,domain_id,name) VALUES ('S108','D7','Thi cử') ON CONFLICT DO NOTHING;
INSERT INTO subdomains (id,domain_id,name) VALUES ('S109','D8','Bệnh viện') ON CONFLICT DO NOTHING;
INSERT INTO subdomains (id,domain_id,name) VALUES ('S110','D8','Nhà thuốc') ON CONFLICT DO NOTHING;
INSERT INTO subdomains (id,domain_id,name) VALUES ('S111','D9','Làm quen bạn mới') ON CONFLICT DO NOTHING;
INSERT INTO subdomains (id,domain_id,name) VALUES ('S112','D9','Quan hệ xã hội') ON CONFLICT DO NOTHING;
INSERT INTO subdomains (id,domain_id,name) VALUES ('S113','D9','Sở thích') ON CONFLICT DO NOTHING;
INSERT INTO subdomains (id,domain_id,name) VALUES ('S114','D9','Câu lạc bộ') ON CONFLICT DO NOTHING;
INSERT INTO subdomains (id,domain_id,name) VALUES ('S115','D4','Điện thoại') ON CONFLICT DO NOTHING;
INSERT INTO subdomains (id,domain_id,name) VALUES ('S116','D4','Máy tính') ON CONFLICT DO NOTHING;
INSERT INTO subdomains (id,domain_id,name) VALUES ('S117','D4','Internet') ON CONFLICT DO NOTHING;
INSERT INTO subdomains (id,domain_id,name) VALUES ('S118','D4','Ứng dụng') ON CONFLICT DO NOTHING;
INSERT INTO subdomains (id,domain_id,name) VALUES ('S119','D6','Ngân hàng') ON CONFLICT DO NOTHING;
INSERT INTO subdomains (id,domain_id,name) VALUES ('S120','D1','Xe buýt') ON CONFLICT DO NOTHING;
INSERT INTO subdomains (id,domain_id,name) VALUES ('S121','D1','Tàu điện') ON CONFLICT DO NOTHING;
INSERT INTO subdomains (id,domain_id,name) VALUES ('S122','D1','Xe đạp công cộng') ON CONFLICT DO NOTHING;
INSERT INTO subdomains (id,domain_id,name) VALUES ('S123','D1','Thuê xe') ON CONFLICT DO NOTHING;
INSERT INTO subdomains (id,domain_id,name) VALUES ('S124','D1','Tàu cao tốc') ON CONFLICT DO NOTHING;
INSERT INTO subdomains (id,domain_id,name) VALUES ('S125','D1','Taxi') ON CONFLICT DO NOTHING;
INSERT INTO subdomains (id,domain_id,name) VALUES ('S126','D3','Khẩn cấp') ON CONFLICT DO NOTHING;
INSERT INTO subdomains (id,domain_id,name) VALUES ('S127','D9','Việc làm') ON CONFLICT DO NOTHING;
INSERT INTO subdomains (id,domain_id,name) VALUES ('S128','D6','Việc làm') ON CONFLICT DO NOTHING;
INSERT INTO subdomains (id,domain_id,name) VALUES ('S129','D7','Tốt nghiệp') ON CONFLICT DO NOTHING;
INSERT INTO subdomains (id,domain_id,name) VALUES ('S130','D5','Ký túc xá') ON CONFLICT DO NOTHING;
INSERT INTO subdomains (id,domain_id,name) VALUES ('S131','D4','Viễn thông') ON CONFLICT DO NOTHING;
INSERT INTO subdomains (id,domain_id,name) VALUES ('S132','D1','Sân bay') ON CONFLICT DO NOTHING;
INSERT INTO subdomains (id,domain_id,name) VALUES ('S133','D9','Chia tay') ON CONFLICT DO NOTHING;
INSERT INTO subdomains (id,domain_id,name) VALUES ('SV1','D3','Nhập cảnh & đăng ký ban đầu') ON CONFLICT DO NOTHING;
INSERT INTO subdomains (id,domain_id,name) VALUES ('SV2','D3','Gia hạn cư trú') ON CONFLICT DO NOTHING;
INSERT INTO subdomains (id,domain_id,name) VALUES ('SV3','D3','Mất giấy tờ & cấp lại') ON CONFLICT DO NOTHING;
INSERT INTO subdomains (id,domain_id,name) VALUES ('SV4','D3','Thay đổi thông tin & chuyển trường') ON CONFLICT DO NOTHING;
INSERT INTO subdomains (id,domain_id,name) VALUES ('SV5','D3','Làm thêm & giới hạn visa') ON CONFLICT DO NOTHING;
INSERT INTO subdomains (id,domain_id,name) VALUES ('SV6','D3','Tốt nghiệp & rời khỏi TQ') ON CONFLICT DO NOTHING;
INSERT INTO subdomains (id,domain_id,name) VALUES ('SF1','D4','Ứng dụng liên lạc cơ bản') ON CONFLICT DO NOTHING;
INSERT INTO subdomains (id,domain_id,name) VALUES ('SF2','D9','Múi giờ & báo bình an') ON CONFLICT DO NOTHING;
INSERT INTO subdomains (id,domain_id,name) VALUES ('SF3','D6','Chuyển tiền & sinh hoạt phí') ON CONFLICT DO NOTHING;
INSERT INTO subdomains (id,domain_id,name) VALUES ('SF4','D9','Chia sẻ đời sống & lễ tết') ON CONFLICT DO NOTHING;
INSERT INTO subdomains (id,domain_id,name) VALUES ('SF5','D9','Tình huống khẩn cấp từ xa') ON CONFLICT DO NOTHING;
INSERT INTO subdomains (id,domain_id,name) VALUES ('SF6','D9','Kế hoạch dài hạn & chia tay') ON CONFLICT DO NOTHING;
INSERT INTO subdomains (id,domain_id,name) VALUES ('SSH1','D5','Ký túc xá & sinh hoạt phòng ở') ON CONFLICT DO NOTHING;
INSERT INTO subdomains (id,domain_id,name) VALUES ('SSH2','D10','Ăn uống trong trường') ON CONFLICT DO NOTHING;
INSERT INTO subdomains (id,domain_id,name) VALUES ('SSH3','D7','Thư viện & tự học') ON CONFLICT DO NOTHING;
INSERT INTO subdomains (id,domain_id,name) VALUES ('SSH4','D1','Di chuyển & sự vụ trong trường') ON CONFLICT DO NOTHING;
INSERT INTO subdomains (id,domain_id,name) VALUES ('SSH5','D5','Dịch vụ đời sống & giặt là') ON CONFLICT DO NOTHING;
INSERT INTO subdomains (id,domain_id,name) VALUES ('SSH6','D9','Xã hội, thể thao & sự vụ khác') ON CONFLICT DO NOTHING;
INSERT INTO subdomains (id,domain_id,name) VALUES ('SHT1','D7','Trên lớp hàng ngày') ON CONFLICT DO NOTHING;
INSERT INTO subdomains (id,domain_id,name) VALUES ('SHT2','D7','Bài tập, luận văn, viết học thuật') ON CONFLICT DO NOTHING;
INSERT INTO subdomains (id,domain_id,name) VALUES ('SHT3','D7','Thi cử, ôn tập, học lại') ON CONFLICT DO NOTHING;
INSERT INTO subdomains (id,domain_id,name) VALUES ('SHT4','D7','Hệ thống học vụ & chọn môn') ON CONFLICT DO NOTHING;
INSERT INTO subdomains (id,domain_id,name) VALUES ('SHT5','D7','Phụ đạo ngôn ngữ & hoạt động học thuật') ON CONFLICT DO NOTHING;
INSERT INTO subdomains (id,domain_id,name) VALUES ('SXH1','D9','Thể thao & văn nghệ trong trường') ON CONFLICT DO NOTHING;
INSERT INTO subdomains (id,domain_id,name) VALUES ('SXH2','D9','Tiệc tùng, quà cáp, giao tế') ON CONFLICT DO NOTHING;
INSERT INTO subdomains (id,domain_id,name) VALUES ('SXH3','D9','Giao tiếp liên văn hoá & hoá giải hiểu lầm') ON CONFLICT DO NOTHING;
INSERT INTO subdomains (id,domain_id,name) VALUES ('SXH4','D9','Cộng đồng online & hẹn gặp offline') ON CONFLICT DO NOTHING;
INSERT INTO subdomains (id,domain_id,name) VALUES ('SXH5','D9','Câu lạc bộ, học trưởng, hoạt động tập thể') ON CONFLICT DO NOTHING;
INSERT INTO subdomains (id,domain_id,name) VALUES ('SXH6','D9','Ranh giới, từ chối & duy trì tình bạn dài hạn') ON CONFLICT DO NOTHING;
INSERT INTO subdomains (id,domain_id,name) VALUES ('SKC1','D3','Tình huống khẩn cấp mở rộng') ON CONFLICT DO NOTHING;
INSERT INTO personas (id,name,age,background,personality_traits) VALUES ('P1','Nguyễn Minh (阮明)',22,'Du học sinh Việt Nam mới đến Trung Quốc, học Thương mại quốc tế','Lễ phép, hơi rón rén, tiếng Trung mức trung bình, cẩn thận') ON CONFLICT DO NOTHING;
INSERT INTO personas (id,name,age,background,personality_traits) VALUES ('P2','Lâm Vũ (林宇)',23,'Bạn cùng phòng người Trung Quốc','Nhiệt tình, thoải mái, hay giúp đỡ') ON CONFLICT DO NOTHING;
INSERT INTO attitude_markers (id,marker,meaning) VALUES ('AM01','呀','Hỏi/đáp nhẹ nhàng, giảm cảm giác cứng nhắc') ON CONFLICT DO NOTHING;
INSERT INTO attitude_markers (id,marker,meaning) VALUES ('AM02','啦','Nhẹ nhõm, vui vẻ, hoặc dứt điểm một việc') ON CONFLICT DO NOTHING;
INSERT INTO attitude_markers (id,marker,meaning) VALUES ('AM03','哦','Chỉnh/bổ sung thông tin nhẹ nhàng, không phủ định gắt') ON CONFLICT DO NOTHING;
INSERT INTO attitude_markers (id,marker,meaning) VALUES ('AM04','呢','Bổ sung/giải thích, hoặc thể hiện hơi bối rối/băn khoăn') ON CONFLICT DO NOTHING;
INSERT INTO attitude_markers (id,marker,meaning) VALUES ('AM05','啊','Hỏi lịch sự hoặc biểu lộ ngạc nhiên nhẹ') ON CONFLICT DO NOTHING;
INSERT INTO attitude_markers (id,marker,meaning) VALUES ('AM06','哈','Nhắc nhẹ, thân thiện, kéo gần khoảng cách hội thoại') ON CONFLICT DO NOTHING;
INSERT INTO attitude_markers (id,marker,meaning) VALUES ('AM07','吧','Đề nghị/xác nhận mang tính dò hỏi, không chắc chắn tuyệt đối') ON CONFLICT DO NOTHING;
INSERT INTO attitude_markers (id,marker,meaning) VALUES ('AM08','嘞','Đáp lời sảng khoái, đậm chất khẩu ngữ') ON CONFLICT DO NOTHING;
INSERT INTO attitude_markers (id,marker,meaning) VALUES ('AM09','嘛','Giọng hiển nhiên, thân mật, xoa dịu') ON CONFLICT DO NOTHING;
INSERT INTO attitude_markers (id,marker,meaning) VALUES ('AM10','哎呀','Tự trách/ngại ngùng bất ngờ') ON CONFLICT DO NOTHING;
INSERT INTO attitude_markers (id,marker,meaning) VALUES ('AM11','咯','Xác nhận nhẹ nhàng, coi như hiển nhiên/dứt khoát, giọng thân mật') ON CONFLICT DO NOTHING;
INSERT INTO attitude_markers (id,marker,meaning) VALUES ('AM12','诶','Than nhẹ, nhấn mạnh điều bất tiện/khó xử vừa nói tới') ON CONFLICT DO NOTHING;
INSERT INTO cultural_patterns (id,pattern_name,description) VALUES ('CP_A','Gọi lái xe taxi/xe công nghệ là ''thầy'' (师傅) bất kể tuổi','Cách gọi phổ biến, thể hiện sự tôn trọng, không phân biệt tuổi tác. Lặp lại ở các tình huống đi taxi/xe công nghệ.') ON CONFLICT DO NOTHING;
INSERT INTO cultural_patterns (id,pattern_name,description) VALUES ('CP_B','Ưu tiên thanh toán quét mã; mạng chậm thì chờ, không thúc ép; một số quán chỉ nhận quét mã','Thanh toán điện tử là chủ đạo ở Trung Quốc; tài xế/người bán thường kiên nhẫn chờ khách quét mã, và nhiều cửa hàng nhỏ không nhận tiền mặt.') ON CONFLICT DO NOTHING;
INSERT INTO cultural_patterns (id,pattern_name,description) VALUES ('CP_C','Ký túc xá quản lý theo quy định thống nhất, không có ngoại lệ','Giờ đóng cửa và quy định khách thăm áp dụng chung cho mọi sinh viên, kể cả sinh viên quốc tế.') ON CONFLICT DO NOTHING;
INSERT INTO cultural_patterns (id,pattern_name,description) VALUES ('CP_D','Thiết bị công cộng (đèn, máy giặt...) hỏng thì báo quản lý, không tự sửa','Trường/ký túc xá chịu trách nhiệm sửa chữa miễn phí; có thể đổi sang thiết bị khác dùng tạm trong lúc chờ.') ON CONFLICT DO NOTHING;
INSERT INTO cultural_patterns (id,pattern_name,description) VALUES ('CP_E','Thủ tục hành chính với sinh viên quốc tế cần thêm giấy xác nhận đang học','Chỉ hộ chiếu và visa thường chưa đủ để mở tài khoản ngân hàng hay làm một số thủ tục, cần bổ sung giấy xác nhận đang học.') ON CONFLICT DO NOTHING;
INSERT INTO cultural_patterns (id,pattern_name,description) VALUES ('CP_F','Thanh toán di động bắt buộc xác thực danh tính thật','Sinh viên nước ngoài dùng hộ chiếu để xác thực, không cần CMND Trung Quốc.') ON CONFLICT DO NOTHING;
INSERT INTO cultural_patterns (id,pattern_name,description) VALUES ('CP_G','Hồ sơ thiếu giấy tờ thường được cho nộp bổ sung có thời hạn','Chỉ cần thành thật xin lỗi và có kế hoạch bổ sung rõ ràng, không cần quá lo lắng.') ON CONFLICT DO NOTHING;
INSERT INTO cultural_patterns (id,pattern_name,description) VALUES ('CP_H','Biên phòng/hải quan làm việc theo nguyên tắc trung thực, ngắn gọn','Không cần giải thích dài dòng, chỉ cần trả lời đúng và đủ thông tin được hỏi.') ON CONFLICT DO NOTHING;
INSERT INTO cultural_patterns (id,pattern_name,description) VALUES ('CP_I','Đi nhầm chiều tàu điện ngầm có thể đổi chiều miễn phí ngay tại sân ga đối diện','Không cần ra cổng mua lại vé, chỉ cần sang sân ga đối diện, việc chuyển tuyến trong nhà ga là miễn phí.') ON CONFLICT DO NOTHING;
INSERT INTO cultural_patterns (id,pattern_name,description) VALUES ('CP_J','Có thể lịch sự đề nghị lái xe đổi lộ trình khi tắc đường mà không bị phụ thu thêm','Tài xế taxi/xe công nghệ thường chủ động hợp tác khi khách giải thích lý do gấp.') ON CONFLICT DO NOTHING;
INSERT INTO cultural_patterns (id,pattern_name,description) VALUES ('CP_K','Phí vận chuyển thực tế có thể cao hơn phí dự tính trên app nếu hàng quá cân','Đây là phụ thu hợp lệ theo cân nặng thật, không phải shipper tự ý tính thêm.') ON CONFLICT DO NOTHING;
INSERT INTO cultural_patterns (id,pattern_name,description) VALUES ('CP_M','Nên chủ động hỏi lại nhân viên nếu nghi ngờ thông tin vừa thay đổi (băng chuyền, cổng ra...)','Không nên tự đoán theo đám đông; thông tin sân bay có thể thay đổi tạm thời so với bảng hiển thị ban đầu.') ON CONFLICT DO NOTHING;
INSERT INTO situations (id,subdomain_id,name,description,difficulty_level) VALUES ('SIT201','S1','Điền tờ khai nhập cảnh trên máy bay','Nhờ tiếp viên hướng dẫn điền tờ khai nhập cảnh','B1') ON CONFLICT DO NOTHING;
INSERT INTO dialogue_variants (id,situation_id,persona_id,outcome_type,register_level,context_note,cultural_note) VALUES ('V201','SIT201','P1','suon_se','ban_chinh_thuc','Nhờ tiếp viên hướng dẫn điền tờ khai nhập cảnh','Tiếp viên trên máy bay giữ giọng mềm mỏng, hành khách hỏi thoải mái không cần quá rón rén.') ON CONFLICT DO NOTHING;
INSERT INTO dialogue_lines (id,variant_id,speaker,order_index,text_zh,pinyin,text_vi,attitude_marker_id) VALUES ('L201_01','V201','Nguyễn Minh',1,'乘务员您好，我不太会填这个入境登记卡，能麻烦您教教我吗？','chéng wù yuán nín hǎo， wǒ bù tài huì tián zhè ge rù jìng dēng jì kǎ， néng má fán nín jiāo jiāo wǒ ma？','Chào chị tiếp viên, em không rành cách điền tờ khai nhập cảnh này lắm, chị có thể chỉ giúp em được không ạ?',NULL) ON CONFLICT DO NOTHING;
INSERT INTO dialogue_lines (id,variant_id,speaker,order_index,text_zh,pinyin,text_vi,attitude_marker_id) VALUES ('L201_02','V201','Tiếp viên',2,'没问题呀，我来跟你说。你护照上的信息照着填就行啦。','méi wèn tí ya， wǒ lái gēn nǐ shuō。 nǐ hù zhào shàng de xìn xī zhào zhe tián jiù xíng la。','Không vấn đề gì đâu, để chị hướng dẫn em nhé. Em cứ nhìn theo thông tin trên hộ chiếu mà điền là được rồi.','AM01') ON CONFLICT DO NOTHING;
INSERT INTO dialogue_lines (id,variant_id,speaker,order_index,text_zh,pinyin,text_vi,attitude_marker_id) VALUES ('L201_03','V201','Nguyễn Minh',3,'好的，请问“来华事由”这一栏，我填“留学”就可以了吧？','hǎo de， qǐng wèn “lái huá shì yóu” zhè yī lán， wǒ tián “liú xué” jiù kě yǐ le ba？','Dạ vâng, cho em hỏi mục "lý do đến Trung Quốc" thì em điền "du học" là được đúng không ạ?','AM07') ON CONFLICT DO NOTHING;
INSERT INTO dialogue_lines (id,variant_id,speaker,order_index,text_zh,pinyin,text_vi,attitude_marker_id) VALUES ('L201_04','V201','Tiếp viên',4,'对的，完全没问题。停留时间就写你签证上的时长哦。','duì de， wán quán méi wèn tí。 tíng liú shí jiān jiù xiě nǐ qiān zhèng shàng de shí cháng ó。','Đúng rồi, hoàn toàn không sao cả. Thời gian lưu trú thì em ghi theo đúng thời hạn trên visa của em nhé.','AM03') ON CONFLICT DO NOTHING;
INSERT INTO dialogue_lines (id,variant_id,speaker,order_index,text_zh,pinyin,text_vi,attitude_marker_id) VALUES ('L201_05','V201','Nguyễn Minh',5,'那籍贯和出生地，直接填越南可以吗？','nà jí guàn hé chū shēng dì， zhí jiē tián yuè nán kě yǐ ma？','Vậy còn mục quê quán với nơi sinh, em điền thẳng là Việt Nam được không ạ?',NULL) ON CONFLICT DO NOTHING;
INSERT INTO dialogue_lines (id,variant_id,speaker,order_index,text_zh,pinyin,text_vi,attitude_marker_id) VALUES ('L201_06','V201','Tiếp viên',6,'可以的，不用写太详细，简洁填写就好啦。','kě yǐ de， bù yòng xiě tài xiáng xì， jiǎn jié tián xiě jiù hǎo la。','Được chứ, không cần ghi chi tiết quá đâu, em cứ điền ngắn gọn là ổn rồi.','AM02') ON CONFLICT DO NOTHING;
INSERT INTO dialogue_lines (id,variant_id,speaker,order_index,text_zh,pinyin,text_vi,attitude_marker_id) VALUES ('L201_07','V201','Nguyễn Minh',7,'太谢谢您了，帮了我大忙！','tài xiè xiè nín le， bāng le wǒ dà máng！','Em cảm ơn chị nhiều lắm ạ, chị giúp em một việc lớn đó!',NULL) ON CONFLICT DO NOTHING;
INSERT INTO dialogue_lines (id,variant_id,speaker,order_index,text_zh,pinyin,text_vi,attitude_marker_id) VALUES ('L201_08','V201','Tiếp viên',8,'不客气哈，有不懂的随时再问我。','bú kè qì hā， yǒu bù dǒng de suí shí zài wèn wǒ。','Không có gì đâu, có gì chưa hiểu cứ hỏi lại chị bất cứ lúc nào nhé.','AM06') ON CONFLICT DO NOTHING;
INSERT INTO situations (id,subdomain_id,name,description,difficulty_level) VALUES ('SIT202','S1','Hỏi lối ra sân bay','Hỏi hướng ra sân bay sau khi hạ cánh, được chỉ dẫn rõ ràng','B1') ON CONFLICT DO NOTHING;
INSERT INTO dialogue_variants (id,situation_id,persona_id,outcome_type,register_level,context_note,cultural_note) VALUES ('V202','SIT202','P1','suon_se','ban_chinh_thuc','Hỏi hướng ra sân bay sau khi hạ cánh, được chỉ dẫn rõ ràng','Nhân viên sân bay chỉ đường thường dùng cách nói dễ hiểu, không dùng thuật ngữ phức tạp.') ON CONFLICT DO NOTHING;
INSERT INTO dialogue_lines (id,variant_id,speaker,order_index,text_zh,pinyin,text_vi,attitude_marker_id) VALUES ('L202_01','V202','Nguyễn Minh',1,'您好，麻烦问一下，机场出口是往这边走吗？','nín hǎo， má fán wèn yī xià， jī chǎng chū kǒu shì wǎng zhè biān zǒu ma？','Chào anh/chị, cho tôi hỏi lối ra sân bay là đi hướng này phải không ạ?',NULL) ON CONFLICT DO NOTHING;
INSERT INTO dialogue_lines (id,variant_id,speaker,order_index,text_zh,pinyin,text_vi,attitude_marker_id) VALUES ('L202_02','V202','Nhân viên',2,'不是哦，这边是转机通道，出口在你的左手边呢。','bú shì ó， zhè biān shì zhuǎn jī tōng dào， chū kǒu zài nǐ de zuǒ shǒu biān ne。','Không phải đâu ạ, bên này là lối đi nối chuyến, cửa ra nằm ở phía tay trái của anh/chị đó.','AM03') ON CONFLICT DO NOTHING;
INSERT INTO dialogue_lines (id,variant_id,speaker,order_index,text_zh,pinyin,text_vi,attitude_marker_id) VALUES ('L202_03','V202','Nguyễn Minh',3,'左手边是吗？一直直走就到了吧？','zuǒ shǒu biān shì ma？ yì zhí zhí zǒu jiù dào le ba？','Bên tay trái đúng không ạ? Cứ đi thẳng là tới phải không?','AM07') ON CONFLICT DO NOTHING;
INSERT INTO dialogue_lines (id,variant_id,speaker,order_index,text_zh,pinyin,text_vi,attitude_marker_id) VALUES ('L202_04','V202','Nhân viên',4,'对的，直走到底左转，跟着“国内到达”的牌子走就行啦。','duì de， zhí zǒu dào dǐ zuǒ zhuǎn， gēn zhe “guó nèi dào dá” de pái zi zǒu jiù xíng la。','Đúng vậy, đi thẳng đến cuối rồi rẽ trái, cứ đi theo biển "đến trong nước" là được ạ.','AM02') ON CONFLICT DO NOTHING;
INSERT INTO dialogue_lines (id,variant_id,speaker,order_index,text_zh,pinyin,text_vi,attitude_marker_id) VALUES ('L202_05','V202','Nguyễn Minh',5,'好的，我明白了，谢谢您！','hǎo de， wǒ míng bái le， xiè xiè nín！','Dạ vâng, tôi hiểu rồi, cảm ơn anh/chị nhé!',NULL) ON CONFLICT DO NOTHING;
INSERT INTO dialogue_lines (id,variant_id,speaker,order_index,text_zh,pinyin,text_vi,attitude_marker_id) VALUES ('L202_06','V202','Nhân viên',6,'没事的，慢走哈！','méi shì de， màn zǒu hā！','Không có gì đâu ạ, đi cẩn thận nhé!','AM06') ON CONFLICT DO NOTHING;
INSERT INTO situations (id,subdomain_id,name,description,difficulty_level) VALUES ('SIT203','S1','Hỏi băng chuyền nhận hành lý','Băng chuyền bị đổi tạm thời so với thông tin ban đầu','B1') ON CONFLICT DO NOTHING;
INSERT INTO dialogue_variants (id,situation_id,persona_id,outcome_type,register_level,context_note,cultural_note) VALUES ('V203','SIT203','P1','twist','chinh_thuc','Băng chuyền bị đổi tạm thời so với thông tin ban đầu',NULL) ON CONFLICT DO NOTHING;
INSERT INTO dialogue_lines (id,variant_id,speaker,order_index,text_zh,pinyin,text_vi,attitude_marker_id) VALUES ('L203_01','V203','Nguyễn Minh',1,'您好，我想请问一下，国际航班的行李在哪里领取啊？','nín hǎo， wǒ xiǎng qǐng wèn yī xià， guó jì háng bān de xíng lǐ zài nǎ lǐ lǐng qǔ a？','Chào anh/chị, cho tôi hỏi hành lý của chuyến bay quốc tế lấy ở đâu vậy ạ?','AM05') ON CONFLICT DO NOTHING;
INSERT INTO dialogue_lines (id,variant_id,speaker,order_index,text_zh,pinyin,text_vi,attitude_marker_id) VALUES ('L203_02','V203','Nhân viên',2,'您好，请问你的航班号是多少呢？','nín hǎo， qǐng wèn nǐ de háng bān hào shì duō shǎo ne？','Chào anh/chị, xin hỏi số hiệu chuyến bay của anh/chị là gì ạ?','AM04') ON CONFLICT DO NOTHING;
INSERT INTO dialogue_lines (id,variant_id,speaker,order_index,text_zh,pinyin,text_vi,attitude_marker_id) VALUES ('L203_03','V203','Nguyễn Minh',3,'是VN520航班，麻烦您查一下。','shì VN520 háng bān， má fán nín chá yī xià。','Là chuyến VN520, phiền anh/chị kiểm tra giúp tôi với.',NULL) ON CONFLICT DO NOTHING;
INSERT INTO dialogue_lines (id,variant_id,speaker,order_index,text_zh,pinyin,text_vi,attitude_marker_id) VALUES ('L203_04','V203','Nhân viên',4,'稍等，这班航班原本在3号转盘，刚刚临时调整到5号转盘了哦。','shāo děng， zhè bān háng bān yuán běn zài 3 hào zhuàn pán， gāng gāng lín shí diào zhěng dào 5 hào zhuàn pán le ó。','Anh/chị chờ chút, chuyến này ban đầu ở băng chuyền số 3, nhưng vừa mới tạm thời chuyển sang băng chuyền số 5 rồi ạ.','AM03') ON CONFLICT DO NOTHING;
INSERT INTO dialogue_lines (id,variant_id,speaker,order_index,text_zh,pinyin,text_vi,attitude_marker_id) VALUES ('L203_05','V203','Nguyễn Minh',5,'原来是这样，还好我问了，不然就走错啦。','yuán lái shì zhè yàng， hái hǎo wǒ wèn le， bù rán jiù zǒu cuò la。','Thì ra là vậy, may mà tôi hỏi, không thì đã đi nhầm rồi.','AM02') ON CONFLICT DO NOTHING;
INSERT INTO dialogue_lines (id,variant_id,speaker,order_index,text_zh,pinyin,text_vi,attitude_marker_id) VALUES ('L203_06','V203','Nhân viên',6,'是的，近期偶尔会调整，你直接去5号转盘等候就行。','shì de， jìn qī ǒu ěr huì tiáo zhěng， nǐ zhí jiē qù 5 hào zhuàn pán děng hòu jiù xíng。','Vâng, gần đây thỉnh thoảng có điều chỉnh, anh/chị cứ đến thẳng băng chuyền số 5 chờ là được ạ.',NULL) ON CONFLICT DO NOTHING;
INSERT INTO dialogue_lines (id,variant_id,speaker,order_index,text_zh,pinyin,text_vi,attitude_marker_id) VALUES ('L203_07','V203','Nguyễn Minh',7,'好的，非常感谢您！','hǎo de， fēi cháng gǎn xiè nín！','Vâng, cảm ơn anh/chị rất nhiều!',NULL) ON CONFLICT DO NOTHING;
INSERT INTO situations (id,subdomain_id,name,description,difficulty_level) VALUES ('SIT204','S5','Mua SIM và tư vấn gói cước','Chọn gói data phù hợp, hệ thống cửa hàng chậm phải chờ kích hoạt','B2') ON CONFLICT DO NOTHING;
INSERT INTO dialogue_variants (id,situation_id,persona_id,outcome_type,register_level,context_note,cultural_note) VALUES ('V204','SIT204','P1','twist','tuy_y','Chọn gói data phù hợp, hệ thống cửa hàng chậm phải chờ kích hoạt',NULL) ON CONFLICT DO NOTHING;
INSERT INTO dialogue_lines (id,variant_id,speaker,order_index,text_zh,pinyin,text_vi,attitude_marker_id) VALUES ('L204_01','V204','Nguyễn Minh',1,'你好，我是留学生，想办一张流量多的电话卡，有合适的套餐吗？','nǐ hǎo， wǒ shì liú xué shēng， xiǎng bàn yī zhāng liú liàng duō de diàn huà kǎ， yǒu hé shì de tào cān ma？','Chào bạn, mình là du học sinh, muốn đăng ký một cái sim có nhiều data một chút, có gói nào phù hợp không?',NULL) ON CONFLICT DO NOTHING;
INSERT INTO dialogue_lines (id,variant_id,speaker,order_index,text_zh,pinyin,text_vi,attitude_marker_id) VALUES ('L204_02','V204','Nhân viên',2,'有的呀，这款学生套餐性价比超高，每月超多流量呢。','yǒu de ya， zhè kuǎn xué shēng tào cān xìng jià bǐ chāo gāo， měi yuè chāo duō liú liàng ne。','Có chứ ạ, gói dành cho sinh viên này giá trị lắm luôn, mỗi tháng data siêu nhiều đó.','AM01') ON CONFLICT DO NOTHING;
INSERT INTO dialogue_lines (id,variant_id,speaker,order_index,text_zh,pinyin,text_vi,attitude_marker_id) VALUES ('L204_03','V204','Nguyễn Minh',3,'那这个套餐可以直接当场激活吧？','nà zhè ge tào cān kě yǐ zhí jiē dāng chǎng jī huó ba？','Vậy gói này có thể kích hoạt luôn tại chỗ được không?','AM07') ON CONFLICT DO NOTHING;
INSERT INTO dialogue_lines (id,variant_id,speaker,order_index,text_zh,pinyin,text_vi,attitude_marker_id) VALUES ('L204_04','V204','Nhân viên',4,'本来可以的，不过今天系统有点卡，需要等两分钟哦。','běn lái kě yǐ de， bù guò jīn tiān xì tǒng yǒu diǎn kǎ， xū yào děng liǎng fēn zhōng ó。','Bình thường thì được đó, nhưng hôm nay hệ thống hơi bị đơ, phải đợi khoảng hai phút nha.','AM03') ON CONFLICT DO NOTHING;
INSERT INTO dialogue_lines (id,variant_id,speaker,order_index,text_zh,pinyin,text_vi,attitude_marker_id) VALUES ('L204_05','V204','Nguyễn Minh',5,'没事的，我可以等，麻烦你啦。','méi shì de， wǒ kě yǐ děng， má fán nǐ la。','Không sao đâu, mình đợi được, phiền bạn giúp nhé.','AM02') ON CONFLICT DO NOTHING;
INSERT INTO dialogue_lines (id,variant_id,speaker,order_index,text_zh,pinyin,text_vi,attitude_marker_id) VALUES ('L204_06','V204','Nhân viên',6,'不麻烦！马上就好，激活后我帮你调好网络设置哈。','bù má fán！ mǎ shàng jiù hǎo， jī huó hòu wǒ bāng nǐ diào hǎo wǎng luò shè zhì hā。','Không phiền đâu! Xong ngay thôi, kích hoạt xong mình chỉnh luôn cài đặt mạng cho bạn nha.','AM06') ON CONFLICT DO NOTHING;
INSERT INTO dialogue_lines (id,variant_id,speaker,order_index,text_zh,pinyin,text_vi,attitude_marker_id) VALUES ('L204_07','V204','Nguyễn Minh',7,'太好了，谢谢你！','tài hǎo le， xiè xiè nǐ！','Tuyệt quá, cảm ơn bạn nhiều nha!',NULL) ON CONFLICT DO NOTHING;
INSERT INTO situations (id,subdomain_id,name,description,difficulty_level) VALUES ('SIT205','S4','Trả lời biên phòng khi nhập cảnh','Trình bày mục đích, trường học, chuyên ngành, thời gian học, nguồn tài trợ','B2') ON CONFLICT DO NOTHING;
INSERT INTO dialogue_variants (id,situation_id,persona_id,outcome_type,register_level,context_note,cultural_note) VALUES ('V205','SIT205','P1','suon_se','chinh_thuc','Trình bày mục đích, trường học, chuyên ngành, thời gian học, nguồn tài trợ',NULL) ON CONFLICT DO NOTHING;
INSERT INTO dialogue_lines (id,variant_id,speaker,order_index,text_zh,pinyin,text_vi,attitude_marker_id) VALUES ('L205_01','V205','Biên phòng',1,'你好，出示一下护照和签证。来华目的是什么？','nǐ hǎo， chū shì yī xià hù zhào hé qiān zhèng。 lái huá mù dì shì shén me？','Xin chào, xuất trình hộ chiếu và visa. Mục đích đến Trung Quốc là gì?',NULL) ON CONFLICT DO NOTHING;
INSERT INTO dialogue_lines (id,variant_id,speaker,order_index,text_zh,pinyin,text_vi,attitude_marker_id) VALUES ('L205_02','V205','Nguyễn Minh',2,'您好，我来中国留学的。','nín hǎo， wǒ lái zhōng guó liú xué de。','Chào anh/chị, tôi đến Trung Quốc để du học ạ.',NULL) ON CONFLICT DO NOTHING;
INSERT INTO dialogue_lines (id,variant_id,speaker,order_index,text_zh,pinyin,text_vi,attitude_marker_id) VALUES ('L205_03','V205','Biên phòng',3,'在哪所学校就读？什么专业？','zài nǎ suǒ xué xiào jiù dú？ shén me zhuān yè？','Anh/chị học ở trường nào? Chuyên ngành gì?',NULL) ON CONFLICT DO NOTHING;
INSERT INTO dialogue_lines (id,variant_id,speaker,order_index,text_zh,pinyin,text_vi,attitude_marker_id) VALUES ('L205_04','V205','Nguyễn Minh',4,'我在省城理工大学，就读国际贸易专业。','wǒ zài shěng chéng lǐ gōng dà xué， jiù dú guó jì mào yì zhuān yè。','Tôi học tại Đại học Bách khoa tỉnh, chuyên ngành Thương mại quốc tế.',NULL) ON CONFLICT DO NOTHING;
INSERT INTO dialogue_lines (id,variant_id,speaker,order_index,text_zh,pinyin,text_vi,attitude_marker_id) VALUES ('L205_05','V205','Biên phòng',5,'学习时长多久？资金来源是哪里？','xué xí shí cháng duō jiǔ？ zī jīn lái yuán shì nǎ lǐ？','Thời gian học là bao lâu? Nguồn tài chính từ đâu?',NULL) ON CONFLICT DO NOTHING;
INSERT INTO dialogue_lines (id,variant_id,speaker,order_index,text_zh,pinyin,text_vi,attitude_marker_id) VALUES ('L205_06','V205','Nguyễn Minh',6,'我学习四年，学费和生活费由家里提供。','wǒ xué xí sì nián， xué fèi hé shēng huó fèi yóu jiā lǐ tí gōng。','Tôi học bốn năm, học phí và sinh hoạt phí do gia đình chu cấp.',NULL) ON CONFLICT DO NOTHING;
INSERT INTO dialogue_lines (id,variant_id,speaker,order_index,text_zh,pinyin,text_vi,attitude_marker_id) VALUES ('L205_07','V205','Biên phòng',7,'好的，信息核对无误，入境通过。','hǎo de， xìn xī hé duì wú wù， rù jìng tōng guò。','Được rồi, thông tin đối chiếu chính xác, anh/chị được phép nhập cảnh.',NULL) ON CONFLICT DO NOTHING;
INSERT INTO dialogue_lines (id,variant_id,speaker,order_index,text_zh,pinyin,text_vi,attitude_marker_id) VALUES ('L205_08','V205','Nguyễn Minh',8,'谢谢工作人员！','xiè xiè gōng zuò rén yuán！','Cảm ơn cán bộ đã hỗ trợ ạ!',NULL) ON CONFLICT DO NOTHING;
INSERT INTO situations (id,subdomain_id,name,description,difficulty_level) VALUES ('SIT206','S4','Xin biên phòng nói chậm/lặp lại','Nghe không rõ câu hỏi, xin lỗi và đề nghị nói chậm hơn','B1') ON CONFLICT DO NOTHING;
INSERT INTO dialogue_variants (id,situation_id,persona_id,outcome_type,register_level,context_note,cultural_note) VALUES ('V206','SIT206','P1','suon_se','chinh_thuc','Nghe không rõ câu hỏi, xin lỗi và đề nghị nói chậm hơn',NULL) ON CONFLICT DO NOTHING;
INSERT INTO dialogue_lines (id,variant_id,speaker,order_index,text_zh,pinyin,text_vi,attitude_marker_id) VALUES ('L206_01','V206','Biên phòng',1,'你本次入境是否携带校外兼职相关材料？','nǐ běn cì rù jìng shì fǒu xié dài xiào wài jiān zhí xiāng guān cái liào？','Lần nhập cảnh này anh/chị có mang theo giấy tờ liên quan đến việc làm thêm ngoài trường không?',NULL) ON CONFLICT DO NOTHING;
