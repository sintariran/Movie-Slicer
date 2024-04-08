import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox
import os
import cv2
from PIL import Image, ImageTk

def video_to_images(video_path, output_dir, output_format, output_size, output_quality):
    # 動画ファイルを開く
    cap = cv2.VideoCapture(video_path)

    # 動画の FPS を取得
    fps = cap.get(cv2.CAP_PROP_FPS)

    # 動画の総フレーム数を取得
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    # 出力ディレクトリが存在しない場合は作成する
    os.makedirs(output_dir, exist_ok=True)

    # プログレスバーの更新
    progress_var.set(0)
    progress_bar['value'] = 0
    progress_bar.update()

    # 1秒ごとに画像を保存
    for frame_idx in range(0, total_frames, int(fps)):
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
        ret, frame = cap.read()
        if ret:
            minute = frame_idx // (int(fps) * 60)
            second = (frame_idx // int(fps)) % 60
            output_path = os.path.join(output_dir, f"{minute:02d}-{second:02d}.{output_format}")
            
            # 画像をリサイズ
            frame = cv2.resize(frame, output_size)
            
            # 画像を保存
            if output_format == "jpg":
                cv2.imwrite(output_path, frame, [cv2.IMWRITE_JPEG_QUALITY, output_quality])
            else:
                cv2.imwrite(output_path, frame)

        # プログレスバーの更新
        progress_var.set(int((frame_idx / total_frames) * 100))
        progress_bar['value'] = progress_var.get()
        progress_bar.update()

    # 動画ファイルを閉じる
    cap.release()

    # プログレスバーを100%に設定
    progress_var.set(100)
    progress_bar['value'] = 100
    progress_bar.update()

    # 完了メッセージボックスを表示
    messagebox.showinfo("完了", "動画の分割が完了しました。")

def select_video():
    global video_path
    video_path = filedialog.askopenfilename(filetypes=[("Video files", "*.mp4")])
    if video_path:
        video_path_label.config(text=os.path.basename(video_path))
        update_video_preview()

def select_output_dir():
    global output_dir
    output_dir = filedialog.askdirectory()
    if output_dir:
        output_dir_label.config(text=output_dir)

def update_video_preview():
    if video_path:
        cap = cv2.VideoCapture(video_path)
        ret, frame = cap.read()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame)
            img = img.resize((320, 180))
            photo = ImageTk.PhotoImage(img)
            video_preview.config(image=photo)
            video_preview.image = photo
        cap.release()

def start_conversion():
    if video_path and output_dir:
        output_format = output_format_var.get()
        output_size = (int(output_width_var.get()), int(output_height_var.get()))
        output_quality = int(output_quality_var.get())
        
        # ステータスバーの更新
        status_var.set("処理中...")
        status_label.update()
        
        # 動画を画像に分割
        video_to_images(video_path, output_dir, output_format, output_size, output_quality)
        
        # ステータスバーの更新
        status_var.set("待機中")
        status_label.update()
    else:
        messagebox.showerror("エラー", "動画ファイルと出力先を選択してください。")

# メインウィンドウの作成
root = tk.Tk()
root.title("動画分割アプリ")

# メニューバーの作成
menu_bar = tk.Menu(root)
root.config(menu=menu_bar)

# ファイルメニューの作成
file_menu = tk.Menu(menu_bar, tearoff=0)
file_menu.add_command(label="動画を選択", command=select_video, accelerator="Ctrl+O")
file_menu.add_command(label="出力先を選択", command=select_output_dir)
file_menu.add_separator()
file_menu.add_command(label="終了", command=root.quit)
menu_bar.add_cascade(label="ファイル", menu=file_menu)

# ヘルプメニューの作成
help_menu = tk.Menu(menu_bar, tearoff=0)
help_menu.add_command(label="使用方法", command=lambda: messagebox.showinfo("使用方法", "1. 動画ファイルを選択します。\n2. 出力先フォルダを選択します。\n3. 出力設定を調整します。\n4. 分割開始ボタンをクリックします。"))
menu_bar.add_cascade(label="ヘルプ", menu=help_menu)

