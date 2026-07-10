# -*- coding: utf-8 -*-
"""Phân tích PASSAGE đầy đủ (6 đoạn, 24 câu) — bài Zoo conservation programmes (C1T1)."""
from docx import Document
from docx.shared import Pt, Twips
from docx.enum.section import WD_ORIENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

FONT = "Cambria"
TABLE_PT = 9.0
MIN_PT = 5.5
DXA_PER_CHAR = 125
MIN_COL = 700
PAGE_W = 16838
MARGIN = 500
USABLE = PAGE_W - 2 * MARGIN

BOLD_TOKENS = {
    "S", "TT", "TGT", "BC", "DV", "Trạng ngữ", "Tính ngữ", "MĐC", "MĐP", "MĐQH", "MĐDT",
    "CNTT", "Conj", "Conjp", "Aux", "Advpđ", "ĐX", "Vlet",
    "Vi", "Vt", "Vikr", "Vtpd", "Vt[bđ]",
}

KY_HIEU_1 = (
    "Chức năng ngữ pháp: S=Chủ ngữ ; TT=Tân trực tiếp ; TGT=Tân gián tiếp ; BC=Bổ chủ ; DV=Đồng vị ngữ ; "
    "Trạng ngữ=Adv / Adv+N[...] / Prep+N[...] ; Tính ngữ=Prep+N[...] sau danh từ ; "
    "MĐC=Mệnh đề chính ; MĐP=Mệnh đề phụ (câu phụ, do Conjp dẫn) ; MĐQH=Mệnh đề quan hệ (relative clause) ; "
    "MĐDT=Mệnh đề danh từ (noun clause, thường sau that/whether làm tân ngữ, chủ ngữ thật, hoặc bổ nghĩa danh từ) ; "
    "CNTT=Chủ ngữ thật (trong câu chủ ngữ giả “it”) ; Conj=Liên từ đẳng lập (and, but, or...) ; "
    "Conjp=Liên từ / cụm dẫn nhập phụ thuộc (because, when, if, although, as, given that...) ; "
    "Aux=Trợ động từ (will, can, may, must, should, do, have...) ; "
    "Advpđ=Trạng từ phủ định (not, never, no longer, hardly...) ; "
    "ĐX=Thành phần đệm-xen (thán từ, hô ngữ, liên từ chuyển ý: Of course, Moreover...) ; "
    "Vt=Ngoại động từ ; Vi=Nội động từ ; Vikr=Động từ nối (linking verb) ; Vt[bđ]=Ngoại động từ ở thể bị động (be + V3/V-ed)"
)

KY_HIEU_2 = (
    "Loại từ: Pro=Đại từ (nhân xưng/quan hệ/chỉ định) ; Pro (CN giả)=Đại từ chủ ngữ giả (“it” không mang nghĩa) ; "
    "PN=Danh từ riêng ; N[C,S]=Danh từ đếm được số ít ; N[C,P]=Danh từ đếm được số nhiều ; "
    "N[U]=Danh từ không đếm được ; N1N2=Danh từ kép ; Article=Mạo từ (a/an/the) ; "
    "Số từ=Số đếm ; Adjsh=Tính từ/cấu trúc sở hữu ('s, my...) ; Adjcd=Tính từ chỉ định (this/that/such) ; "
    "Adjbd=Tính từ bất định (some, several, a number of...) ; Adj=Tính từ miêu tả ; Adv=Trạng từ ; Prep=Giới từ ; "
    "Adv[N]=Danh từ chỉ thời gian dùng như trạng ngữ khi không có giới từ đứng trước (vd: Today) ; "
    "V-ing=Danh động từ / phân từ hiện tại dùng làm trạng ngữ giảm lược ; "
    "V-ed=Phân từ quá khứ dùng làm trạng ngữ giảm lược (reduced participle clause, vd: Headlined..., Given that...) ; "
    "to V=Cụm động từ nguyên mẫu có “to”"
)

def mk(num, vn, en, cols):
    return {"num": num, "vn": vn, "en": en, "cols": cols}

