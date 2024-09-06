import tkinter as tk

# Model


class CalculatorModel:
    def __init__(self):
        self.result = 0

    def add(self, num1, num2):
        self.result = num1 + num2

    def subtract(self, num1, num2):
        self.result = num1 - num2

# View


class CalculatorView(tk.Frame):
    def __init__(self, master, controller):
        super().__init__(master)
        self.controller = controller

        self.num1_label = tk.Label(self, text="Number 1:")
        self.num1_entry = tk.Entry(self)
        self.num2_label = tk.Label(self, text="Number 2:")
        self.num2_entry = tk.Entry(self)
        self.add_button = tk.Button(self, text="Add", command=self.add)
        self.subtract_button = tk.Button(
            self, text="Subtract", command=self.subtract)
        self.result_label = tk.Label(self, text="Result:")
        self.result_value = tk.Label(self, text="")

        self.num1_label.grid(row=0, column=0)
        self.num1_entry.grid(row=0, column=1)
        self.num2_label.grid(row=1, column=0)
        self.num2_entry.grid(row=1, column=1)
        self.add_button.grid(row=2, column=0)
        self.subtract_button.grid(row=2, column=1)
        self.result_label.grid(row=3, column=0)
        self.result_value.grid(row=3, column=1)

    def add(self):
        num1 = float(self.num1_entry.get())
        num2 = float(self.num2_entry.get())
        self.controller.add(num1, num2)

    def subtract(self):
        num1 = float(self.num1_entry.get())
        num2 = float(self.num2_entry.get())
        self.controller.subtract(num1, num2)

    def update_result(self, result):
        self.result_value.config(text=result)

# Controller


class CalculatorController:
    def __init__(self, model, view):
        self.model = model
        self.view = view

    def add(self, num1, num2):
        self.model.add(num1, num2)
        self.view.update_result(self.model.result)

    def subtract(self, num1, num2):
        self.model.subtract(num1, num2)
        self.view.update_result(self.model.result)


# Main
if __name__ == "__main__":
    root = tk.Tk()
    model = CalculatorModel()
    view = CalculatorView(root, None)
    controller = CalculatorController(model, view)
    view.controller = controller
    view.pack()
    root.mainloop()