# メインフレームの作成
main_frame = ttk.Frame(root, padding=10)
main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

# 動画ファイルの読み込み
video_frame = ttk.LabelFrame(main_frame, text="動画ファイル", padding=10)
video_frame.grid(row=0, column=0, padx=5, pady=5, sticky=(tk.W, tk.E, tk.N, tk.S))

video_path_label = ttk.Label(video_frame, text="動画ファイルが選択されていません")
video_path_label.grid(row=0, column=0, padx=5, pady=5, sticky=(tk.W, tk.E))

video_select_button = ttk.Button(video_frame, text="動画を選択", command=select_video)
video_select_button.grid(row=1, column=0, padx=5, pady=5, sticky=(tk.W, tk.E))

video_preview = ttk.Label(video_frame)
video_preview.grid(row=2, column=0, padx=5, pady=5)

# 出力設定
output_frame = ttk.LabelFrame(main_frame, text="出力設定", padding=10)
output_frame.grid(row=0, column=1, padx=5, pady=5, sticky=(tk.W, tk.E, tk.N, tk.S))

output_format_var = tk.StringVar(value="jpg")
output_format_label = ttk.Label(output_frame, text="出力フォーマット:")
output_format_label.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)

output_format_combo = ttk.Combobox(output_frame, textvariable=output_format_var, values=["jpg", "png"], state="readonly", width=10)
output_format_combo.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)

output_size_label = ttk.Label(output_frame, text="出力サイズ:")
output_size_label.grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)

output_width_var = tk.StringVar(value="640")
output_width_entry = ttk.Entry(output_frame, textvariable=output_width_var, width=10)
output_width_entry.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)

output_height_var = tk.StringVar(value="360")
output_height_entry = ttk.Entry(output_frame, textvariable=output_height_var, width=10)
output_height_entry.grid(row=1, column=2, padx=5, pady=5, sticky=tk.W)

output_quality_label = ttk.Label(output_frame, text="出力品質 (1-100):")
output_quality_label.grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)

output_quality_var = tk.StringVar(value="90")
output_quality_entry = ttk.Entry(output_frame, textvariable=output_quality_var, width=10)
output_quality_entry.grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)

# 出力パスの選択
output_dir_frame = ttk.LabelFrame(main_frame, text="出力先", padding=10)
output_dir_frame.grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky=(tk.W, tk.E))

output_dir_label = ttk.Label(output_dir_frame, text="出力先フォルダが選択されていません")
output_dir_label.grid(row=0, column=0, padx=5, pady=5, sticky=(tk.W, tk.E))

output_dir_button = ttk.Button(output_dir_frame, text="出力先を選択", command=select_output_dir)
output_dir_button.grid(row=0, column=1, padx=5, pady=5, sticky=(tk.W, tk.E))

# 分割開始ボタンとプログレスバー
convert_frame = ttk.Frame(main_frame)
convert_frame.grid(row=2, column=0, columnspan=2, padx=5, pady=5, sticky=(tk.W, tk.E))

convert_button = ttk.Button(convert_frame, text="分割開始", command=start_conversion)
convert_button.grid(row=0, column=0, padx=5, pady=5, sticky=(tk.W, tk.E))

progress_var = tk.IntVar(value=0)
progress_bar = ttk.Progressbar(convert_frame, variable=progress_var, maximum=100, mode='determinate')
progress_bar.grid(row=1, column=0, padx=5, pady=5, sticky=(tk.W, tk.E))

# ステータスバー
status_var = tk.StringVar(value="待機中")
status_label = ttk.Label(root, textvariable=status_var, relief=tk.SUNKEN, anchor=tk.W)
status_label.grid(row=1, column=0, padx=5, pady=5, sticky=(tk.W, tk.E))

# キーボードショートカットの設定
root.bind("<Control-o>", lambda event: select_video())

# ウィンドウサイズの設定
root.geometry("800x600")

# メインループ
root.mainloop()