SENTENCES = [
mk("Đoạn 1 — Câu 1",
   "Một trong những quảng cáo gần đây của Sở thú London khiến tôi khá khó chịu, bởi nó bóp méo thực tế một cách trắng trợn đến vậy.",
   "One of London Zoo's recent advertisements caused me some irritation, so patently did it distort reality.",
   [("[One]","Pro=S"),
    ("[of London Zoo's recent advertisements],","Tính ngữ=Prep+PN+Adjsh+Adj+N[C,P]"),
    ("[caused]","Vt"),
    ("[me]","Pro=TGT"),
    ("some [irritation],","Adjbd+N[U]=TT"),
    ("[so patently]","Trạng ngữ=Adv+Adv"),
    ("[did]","Aux"),
    ("[it]","Pro=S"),
    ("[distort]","Vt"),
    ("[reality].","N[U]=TT")]),

mk("Đoạn 1 — Câu 2",
   "Với tiêu đề “Không có sở thú thì thà bảo những con vật này đi mà nhồi bông”, quảng cáo được viền bằng hình ảnh nhiều loài nguy cấp và tiếp tục tô vẽ huyền thoại rằng nếu không có những sở thú như London Zoo, các loài vật này “gần như chắc chắn sẽ biến mất mãi mãi.”",
   "Headlined \"Without zoos you might as well tell these animals to get stuffed\", it was bordered with illustrations of several endangered species and went on to extol the myth that without zoos like London Zoo these animals \"will almost certainly disappear forever.\"",
   [("[Headlined “Without zoos you might as well tell these animals to get stuffed”],","Trạng ngữ=V-ed+TT=N[U]"),
    ("[it]","Pro=S"),
    ("[was bordered]","Vt[bđ]"),
    ("[with illustrations]","Trạng ngữ=Prep+N[C,P]"),
    ("[of several endangered species]","Tính ngữ=Prep+Adjbd+Adj+N[C,P]"),
    ("[and]","Conj"),
    ("[went on]","Vi"),
    ("[to extol]","Trạng ngữ=to V"),
    ("the [myth]","Article+N[C,S]=TT"),
    ("[that without zoos like London Zoo these animals “will almost certainly disappear forever.”]","MĐDT=Conj+Trạng ngữ+S+Aux+Advpđ+Vi")]),

mk("Đoạn 1 — Câu 3",
   "Với thành tích bảo tồn khá tầm thường của các sở thú trên thế giới, người ta có thể được thông cảm nếu tỏ ra hoài nghi đôi chút về một quảng cáo như vậy.",
   "With the world's zoos rather mediocre record on conservation, one might be forgiven for being slightly skeptical about such an advertisement.",
   [("[With the world’s zoos rather mediocre record on conservation],","Trạng ngữ=Prep+Adjsh+Adv+Adj+N[C,S]+Prep+N[U]"),
    ("[one]","Pro=S"),
    ("[might]","Aux"),
    ("[be forgiven]","Vt[bđ]"),
    ("[for being slightly skeptical about such an advertisement].","Trạng ngữ=Prep+V-ing+Adv+BC=Adj+Prep+Adjcd+Article+N[C,S]")]),

mk("Đoạn 2 — Câu 4",
   "Các sở thú vốn dĩ được tạo ra như những nơi giải trí, và sự tham gia được cho là có của chúng vào công tác bảo tồn mãi đến khoảng 30 năm trước mới nghiêm túc xuất hiện, khi Hội Động vật học London tổ chức cuộc họp quốc tế chính thức đầu tiên về chủ đề này.",
   "Zoos were originally created as places of entertainment, and their suggested involvement with conservation didn't seriously arise until about 30 years ago, when the Zoological Society of London held the first formal international meeting on the subject.",
   [("[Zoos]","N[C,P]=S"),
    ("[were originally created]","Vt[bđ]"),
    ("[as places]","Trạng ngữ=Prep+N[C,P]"),
    ("[of entertainment],","Tính ngữ=Prep+N[U]"),
    ("[and]","Conj"),
    ("their suggested [involvement]","Adjsh+Adj+N[C,S]=S"),
    ("[with conservation]","Tính ngữ=Prep+N[U]"),
    ("[didn't]","Aux+Advpđ"),
    ("[seriously]","Adv"),
    ("[arise]","Vi"),
    ("[until about 30 years ago],","Trạng ngữ=Prep+Adv+Số từ+N[C,P]+Adv"),
    ("[when the Zoological Society of London held the first formal international meeting on the subject].","MĐQH=Conj+S=Article+PN+Vt+TT=Article+Adj+Adj+N[C,S]+Tính ngữ")]),

mk("Đoạn 2 — Câu 5",
   "Tám năm sau, một loạt hội nghị quốc tế đã diễn ra, mang tên “Nhân giống các loài có nguy cơ tuyệt chủng”, và kể từ thời điểm đó trở đi, bảo tồn trở thành từ khóa thời thượng của cộng đồng sở thú.",
   "Eight years later, a series of world conferences took place, entitled \"The Breeding of Endangered Species\", and from this point onwards conservation became the zoo community's buzzword.",
   [("[Eight years later],","Trạng ngữ=Số từ+N[C,P]+Adv"),
    ("a [series]","Article+N[C,S]=S"),
    ("[of world conferences]","Tính ngữ=Prep+N1N2"),
    ("[took place],","Vi"),
    ("[entitled “The Breeding of Endangered Species”],","Trạng ngữ=V-ed+TT=N[U]"),
    ("[and]","Conj"),
    ("[from this point onwards],","Trạng ngữ=Prep+Adjcd+N[C,S]+Adv"),
    ("[conservation]","N[U]=S"),
    ("[became]","Vikr"),
    ("the zoo community's [buzzword].","Article+N[C,S]+Adjsh+N[C,S]=BC")]),

mk("Đoạn 2 — Câu 6",
   "Cam kết này giờ đây đã được định nghĩa rõ ràng trong Chiến lược Bảo tồn Sở thú Thế giới (WZGS, tháng 9 năm 1993) — tài liệu mà, dù là một văn kiện quan trọng và đáng hoan nghênh, lại dường như dựa trên một sự lạc quan phi thực tế về bản chất của ngành sở thú.",
   "This commitment has now been clearly defined in The World Zoo Conservation Strategy (WZGS, September 1993), which although an important and welcome document does seem to be based on an unrealistic optimism about the nature of the zoo industry.",
   [("This [commitment]","Adjcd+N[C,S]=S"),
    ("[has]","Aux"),
    ("[now]","Adv"),
    ("[been clearly defined]","Vt[bđ]"),
    ("[in The World Zoo Conservation Strategy]","Trạng ngữ=Prep+PN"),
    ("[(WZGS, September 1993)],","DV=N[U]"),
    ("[which although an important and welcome document does seem to be based on an unrealistic optimism about the nature of the zoo industry].","MĐQH=Pro+Conjp+Article+Adj+Conj+Adj+N[C,S]+Aux+Vikr+to V+Vt[bđ]+Trạng ngữ")]),

mk("Đoạn 3 — Câu 7",
   "WZCS ước tính rằng có khoảng 10.000 sở thú trên thế giới, trong đó khoảng 1.000 sở thú tạo thành một nhóm nòng cốt gồm các bộ sưu tập chất lượng, có khả năng tham gia vào các chương trình bảo tồn phối hợp.",
   "The WZCS estimates that there are about 10,000 zoos in the world, of which around 1,000 represent a core of quality collections capable of participating in coordinated conservation programmes.",
   [("[The WZCS]","Article+PN=S"),
    ("[estimates]","Vt"),
    ("[that there are about 10,000 zoos in the world],","MĐDT=Conj+Pro (CN giả)+Vikr+Adv+Số từ+N[C,P]+Trạng ngữ"),
    ("[of which around 1,000 represent a core of quality collections capable of participating in coordinated conservation programmes].","MĐQH=Prep+Pro+Adv+Số từ+Vt+TT=Article+N[C,S]+Tính ngữ")]),

mk("Đoạn 3 — Câu 8",
   "Đây có lẽ là thiếu sót đầu tiên của tài liệu, bởi tôi cho rằng con số 10.000 là một sự đánh giá thấp nghiêm trọng so với tổng số các nơi đang đội lốt cơ sở động vật học.",
   "This is probably the document's first failing, as I believe that 10,000 is a serious underestimate of the total number of places masquerading as zoological establishments.",
   [("[This]","Pro=S"),
    ("[is]","Vikr"),
    ("[probably]","Adv"),
    ("the document's first [failing],","Article+Adjsh+Adj+N[C,S]=BC"),
    ("[as I believe that 10,000 is a serious underestimate of the total number of places masquerading as zoological establishments].","MĐP=Conjp+S=Pro+Vt+TT")]),

mk("Đoạn 3 — Câu 9",
   "Tất nhiên, việc thu thập dữ liệu chính xác là khó khăn, nhưng để đặt vấn đề vào đúng bối cảnh, tôi nhận thấy rằng chỉ trong một năm làm việc ở Đông Âu, tôi đã phát hiện ra những sở thú mới gần như mỗi tuần.",
   "Of course, it is difficult to get accurate data but, to put the issue into perspective, I have found that, in a year of working in Eastern Europe, I discover fresh zoos on almost a weekly basis.",
   [("[Of course],","ĐX"),
    ("[it]","Pro (CN giả)=S"),
    ("[is]","Vikr"),
    ("[difficult]","Adj=BC"),
    ("[to get accurate data]","CNTT=to V+TT=Adj+N[U]"),
    ("[but],","Conj"),
    ("[to put the issue into perspective],","Trạng ngữ=to V+TT=Article+N[C,S]+Trạng ngữ"),
    ("[I]","Pro=S"),
    ("[have found]","Vt"),
    ("[that, in a year of working in Eastern Europe, I discover fresh zoos on almost a weekly basis].","MĐDT=Conj+Trạng ngữ+S+Vt+TT+Trạng ngữ")]),

mk("Đoạn 4 — Câu 10",
   "Sai lầm thứ hai trong lập luận của tài liệu WZCS là niềm tin ngây thơ mà nó đặt vào 1.000 sở thú nòng cốt của mình.",
   "The second flaw in the reasoning of the WZCS document is the naive faith it places in its 1,000 core zoos.",
   [("The second [flaw]","Article+Adjcd+N[C,S]=S"),
    ("[in the reasoning]","Tính ngữ=Prep+Article+N[U]"),
    ("[of the WZCS document]","Tính ngữ=Prep+Article+PN+N[C,S]"),
    ("[is]","Vikr"),
    ("the naive [faith]","Article+Adj+N[C,S]=BC"),
    ("[it places in its 1,000 core zoos].","MĐQH=Pro+Vt+Trạng ngữ")]),

mk("Đoạn 4 — Câu 11",
   "Người ta hẳn sẽ nghĩ rằng chất lượng của các tổ chức này đã được xem xét kỹ lưỡng, nhưng có vẻ như tiêu chí để được đưa vào danh sách chọn lọc này chỉ đơn giản là sở thú đó là thành viên của một liên đoàn hay hiệp hội sở thú.",
   "One would assume that the caliber of these institutions would have been carefully examined, but it appears that the criterion for inclusion on this select list might merely be that the zoo is a member of a zoo federation or association.",
   [("[One]","Pro=S"),
    ("[would]","Aux"),
    ("[assume]","Vt"),
    ("[that the caliber of these institutions would have been carefully examined],","MĐDT=Conj+S+Aux+Vt[bđ]"),
    ("[but]","Conj"),
    ("[it]","Pro (CN giả)=S"),
    ("[appears]","Vi"),
    ("[that the criterion for inclusion on this select list might merely be that the zoo is a member of a zoo federation or association].","CNTT=Conj+S+Aux+Adv+Vikr+MĐDT")]),

mk("Đoạn 4 — Câu 12",
   "Đây có thể là một điểm khởi đầu tốt, dựa trên tiền đề rằng các thành viên phải đáp ứng những tiêu chuẩn nhất định, nhưng một lần nữa, thực tế lại không ủng hộ lý thuyết đó.",
   "This might be a good starting point, working on the premise that members must meet certain standards, but again the facts don't support the theory.",
   [("[This]","Pro=S"),
    ("[might]","Aux"),
    ("[be]","Vikr"),
    ("a good [starting point],","Article+Adj+N[C,S]=BC"),
    ("[working on the premise that members must meet certain standards],","Trạng ngữ=V-ing+Trạng ngữ+MĐDT"),
    ("[but]","Conj"),
    ("[again],","Adv"),
    ("the [facts]","Article+N[C,P]=S"),
    ("[don't]","Aux+Advpđ"),
    ("[support]","Vt"),
    ("the [theory].","Article+N[C,S]=TT")]),

mk("Đoạn 4 — Câu 13",
   "Hiệp hội các Công viên và Thủy cung Động vật học Hoa Kỳ (AAZPA) — vốn được kính trọng rộng rãi — từng có những thành viên hết sức đáng ngờ, và tại Anh, Liên đoàn các Vườn Động vật học của Vương quốc Anh và Ireland đôi khi cũng có những thành viên từng bị báo chí trong nước chỉ trích nặng nề.",
   "The greatly respected American Association of Zoological Parks and Aquariums (AAZPA) has had extremely dubious members, and in the UK the Federation of Zoological Gardens of Great Britain and Ireland has occasionally had members that have been roundly censured in the national press.",
   [("The greatly respected American [Association]","Article+Adv+Adj+Adj+PN=S"),
    ("[of Zoological Parks and Aquariums]","Tính ngữ=Prep+Adj+N[C,P]+Conj+N[C,P]"),
    ("[(AAZPA)],","DV=PN"),
    ("[has had]","Vt"),
    ("extremely dubious [members],","Adv+Adj+N[C,P]=TT"),
    ("[and]","Conj"),
    ("[in the UK],","Trạng ngữ=Prep+Article+N[C,S]"),
    ("the [Federation]","Article+PN=S"),
    ("[of Zoological Gardens of Great Britain and Ireland]","Tính ngữ=Prep+PN"),
    ("[has]","Aux"),
    ("[occasionally]","Adv"),
    ("[had]","Vt"),
    ("[members]","N[C,P]=TT"),
    ("[that have been roundly censured in the national press].","MĐQH=Pro+Aux+Vt[bđ]+Trạng ngữ")]),

mk("Đoạn 4 — Câu 14",
   "Trong số đó có Công viên Phiêu lưu Robin Hill trên đảo Wight — nơi mà nhiều người xem là bộ sưu tập động vật khét tiếng nhất cả nước.",
   "These include Robin Hill Adventure Park on the Isle of Wight, which many considered the most notorious collection of animals in the country.",
   [("[These]","Pro=S"),
    ("[include]","Vt"),
    ("[Robin Hill Adventure Park]","PN=TT"),
    ("[on the Isle of Wight],","Tính ngữ=Prep+Article+PN"),
    ("[which many considered the most notorious collection of animals in the country].","MĐQH=Pro+Adjbd+Vt+TT")]),

mk("Đoạn 4 — Câu 15",
   "Cơ sở này — vốn trong nhiều năm được hội đồng địa phương của đảo bảo vệ (hội đồng này xem nó như một tiện ích du lịch) — cuối cùng đã bị đóng cửa, sau một báo cáo lên án gay gắt của một thanh tra thú y được bổ nhiệm theo các điều khoản của Đạo luật Cấp phép Sở thú năm 1981.",
   "This establishment, which for years was protected by the Isle's local council (which viewed it as a tourist amenity), was finally closed down following a damning report by a veterinary inspector appointed under the terms of the Zoo Licensing Act 1981.",
   [("This [establishment],","Adjcd+N[C,S]=S"),
    ("[which for years was protected by the Isle’s local council (which viewed it as a tourist amenity)],","MĐQH=Pro+Trạng ngữ+Vt[bđ]+Trạng ngữ"),
    ("[was]","Aux"),
    ("[finally]","Adv"),
    ("[closed down]","Vt[bđ]"),
    ("[following a damning report by a veterinary inspector appointed under the terms of the Zoo Licensing Act 1981].","Trạng ngữ=V-ing+TT")]),

mk("Đoạn 4 — Câu 16",
   "Vì đây vốn luôn là một bộ sưu tập tai tiếng, người ta buộc phải suy ngẫm về các tiêu chuẩn mà Liên đoàn Sở thú áp dụng khi cấp tư cách thành viên.",
   "As it was always a collection of dubious repute, one is obliged to reflect upon the standards that the Zoo Federation sets when granting membership.",
   [("[As it was always a collection of dubious repute],","MĐP=Conjp+S+Vikr+Adv+BC"),
    ("[one]","Pro=S"),
    ("[is]","Vikr"),
    ("[obliged]","Adj=BC"),
    ("[to reflect upon the standards that the Zoo Federation sets when granting membership].","Trạng ngữ=to V+Trạng ngữ")]),

mk("Đoạn 4 — Câu 17",
   "Tình hình còn tệ hơn ở các nước đang phát triển, nơi có rất ít tiền dành cho việc tái phát triển, và rất khó để tìm ra cách đưa các bộ sưu tập vào kế hoạch tổng thể của WZCS.",
   "The situation is even worse in developing countries where little money is available for redevelopment and it is hard to see a way of incorporating collections into the overall scheme of the WZCS.",
   [("The [situation]","Article+N[C,S]=S"),
    ("[is]","Vikr"),
    ("[even worse]","Adv+Adj=BC"),
    ("[in developing countries where little money is available for redevelopment and it is hard to see a way of incorporating collections into the overall scheme of the WZCS].","Trạng ngữ=Prep+V-ing+N[C,P]+MĐQH")]),

mk("Đoạn 5 — Câu 18",
   "Ngay cả khi giả định rằng 1.000 sở thú nòng cốt của WZCS đều đạt tiêu chuẩn cao — có đầy đủ đội ngũ khoa học và cơ sở nghiên cứu, đội ngũ chăm sóc được đào tạo và tận tâm, chỗ ở cho phép hành vi bình thường hoặc tự nhiên, cùng một chính sách hợp tác trọn vẹn với nhau — thì tiềm năng cho công tác bảo tồn sẽ là gì?",
   "Even assuming that the WZCS's 1,000 core zoos are all of a high standard complete with scientific staff and research facilities, trained and dedicated keepers, accommodation that permits normal or natural behavior, and a policy of cooperating fully with one another, what might be the potential for conservation?",
   [("[Even assuming that the WZCS’s 1,000 core zoos are all of a high standard complete with scientific staff and research facilities, trained and dedicated keepers, accommodation that permits normal or natural behavior, and a policy of cooperating fully with one another],","Trạng ngữ=Adv+V-ing+MĐDT"),
    ("[what]","Pro=BC"),
    ("[might]","Aux"),
    ("[be]","Vikr"),
    ("the [potential]","Article+N[C,S]=S"),
    ("[for conservation]?","Tính ngữ=Prep+N[U]")]),

mk("Đoạn 5 — Câu 19",
   "Colin Tudge — tác giả cuốn Last Animals at the Zoo (Nhà xuất bản Đại học Oxford, 1992) — lập luận rằng “nếu các sở thú trên thế giới cùng hợp tác trong các chương trình nhân giống, thì ngay cả khi không mở rộng thêm, họ vẫn có thể cứu được khoảng 2.000 loài động vật có xương sống trên cạn đang nguy cấp.”",
   "Colin Tudge, author of Last Animals at the Zoo (Oxford University Press, 1992), argues that \"if the world's zoos worked together in co-operative breeding programmes, then even without further expansion they could save around 2,000 species of endangered land vertebrates.\"",
   [("[Colin Tudge],","PN=S"),
    ("[author of Last Animals at the Zoo (Oxford University Press, 1992)],","DV=N[C,S]+Tính ngữ"),
    ("[argues]","Vt"),
    ("[that “if the world’s zoos worked together in co-operative breeding programmes, then even without further expansion they could save around 2,000 species of endangered land vertebrates.”]","MĐDT=Conjp+S+Vi+Trạng ngữ+Trạng ngữ+S+Aux+Vt+TT")]),

mk("Đoạn 5 — Câu 20",
   "Điều này có vẻ là một nhận định lạc quan thái quá đến từ một người đáng lẽ phải hiểu rõ những thiếu sót và điểm yếu của ngành sở thú — người mà, khi còn là thành viên hội đồng của Sở thú London, đã từng phải thuyết phục sở thú này dành nhiều hoạt động hơn cho công tác bảo tồn.",
   "This seems an extremely optimistic proposition from a man who must be aware of the failings and weaknesses of the zoo industry, the man who, when a member of the council of London Zoo, had to persuade the zoo to devote more of its activities to conservation.",
   [("[This]","Pro=S"),
    ("[seems]","Vikr"),
    ("an extremely optimistic [proposition]","Article+Adv+Adj+N[C,S]=BC"),
    ("[from a man who must be aware of the failings and weaknesses of the zoo industry],","Tính ngữ=Prep+Article+N[C,S]+MĐQH"),
    ("[the man who, when a member of the council of London Zoo, had to persuade the zoo to devote more of its activities to conservation].","DV=Article+N[C,S]+MĐQH")]),

mk("Đoạn 5 — Câu 21",
   "Hơn nữa, đâu là những bằng chứng để ủng hộ sự lạc quan như vậy?",
   "Moreover, where are the facts to support such optimism?",
   [("[Moreover],","ĐX"),
    ("[where]","Trạng ngữ=Adv"),
    ("[are]","Vikr"),
    ("the [facts]","Article+N[C,P]=S"),
    ("[to support such optimism]?","Trạng ngữ=to V+TT=Adjcd+N[U]")]),

mk("Đoạn 6 — Câu 22",
   "Ngày nay, có thể nói khoảng 16 loài đã được “cứu” nhờ các chương trình nhân giống trong điều kiện nuôi nhốt, mặc dù một số trong đó khó có thể được xem là thành công vang dội.",
   "Today approximately 16 species might be said to have been \"saved\" by captive breeding programmes, although a number of these can hardly be looked upon as resounding successes.",
   [("[Today]","Trạng ngữ=Adv[N]"),
    ("approximately [16] species","Adv+Số từ+N[C,P]=S"),
    ("[might]","Aux"),
    ("[be said]","Vt[bđ]"),
    ("[to have been “saved”]","to V"),
    ("[by captive breeding programmes],","Trạng ngữ=Prep+Adj+V-ing+N[C,P]"),
    ("[although a number of these can hardly be looked upon as resounding successes].","MĐP=Conjp+S+Aux+Advpđ+Vt[bđ]+Trạng ngữ")]),

mk("Đoạn 6 — Câu 23",
   "Ngoài ra, khoảng 20 loài nữa đang được xem xét nghiêm túc cho các chương trình bảo tồn tại sở thú.",
   "Beyond that, about a further 20 species are being seriously considered for zoo conservation programmes.",
   [("[Beyond that],","Trạng ngữ=Prep+Pro"),
    ("about a further [20] species","Adv+Article+Adj+Số từ+N[C,P]=S"),
    ("[are being seriously considered]","Vt[bđ]"),
    ("[for zoo conservation programmes].","Trạng ngữ=Prep+N1N2+N[C,P]")]),

mk("Đoạn 6 — Câu 24",
   "Xét rằng hội nghị quốc tế tại Sở thú London đã được tổ chức cách đây 30 năm, đây là một tiến độ khá chậm, và còn cách rất xa mục tiêu 2.000 loài mà Tudge đề ra.",
   "Given that the international conference at London Zoo was held 30 years ago, this is pretty slow progress, and a long way off Tudge's target of 2,000.",
   [("[Given that the international conference at London Zoo was held 30 years ago],","MĐP=Conjp+S=Article+Adj+N[C,S]+Trạng ngữ+Vt[bđ]+Trạng ngữ"),
    ("[this]","Pro=S"),
    ("[is]","Vikr"),
    ("pretty slow [progress],","Adv+Adj+N[U]=BC"),
    ("[and]","Conj"),
    ("a long [way]","Article+Adj+N[C,S]=BC"),
    ("[off Tudge’s target]","Tính ngữ=Prep+PN+Adjsh+N[C,S]"),
    ("[of 2,000].","Tính ngữ=Prep+Số từ")]),
]


