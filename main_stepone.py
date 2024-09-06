import tkinter as tk
from dl_tsc_tsl_view import *
from dl_tsc_tsl_controller import *


if __name__ == "__main__":
    root = tk.Tk()
    stepOneView = StepOneView(root, None)

    controller = StepOneController(stepOneView)
    stepOneView.controller = controller
    stepOneView.pack()

    # Execute Tkinter
    root.mainloop()
