import tkinter as tk
from tkinter import filedialog
from io import StringIO
import sys

class interpreter():
    def __init__(self):
        self.states = {}
        self.instructions = {
            "sav-a": lambda val: self.setstate("a", val),
            "sav-b": lambda val: self.setstate("b", val),
            "sav-c": lambda val: self.setstate("c", val),
            "sav-d": lambda val: self.setstate("d", val),
            "out-c": lambda line: self.writestate("c", line),
            "out-d": lambda line: self.writestate("d", line),
            "add": self.add,
            "sub": self.sub,
            "pri": self.pri,
            "inp": self.inp,
            "HALT": self.halt,
            "l-sav-a": lambda val: self.lsetstate("a", val),
            "l-sav-b": lambda val: self.lsetstate("b", val),
            "l-sav-c": lambda val: self.lsetstate("c", val),
            "l-sav-d": lambda val: self.lsetstate("d", val),
            "lsta": self.lsta,
            "lsto": self.lsto,
            "equ": lambda line: self.equ(line),
            "goto": lambda line: self.goto(line),
        }
        self.pointer = 0
        self.lines = []

    def equ(self, line):
        if self.states["a"] == self.states["b"]:
            self.goto(line)

    def goto(self, line):
        self.pointer = int(line)-1

    def setstate(self, state, val):
        self.states[state] = val

    def lsta(self):
        pass

    def findfirstcom(self, target):
        for i in range(self.pointer, 0, -1):
            if self.lines[i] != "":
                if self.lines[i].split(" ")[0] == target:
                    return i
        return False

    def lsto(self):
        if self.states["d"] != "0":
            self.pointer = self.findfirstcom("lsta")

    def lsetstate(self, state, val):
        self.states[state] = self.lines[int(val)]

    def pri(self):
        print(self.states["c"])

    def inp(self):
        self.setstate("c", input("in: "))

    def add(self):
        if self.states["a"].isnumeric() == True and self.states["b"].isnumeric() == True:
            self.setstate("c", str(int(self.states["a"])+int(self.states["b"])))
        else:
            raise ValueError("non-numeric registers")

    def halt(self):
        self.pointer = 9999999999999999999999999999999999999999999

    def sub(self):
        if self.states["a"].isnumeric() == True and self.states["b"].isnumeric() == True:
            self.setstate("c", str(int(self.states["a"])-int(self.states["b"])))
        else:
            raise ValueError("non-numeric registers")

    def writestate(self, state, line):
        self.lines[int(line)] = self.states[state]

    def listtostr(self, target):
        temp = ""
        for i in target:
            temp = temp + i + " "
        temp = temp[:-1]
        return temp

    def execline(self, line):
        temp = self.lines[line].split(" ")
        ins = temp[0]
        temp.pop(0)

        temp2 = self.listtostr(temp)
        if temp2.startswith('"'):
            temp = temp2.replace('"', "")
            temp = [temp]

        try:
            if len(temp) == 0:
                self.instructions[ins]()
            elif len(temp) == 1:
                self.instructions[ins](temp[0])
            elif len(temp) == 2:
                self.instructions[ins](temp[0], temp[1])
        except Exception as e:
            print("error at line {}, error: {}.".format(self.pointer, e))
            input("press enter to continue ")

    def execcode(self, code):
        self.lines = code.split("\n")
        self.pointer = 0
        while self.pointer < len(self.lines):
            if self.lines[self.pointer] != "":
                self.execline(self.pointer)
            self.pointer += 1
        print()
        print("program finished")