def set_run(run, size, bold=False, italic=False):
    run.font.name = FONT
    run.font.size = Pt(size)
    run.bold = bold
    run.italic = italic
    rPr = run._element.get_or_add_rPr()
    rFonts = rPr.find(qn("w:rFonts"))
    if rFonts is None:
        rFonts = OxmlElement("w:rFonts")
        rPr.append(rFonts)
    for attr in ("w:ascii", "w:hAnsi", "w:cs", "w:eastAsia"):
        rFonts.set(qn(attr), FONT)


def add_code_runs(par, code, size):
    PLACEHOLDER = "§"
    protected = code.replace("=>", PLACEHOLDER)
    runs, token = [], ""
    for ch in protected:
        if ch in "+=":
            if token:
                runs.append(("tok", token)); token = ""
            runs.append(("sep", ch))
        else:
            token += ch
    if token:
        runs.append(("tok", token))
    for kind, text in runs:
        text = text.replace(PLACEHOLDER, "=>")
        bold = kind == "tok" and text in BOLD_TOKENS
        r = par.add_run(text)
        set_run(r, size, bold=bold)


def col_width(c1, c2):
    n = max(len(c1), len(c2))
    return max(MIN_COL, n * DXA_PER_CHAR + 140)


def set_cell_width(cell, w):
    tcPr = cell._tc.get_or_add_tcPr()
    tcW = tcPr.find(qn("w:tcW"))
    if tcW is None:
        tcW = OxmlElement("w:tcW")
        tcPr.append(tcW)
    tcW.set(qn("w:w"), str(w))
    tcW.set(qn("w:type"), "dxa")


