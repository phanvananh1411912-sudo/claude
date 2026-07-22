"""
Ứng dụng Desktop: Tạo hiệu ứng "giọng ma/giọng quỷ" bằng cách chồng 10 lớp trầm giọng
Yêu cầu hệ thống: đã cài đặt FFmpeg và thêm vào biến môi trường PATH.
"""

import os
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

# Tổng số vòng lặp xử lý (theo yêu cầu: đúng 10 lần)
TONG_SO_LAN = 10
# Hệ số hạ pitch dùng ở Lần 1 (đi kèm với việc đổi tốc độ theo thanh trượt)
HE_SO_PITCH_LAN_DAU = 0.8
# Hệ số hạ pitch dùng cho mỗi lần lặp từ Lần 2 đến Lần 10 (có thể tinh chỉnh để giọng
# trầm nhanh/chậm hơn qua từng lớp, miễn nằm trong khoảng ffmpeg atempo hỗ trợ tốt)
HE_SO_PITCH_MOI_LAN = 0.95


class AudioSpeedChangerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Công Cụ Đổi Tốc Độ & Chồng Hiệu Ứng Trầm Giọng")
        self.root.geometry("560x420")
        self.root.resizable(False, False)

        # Biến lưu đường dẫn file đang chọn, liên kết trực tiếp với ô Entry
        self.file_path = tk.StringVar()
        # Biến lưu giá trị tốc độ V, mặc định 1.2x theo yêu cầu
        self.speed_var = tk.DoubleVar(value=1.2)

        self._build_ui()

    def _build_ui(self):
        # Khung chứa chính, có padding đều 4 phía để giao diện thoáng và cân đối
        main_frame = ttk.Frame(self.root, padding=20)
        main_frame.pack(fill="both", expand=True)

        # Tiêu đề ứng dụng, canh giữa
        title_label = ttk.Label(
            main_frame,
            text="Công Cụ Đổi Tốc Độ & Hiệu Ứng Giọng",
            font=("Segoe UI", 14, "bold"),
            anchor="center",
        )
        title_label.pack(pady=(0, 15), fill="x")

        # ---------- Khu vực chọn file ----------
        file_frame = ttk.Frame(main_frame)
        file_frame.pack(fill="x", pady=5)

        # Nút "Duyệt..." để mở hộp thoại chọn file
        browse_btn = ttk.Button(file_frame, text="Duyệt file", command=self.browse_file)
        browse_btn.pack(side="left")

        # Ô văn bản hiển thị đường dẫn file đã chọn (chỉ đọc, không cho gõ tay)
        self.file_entry = ttk.Entry(file_frame, textvariable=self.file_path, state="readonly")
        self.file_entry.pack(side="left", fill="x", expand=True, padx=(10, 0))

        # ---------- Khu vực thanh trượt tốc độ ----------
        speed_frame = ttk.Frame(main_frame)
        speed_frame.pack(fill="x", pady=(20, 5))

        # Nhãn tiêu đề cho thanh trượt
        speed_title = ttk.Label(speed_frame, text="Tốc độ mong muốn (V):")
        speed_title.pack(anchor="w")

        # Nhãn hiển thị giá trị hiện tại của thanh trượt, cập nhật realtime khi kéo
        self.speed_value_label = ttk.Label(
            speed_frame,
            text=f"{self.speed_var.get():.1f}x",
            font=("Segoe UI", 13, "bold"),
            anchor="center",
        )
        self.speed_value_label.pack(fill="x")

        # Thanh trượt (Scale): kéo từ 0.5x đến 2.0x, mỗi nấc 0.1, giá trị mặc định 1.2x
        self.speed_scale = tk.Scale(
            speed_frame,
            from_=0.5,
            to=2.0,
            resolution=0.1,
            orient="horizontal",
            variable=self.speed_var,
            showvalue=False,  # Không dùng số hiển thị mặc định của Scale, đã có nhãn riêng ở trên
            length=460,
            command=self._on_speed_change,  # Gọi hàm cập nhật nhãn mỗi khi kéo
        )
        self.speed_scale.pack(fill="x")

        # ---------- Nút xử lý chính, to và nổi bật ----------
        self.process_btn = tk.Button(
            main_frame,
            text="TẠO HIỆU ỨNG",
            font=("Segoe UI", 13, "bold"),
            bg="#e74c3c",
            fg="white",
            activebackground="#c0392b",
            activeforeground="white",
            relief="raised",
            bd=3,
            height=2,
            cursor="hand2",
            command=self.start_processing,
        )
        self.process_btn.pack(fill="x", pady=(25, 10))

        # ---------- Nhãn trạng thái, cập nhật realtime trong quá trình xử lý ----------
        self.status_label = ttk.Label(
            main_frame, text="Sẵn sàng.", foreground="#555555", anchor="center"
        )
        self.status_label.pack(fill="x", pady=(5, 0))

    def _on_speed_change(self, value):
        # Cập nhật nhãn hiển thị số ngay khi người dùng kéo thanh trượt
        self.speed_value_label.config(text=f"{float(value):.1f}x")

    def browse_file(self):
        # Mở hộp thoại chọn file, giới hạn định dạng MP3 và WAV
        path = filedialog.askopenfilename(
            title="Chọn file âm thanh",
            filetypes=[("File âm thanh (MP3, WAV)", "*.mp3 *.wav"), ("Tất cả file", "*.*")],
        )
        if path:
            # Ghi đường dẫn vào ô Entry thông qua biến StringVar
            self.file_path.set(path)
            self.status_label.config(text="Đã chọn file. Sẵn sàng xử lý.", foreground="#555555")

    def _cap_nhat_trang_thai(self, text, color="#555555"):
        # Cập nhật nhãn trạng thái rồi ép tkinter vẽ lại ngay lập tức,
        # tránh để cửa sổ bị coi là "không phản hồi" trong lúc xử lý dài
        self.status_label.config(text=text, foreground=color)
        self.root.update()

    def _goi_ffmpeg(self, input_path, output_path, filter_str):
        # Câu lệnh gọi FFmpeg thông qua subprocess (dạng list để tránh lỗi shell injection)
        command = [
            "ffmpeg",
            "-y",  # Tự động ghi đè nếu file đầu ra đã tồn tại
            "-i", input_path,  # File âm thanh đầu vào của bước này
            "-filter:a", filter_str,  # Bộ lọc âm thanh áp dụng cho bước này
            output_path,  # File âm thanh đầu ra của bước này
        ]
        # Chạy ffmpeg và đợi hoàn tất; gộp log lỗi vào stdout để không làm rối terminal
        result = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )
        if result.returncode != 0:
            raise RuntimeError(f"FFmpeg báo lỗi với mã thoát {result.returncode}.")

    def start_processing(self):
        input_path = self.file_path.get()

        # Kiểm tra: người dùng đã chọn file chưa
        if not input_path:
            messagebox.showerror("Lỗi", "Vui lòng chọn một file MP3 hoặc WAV trước khi xử lý.")
            return

        # Kiểm tra: file có thực sự tồn tại trên ổ đĩa không
        if not os.path.isfile(input_path):
            messagebox.showerror("Lỗi", "File đã chọn không tồn tại hoặc đã bị di chuyển/xóa.")
            return

        # Kiểm tra: đúng định dạng đuôi file được hỗ trợ (mp3 hoặc wav)
        ext = os.path.splitext(input_path)[1].lower()
        if ext not in (".mp3", ".wav"):
            messagebox.showerror("Lỗi", "Chỉ hỗ trợ định dạng file MP3 hoặc WAV.")
            return

        # Lấy giá trị V từ thanh trượt, làm tròn 1 chữ số thập phân cho gọn
        speed_v = round(self.speed_var.get(), 1)

        # Vô hiệu hóa nút bấm trong lúc xử lý để tránh người dùng bấm nhiều lần
        self.process_btn.config(state="disabled")

        # Danh sách lưu đường dẫn các file tạm đã tạo ra, dùng để dọn dẹp sau này
        file_tam_list = []
        try:
            folder = os.path.dirname(input_path)
            base_name = os.path.splitext(os.path.basename(input_path))[0]

            current_input = input_path  # Đầu vào của vòng lặp hiện tại

            # Vòng lặp for chạy đúng 10 lần, mỗi lần dùng đầu ra của lần trước làm đầu vào
            for lan in range(1, TONG_SO_LAN + 1):
                self._cap_nhat_trang_thai(f"Đang xử lý lần {lan}/{TONG_SO_LAN}...")

                file_tam = os.path.join(folder, f"{base_name}_file_tam_{lan}{ext}")

                if lan == 1:
                    # Lần 1: áp dụng ĐỒNG THỜI đổi tốc độ (theo V) và hạ pitch lần đầu
                    # asetrate=44100*0.8 làm pitch trầm xuống nhưng cũng làm chậm đi 0.8 lần
                    # -> phải bù atempo = V / 0.8 để tốc độ cuối cùng đúng bằng V
                    atempo_bu_toc_do = round(speed_v / HE_SO_PITCH_LAN_DAU, 4)
                    filter_str = f"asetrate=44100*{HE_SO_PITCH_LAN_DAU},atempo={atempo_bu_toc_do}"
                else:
                    # Lần 2 -> 10: CHỈ hạ thêm pitch, tuyệt đối không đổi tốc độ nữa
                    # Vì asetrate luôn kéo theo thay đổi tốc độ, phải bù atempo = 1 / hệ_số_pitch
                    # để triệt tiêu phần chậm/nhanh sinh ra, giữ nguyên tốc độ đã đạt ở Lần 1
                    atempo_bu_toc_do = round(1 / HE_SO_PITCH_MOI_LAN, 4)
                    filter_str = f"asetrate=44100*{HE_SO_PITCH_MOI_LAN},atempo={atempo_bu_toc_do}"

                # Gọi FFmpeg xử lý bước này: đầu vào là kết quả bước trước, đầu ra là file tạm mới
                self._goi_ffmpeg(current_input, file_tam, filter_str)

                file_tam_list.append(file_tam)
                current_input = file_tam  # File tạm vừa tạo sẽ là đầu vào cho lần lặp kế tiếp

            # ---------- Dọn dẹp: đổi tên file tạm cuối cùng thành file kết quả ----------
            self._cap_nhat_trang_thai("Đang hoàn tất và dọn dẹp file tạm...")

            final_output = os.path.join(folder, f"{base_name}_10x_Lower{ext}")
            # Đổi tên file_tam_10 thành file thành phẩm cuối cùng
            os.replace(file_tam_list[-1], final_output)

            # Xóa sạch các file trung gian từ file_tam_1 đến file_tam_9
            for file_thua in file_tam_list[:-1]:
                os.remove(file_thua)

            self._cap_nhat_trang_thai("Hoàn tất! Đã tạo file hiệu ứng.", "#27ae60")
            messagebox.showinfo("Thành công", f"Đã tạo file:\n{final_output}")

        except FileNotFoundError:
            # Trường hợp hệ điều hành không tìm thấy lệnh "ffmpeg" (chưa cài hoặc chưa có trong PATH)
            self._cap_nhat_trang_thai("Đã xảy ra lỗi.", "#e74c3c")
            messagebox.showerror(
                "Lỗi", "Không tìm thấy FFmpeg. Vui lòng cài đặt FFmpeg và thêm vào biến môi trường PATH."
            )
        except Exception as exc:
            # Bắt mọi lỗi phát sinh khác (file hỏng, quyền truy cập, v.v.)
            self._cap_nhat_trang_thai("Đã xảy ra lỗi.", "#e74c3c")
            messagebox.showerror("Lỗi", str(exc))
            # Cố gắng dọn rác các file tạm đã lỡ tạo ra trước khi lỗi xảy ra
            for file_thua in file_tam_list:
                try:
                    if os.path.isfile(file_thua):
                        os.remove(file_thua)
                except OSError:
                    pass
        finally:
            # Luôn bật lại nút bấm dù thành công hay thất bại
            self.process_btn.config(state="normal")


def main():
    # Khởi tạo cửa sổ gốc và chạy vòng lặp sự kiện của tkinter
    root = tk.Tk()
    app = AudioSpeedChangerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
