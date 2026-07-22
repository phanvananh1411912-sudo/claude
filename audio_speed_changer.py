"""
Ứng dụng Desktop: Thay đổi tốc độ & hiệu ứng giọng nói cho file âm thanh (MP3/WAV)
Yêu cầu hệ thống: đã cài đặt FFmpeg và thêm vào biến môi trường PATH.
"""

import os
import queue
import subprocess
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk


class AudioSpeedChangerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Công Cụ Đổi Tốc Độ Âm Thanh")
        self.root.geometry("560x420")
        self.root.resizable(False, False)

        # Hàng đợi dùng để luồng xử lý ffmpeg (chạy nền) gửi trạng thái về luồng giao diện chính
        self.status_queue = queue.Queue()

        # Biến lưu đường dẫn file đang chọn, liên kết trực tiếp với ô Entry
        self.file_path = tk.StringVar()
        # Biến lưu giá trị tốc độ V, mặc định 1.2x theo yêu cầu
        self.speed_var = tk.DoubleVar(value=1.2)

        self._build_ui()
        # Khởi động vòng lặp kiểm tra hàng đợi trạng thái mỗi 100ms
        self.root.after(100, self._process_queue)

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
        browse_btn = ttk.Button(file_frame, text="Duyệt...", command=self.browse_file)
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
        self.status_label.config(text="Đang chuẩn bị xử lý...", foreground="#555555")

        # Chạy FFmpeg trên một luồng (thread) riêng để không làm treo giao diện chính
        worker = threading.Thread(
            target=self._run_ffmpeg, args=(input_path, speed_v, ext), daemon=True
        )
        worker.start()

    def _run_ffmpeg(self, input_path, speed_v, ext):
        try:
            # Công thức bắt buộc: asetrate=44100*0.8 làm bài hát chậm/trầm đi 0.8 lần
            # Để bù lại và đạt tốc độ cuối cùng V, phải tính atempo = V / 0.8
            atempo_value = round(speed_v / 0.8, 4)

            # Xác định thư mục và tên file gốc để tạo đường dẫn file đầu ra
            folder = os.path.dirname(input_path)
            base_name = os.path.splitext(os.path.basename(input_path))[0]
            # File đầu ra: cùng thư mục với file gốc, thêm hậu tố "_effect_{V}x"
            output_path = os.path.join(folder, f"{base_name}_effect_{speed_v:.1f}x{ext}")

            # Chuỗi bộ lọc âm thanh ghép hai bước: hạ tần số lấy mẫu rồi bù tốc độ
            filter_str = f"asetrate=44100*0.8,atempo={atempo_value}"

            # Câu lệnh gọi FFmpeg thông qua subprocess (dạng list để tránh lỗi shell injection)
            command = [
                "ffmpeg",
                "-y",  # Tự động ghi đè nếu file đầu ra đã tồn tại
                "-i", input_path,  # Chỉ định file âm thanh đầu vào
                "-filter:a", filter_str,  # Áp dụng chuỗi bộ lọc âm thanh vừa tính toán
                output_path,  # Đường dẫn file đầu ra
            ]

            self.status_queue.put(("status", "Đang gọi FFmpeg xử lý âm thanh..."))

            # Khởi chạy tiến trình FFmpeg, gộp stderr vào stdout để đọc log tiến trình
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding="utf-8",
                errors="ignore",
            )

            # Đọc từng dòng log của FFmpeg theo thời gian thực để cập nhật trạng thái
            for line in process.stdout:
                line = line.strip()
                if "time=" in line:
                    # Trích phần "time=" trong log để biết FFmpeg đã xử lý tới đâu
                    time_part = line.split("time=")[-1].split(" ")[0]
                    self.status_queue.put(("status", f"Đang xử lý... (đã qua: {time_part})"))

            # Chờ tiến trình FFmpeg kết thúc và lấy mã thoát (return code)
            process.wait()

            # Nếu FFmpeg thoát với mã lỗi khác 0 nghĩa là xử lý thất bại
            if process.returncode != 0:
                raise RuntimeError(f"FFmpeg báo lỗi với mã thoát {process.returncode}.")

            self.status_queue.put(("success", output_path))

        except FileNotFoundError:
            # Trường hợp hệ điều hành không tìm thấy lệnh "ffmpeg" (chưa cài hoặc chưa có trong PATH)
            self.status_queue.put((
                "error",
                "Không tìm thấy FFmpeg. Vui lòng cài đặt FFmpeg và thêm vào biến môi trường PATH.",
            ))
        except Exception as exc:
            # Bắt mọi lỗi phát sinh khác (file hỏng, quyền truy cập, v.v.)
            self.status_queue.put(("error", str(exc)))

    def _process_queue(self):
        # Lấy hết các thông báo đang chờ trong hàng đợi để cập nhật giao diện
        try:
            while True:
                kind, payload = self.status_queue.get_nowait()
                if kind == "status":
                    # Cập nhật nhãn trạng thái với thông tin tiến trình hiện tại
                    self.status_label.config(text=payload, foreground="#555555")
                elif kind == "success":
                    # Xử lý thành công: bật lại nút bấm và báo kết quả cho người dùng
                    self.status_label.config(text="Hoàn tất! Đã tạo file hiệu ứng.", foreground="#27ae60")
                    self.process_btn.config(state="normal")
                    messagebox.showinfo("Thành công", f"Đã tạo file:\n{payload}")
                elif kind == "error":
                    # Xử lý thất bại: bật lại nút bấm và hiển thị hộp thoại lỗi
                    self.status_label.config(text="Đã xảy ra lỗi.", foreground="#e74c3c")
                    self.process_btn.config(state="normal")
                    messagebox.showerror("Lỗi", payload)
        except queue.Empty:
            # Hàng đợi rỗng, không có gì mới để xử lý
            pass
        finally:
            # Lặp lại việc kiểm tra hàng đợi sau mỗi 100ms để cập nhật realtime
            self.root.after(100, self._process_queue)


def main():
    # Khởi tạo cửa sổ gốc và chạy vòng lặp sự kiện của tkinter
    root = tk.Tk()
    app = AudioSpeedChangerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