def set_table_borders(table):
    tbl = table._tbl
    tblPr = tbl.tblPr
    borders = OxmlElement("w:tblBorders")
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        el = OxmlElement(f"w:{edge}")
        el.set(qn("w:val"), "single")
        el.set(qn("w:sz"), "4")
        el.set(qn("w:color"), "000000")
        borders.append(el)
    tblPr.append(borders)
    layout = OxmlElement("w:tblLayout")
    layout.set(qn("w:type"), "fixed")
    tblPr.append(layout)


doc = Document()
sec = doc.sections[0]
sec.orientation = WD_ORIENT.LANDSCAPE
sec.page_width = Twips(PAGE_W)
sec.page_height = Twips(11906)
for m in ("left_margin", "right_margin", "top_margin", "bottom_margin"):
    setattr(sec, m, Twips(MARGIN))

h = doc.add_heading(level=1)
r = h.add_run("PASSAGE ANALYSIS — ZOO CONSERVATION PROGRAMMES (C1T1)")
set_run(r, 15, bold=True)

for block in (KY_HIEU_1, KY_HIEU_2):
    p = doc.add_paragraph()
    r = p.add_run(block)
    set_run(r, 8.5, italic=True)

max_font_used = TABLE_PT
min_font_used = TABLE_PT
overflow_sentences = []