class JemblyIDE:
    def __init__(self, root):
        self.root = root
        self.root.title("Jembly IDE")

        self.text_editor = tk.Text(self.root, wrap="none")
        self.text_editor.pack(expand=True, fill="both")

        self.run_button = tk.Button(self.root, text="Run", command=self.run_jembly_code)
        self.run_button.pack()

        self.output_text = tk.Text(self.root, wrap="word")
        self.output_text.pack(expand=True, fill="both")

        self.menubar = tk.Menu(self.root)
        self.filemenu = tk.Menu(self.menubar, tearoff=0)
        self.filemenu.add_command(label="Open", command=self.open)
        self.filemenu.add_command(label="Save as...", command=self.save)
        self.filemenu.add_command(label="Exit", command=self.exit)
        self.menubar.add_cascade(label="File", menu=self.filemenu)

        self.helpmenu = tk.Menu(self.menubar, tearoff=0)
        self.helpmenu.add_command(label="List of all instructions", command=self.listinstructions)
        self.menubar.add_cascade(label="Help", menu=self.helpmenu)

        self.root.config(menu=self.menubar)

    def listinstructions(self):
        self.text_editor.delete("1.0", tk.END)
        code = """
sav-c "sav-a: sets register A to argument"
pri
sav-c "sav-b: sets register B to argument"
pri
sav-c "sav-c: sets register C to argument"
pri
sav-c "sav-d: sets register D to argument"
pri
sav-c "out-c: sets the specified line to the value of register C"
pri
sav-c "out-d: sets the specified line to the value of register D"
pri
sav-c "add: adds value of register A and register B and sets register C to result"
pri
sav-c "sub: subtracts value of register A and register B and sets register C to result"
pri
sav-c "pri: prints value of register C"
pri
sav-c "inp: asks user for input and sets value of register C"
pri
sav-c "HALT: exits program"
pri
sav-c "l-sav-a: sets register A to the text from the specified line"
pri
sav-c "l-sav-b: sets register B to the text from the specified line"
pri
sav-c "l-sav-c: sets register C to the text from the specified line"
pri
sav-c "l-sav-d: sets register D to the text from the specified line"
pri
sav-c "lsta: marks the start of a loop"
pri
sav-c "lsto: marks the stop of a loop. goes to lsta if register D is not 0"
pri
sav-c "equ: checks if register A and B are equal. if True then goes to specified line"
pri
sav-c "goto: goes to specified line"
pri
        """
        self.text_editor.insert(tk.END, code)
        self.run_jembly_code()

    def exit(self):
        self.root.destroy()

    def open(self):
        name = filedialog.askopenfilename(
            filetypes=(
                ('Jembly Code Files', '*.JCF'),
            )
        )
        self.text_editor.delete("1.0", tk.END)
        file = open(name, 'r')
        file = file.read()
        self.text_editor.insert(tk.END, file)

    def save(self):
        name = filedialog.asksaveasfilename(
            filetypes=(
                ('Jembly Code Files', '*.JCF'),
            )
        )
        file = open(name, 'w')
        file.write(self.text_editor.get("1.0", "end-1c"))
        file.close()

    def custom_inp(self):
        sys.stdout = sys.__stdout__
        input_value = tk.simpledialog.askstring("Input", "in:")
        runner.setstate("c", input_value)
        sys.stdout = self.output_stream

    def custom_pri(self):
        print(runner.states["c"])
        sys.stdout.flush()
        output = self.output_stream.getvalue()
        self.output_text.delete("1.0", tk.END)
        self.output_text.insert(tk.END, output)
        self.output_text.see("end")

    def run_jembly_code(self):
        code = self.text_editor.get("1.0", "end-1c")
        self.output_stream = StringIO()
        sys.stdout = self.output_stream

        runner.instructions["inp"] = lambda: self.custom_inp()
        runner.instructions["pri"] = lambda: self.custom_pri()

        runner.execcode(code)

        sys.stdout = sys.__stdout__
        output = self.output_stream.getvalue()
        self.output_text.delete("1.0", tk.END)
        self.output_text.insert(tk.END, output)
        self.output_text.see("end")

if __name__ == "__main__":
    runner = interpreter()
    root = tk.Tk()
    app = JemblyIDE(root)
    root.mainloop()



