import tkinter as tk
import os

class GPA_Calculator:
    DATA_FILE = "courses.txt"  # نام فایل ذخیره‌سازی

    def __init__(self, root):
        self.root = root
        self.root.title("محاسبه‌گر معدل")
        self.root.geometry("380x570")
        self.root.eval('tk::PlaceWindow . center')

        self.course_counter = 1
        self.course_vars = []

        # === 1. معدل در بالا ===
        gpa_frame = tk.Frame(root)
        gpa_frame.pack(pady=5)
        tk.Label(gpa_frame, text="معدل", font=("Arial", 12)).pack()
        self.gpa_label = tk.Label(gpa_frame, text="0.00", font=("Arial", 16, "bold"), fg="blue")
        self.gpa_label.pack()

        # === 2. دکمه‌های افزودن و ذخیره ===
        btn_frame = tk.Frame(root)
        btn_frame.pack(pady=5)
        tk.Button(btn_frame, text="➕ افزودن درس", command=self.add_course, bg="#4CAF50", fg="white").pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="💾 ذخیره", command=self.save_to_file, bg="#2196F3", fg="white").pack(side=tk.LEFT, padx=5)

        # === 3. فریم اسکرول‌پذیر ===
        canvas_frame = tk.Frame(root)
        canvas_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.canvas = tk.Canvas(canvas_frame)
        scrollbar = tk.Scrollbar(canvas_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # بارگذاری داده‌های قبلی (اگر وجود داشت)
        self.load_from_file()

        # اگر فایل خالی بود یا وجود نداشت، یک درس پیش‌فرض اضافه کن
        if not self.course_vars:
            self.add_course()

    def add_course(self, name="درس جدید", unit="3", grade="18"):
        """افزودن درس جدید (قابل فراخوانی با مقادیر پیش‌فرض یا بارگذاری‌شده)"""
        frame = tk.Frame(self.scrollable_frame, relief=tk.GROOVE, bd=1, padx=5, pady=5)
        frame.pack(fill=tk.X, pady=3)

        # اگر اسم پیشنهادی "درس X" باشد و از counter استفاده شود
        if name == "درس جدید":
            name = f"درس {self.course_counter}"
            self.course_counter += 1

        name_var = tk.StringVar(value=name)
        unit_var = tk.StringVar(value=str(unit))
        grade_var = tk.StringVar(value=str(grade))

        tk.Entry(frame, textvariable=name_var, width=25, font=("Arial", 10)).pack(side=tk.LEFT, padx=2)
        tk.Entry(frame, textvariable=unit_var, width=5, font=("Arial", 10)).pack(side=tk.LEFT, padx=2)
        tk.Entry(frame, textvariable=grade_var, width=5, font=("Arial", 10)).pack(side=tk.LEFT, padx=2)

        def remove():
            frame.destroy()
            self.course_vars[:] = [c for c in self.course_vars if c['frame'] != frame]
            self.update_gpa()

        tk.Button(frame, text="🗑️ حذف", command=remove, bg="#f44336", fg="white", width=9).pack(side=tk.RIGHT, padx=2)

        course_data = {
            'frame': frame,
            'name': name_var,
            'unit': unit_var,
            'grade': grade_var
        }
        self.course_vars.append(course_data)

        grade_var.trace_add("write", self.update_gpa)
        unit_var.trace_add("write", self.update_gpa)

        self.update_gpa()

    def save_to_file(self):
        """ذخیره داده‌ها در فایل متنی"""
        try:
            with open(self.DATA_FILE, "w", encoding="utf-8") as f:
                for course in self.course_vars:
                    name = course['name'].get().strip()
                    unit = course['unit'].get().strip()
                    grade = course['grade'].get().strip()
                    # ذخیره فقط اگر داده‌ها معتبر باشند
                    if name and unit and grade:
                        f.write(f"{name},{unit},{grade}\n")
            # اختیاری: نمایش پیام موفقیت
            # (می‌توانیم از messagebox استفاده کنیم اگر بخوایم)
        except Exception as e:
            print(f"خطا در ذخیره: {e}")

    def load_from_file(self):
        """بارگذاری داده‌ها از فایل (اگر وجود داشت)"""
        if not os.path.exists(self.DATA_FILE):
            return

        try:
            with open(self.DATA_FILE, "r", encoding="utf-8") as f:
                lines = f.readlines()

            if not lines:
                return

            # بازنشانی شمارنده بر اساس بیشترین شماره درس
            max_num = 0
            for line in lines:
                parts = line.strip().split(",", 2)
                if len(parts) == 3:
                    name, unit, grade = parts
                    # سعی برای استخراج شماره از "درس X"
                    if name.startswith("درس "):
                        try:
                            num = int(name.split("درس ", 1)[1])
                            if num > max_num:
                                max_num = num
                        except ValueError:
                            pass
                    self.add_course(name=name, unit=unit, grade=grade)

            self.course_counter = max_num + 1

        except Exception as e:
            print(f"خطا در بارگذاری: {e}")

    def update_gpa(self, *args):
        total_units = 0.0
        total_points = 0.0

        for course in self.course_vars:
            try:
                unit = float(course['unit'].get())
                grade = float(course['grade'].get())
                if unit < 0 or grade < 0 or grade > 20:
                    continue
                total_units += unit
                total_points += unit * grade
            except ValueError:
                continue

        gpa = total_points / total_units if total_units > 0 else 0.0
        self.gpa_label.config(text=f"{gpa:.2f}")


if __name__ == "__main__":
    root = tk.Tk()
    app = GPA_Calculator(root)
    root.mainloop()