for s in SENTENCES:
    widths = [col_width(c1, c2) for c1, c2 in s["cols"]]
    total = sum(widths)
    pt = TABLE_PT
    if total > USABLE:
        scale = USABLE / total
        pt = max(MIN_PT, TABLE_PT * scale)
        widths = [int(w * scale) for w in widths]
        total = sum(widths)
        if pt <= MIN_PT + 0.01:
            overflow_sentences.append((s["num"], len(s["cols"])))
    min_font_used = min(min_font_used, pt)

    p = doc.add_paragraph()
    r = p.add_run(s["num"])
    set_run(r, 11, bold=True)

    p = doc.add_paragraph()
    r = p.add_run(s["vn"])
    set_run(r, 10.5, italic=True)

    p = doc.add_paragraph()
    r = p.add_run(s["en"])
    set_run(r, 10.5, bold=True)

    table = doc.add_table(rows=2, cols=len(s["cols"]))
    set_table_borders(table)
    table.autofit = False
    for i, ((c1, c2), w) in enumerate(zip(s["cols"], widths)):
        cell1 = table.cell(0, i)
        cell2 = table.cell(1, i)
        set_cell_width(cell1, w)
        set_cell_width(cell2, w)
        par1 = cell1.paragraphs[0]
        par1.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = par1.add_run(c1)
        set_run(r, pt, bold=True)
        par2 = cell2.paragraphs[0]
        par2.alignment = WD_ALIGN_PARAGRAPH.CENTER
        add_code_runs(par2, c2, pt)

    doc.add_paragraph()
    print(f"{s['num']}: {len(s['cols'])} cot, tong {total} DXA (kha dung {USABLE}), font {pt:.1f}pt")

import os
out = os.environ.get("OUT", "Passage-ZooConservation-20260710.docx")
doc.save(out)
print("Saved:", out)
print("Font nho nhat dung:", round(min_font_used, 1), "pt")
print("So cau bi ep xuong san toi thieu (co the con tran):", len(overflow_sentences), overflow_sentences)
