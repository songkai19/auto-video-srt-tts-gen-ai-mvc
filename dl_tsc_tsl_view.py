import tkinter as tk
import tkinter.ttk as ttk
from tkinter import filedialog
from threading import Thread


class StepOneView(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # Set geometry
        parent.geometry('400x450')

        # Main title
        tk.Label(self, text="Youtube Video Transcriber",
                 font="Consolas").pack(pady=10)
        tk.Label(self, text="Enter Video URL:-", font="Consolas 10").pack()

        # URL Textbox
        self.videoId = tk.Entry(self, width=50)
        self.videoId.pack(pady=10)

        # progress bar
        self.progress_var = tk.DoubleVar()
        self.pb = ttk.Progressbar(self, variable=self.progress_var,
                                  orient=tk.HORIZONTAL, length=350, mode="determinate")
        self.pb.pack(pady=5)

        # download message label
        self.saved_path_var = tk.StringVar()
        self.saved_path_var.set("-")
        self.saved_path_lbl = tk.Label(
            self, textvariable=self.saved_path_var, font="Consolas 10")
        self.saved_path_lbl.pack()

        # transcribe message label
        self.tsc_msg_var = tk.StringVar()
        self.tsc_msg_var.set("-")
        self.tsc_msg_lbl = tk.Label(
            self, textvariable=self.tsc_msg_var, font="Consolas 10")
        self.tsc_msg_lbl.pack()

        # translate message label
        self.tsl_msg_var = tk.StringVar()
        self.tsl_msg_var.set("-")
        self.tsl_msg_lbl = tk.Label(
            self, textvariable=self.tsl_msg_var, font="Consolas 10")
        self.tsl_msg_lbl.pack()

        # download button
        self.btn_dl = tk.Button(self, text="Download",
                                command=self.dl_threading)
        self.btn_dl.pack(pady=5)

        # download + transcribe button
        self.btn_plus_tsc = tk.Button(self, text="Download + Transcribe",
                                      command=self.tsc_threading)
        self.btn_plus_tsc.pack(pady=5)

        # download + transcribe + translate button
        self.btn_plus_tsl = tk.Button(self, text="Download + Transcribe + Translate",
                                      command=self.tsl_threading)
        self.btn_plus_tsl.pack(pady=5)

        # select video file to attach the translated subtitle to
        self.sel_path_lbl_var = tk.StringVar()
        self.sel_path_lbl_var.set("Selected Video File: ")
        self.lbl_s_path = tk.Label(self, textvariable=self.sel_path_lbl_var,
                                   font="Consolas 10").pack(pady=5)

        self.btn_open_file = tk.Button(self, text="Open Video",
                                       command=self.o_vf_attach)
        self.btn_open_file.pack(side= tk.LEFT, padx=70)

        # attach button
        self.btn_attach_sub = tk.Button(self, text="Attach",
                                        command=self.atc_threading).pack(side= tk.LEFT, pady=10)

    def update_btn_state(self, state):
        self.btn_dl.config(state=state)
        self.btn_plus_tsc.config(state=state)
        self.btn_plus_tsl.config(state=state)

    def update_pb_progress(self, progress):
        self.progress_var.set(progress)

    def update_lbl_msg(self, msg):
        self.saved_path_var.set(msg)

    def update_tsc_lbl_msg(self, msg):
        self.tsc_msg_var.set(msg)

    def get_tsc_lbl_msg(self):
        return self.tsc_msg_var.get()

    def update_tsl_lbl_msg(self, msg):
        self.tsl_msg_var.set(msg)

    def get_tsl_lbl_msg(self):
        return self.tsl_msg_var.get()
    
    def update_lbl_s_path(self, msg):
        self.sel_path_lbl_var.set(msg)
    
    def o_vf_attach(self):
        v_file_path = filedialog.askopenfilename(
            filetypes=[("Video files", "*.mp4"), ("All files", "*.*")])
        self.sel_path_lbl_var.set(v_file_path)

    def dl_threading(self):
        vid = self.videoId.get()
        t1 = Thread(target=self.controller.download, kwargs={"vid": vid})
        t1.start()

    def tsc_threading(self):
        vid = self.videoId.get()
        t1 = Thread(target=self.controller.dl_tsc, kwargs={"vid": vid})
        t1.start()

    def tsl_threading(self):
        vid = self.videoId.get()
        t1 = Thread(target=self.controller.dl_tsc_tsl, kwargs={"vid": vid})
        t1.start()

    def atc_threading(self):
        v_path = self.sel_path_lbl_var.get()
        t1 = Thread(target=self.controller.atc, kwargs={"v_path": v_path})
        t1.start()
