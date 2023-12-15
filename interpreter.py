import tkinter as tk
from tkinter import filedialog
from io import StringIO
import sys
import easygui
import threading

class LineNumbers(tk.Text):
    def __init__(self, master, text_widget, **kwargs):
        super().__init__(master, **kwargs)

        self.text_widget = text_widget
        self.text_widget.bind('<KeyRelease>', self.on_key_release)
        self.text_widget.bind('<FocusIn>', self.on_key_release)

        self.insert(1.0, '1')
        self.configure(state='disabled')

    def on_key_release(self, event=None):
        p, q = self.text_widget.index("@0,0").split('.')
        p = int(p)
        final_index = str(self.text_widget.index(tk.END))
        num_of_lines = final_index.split('.')[0]
        line_numbers_string = "\n".join(str(p + no) for no in range(int(num_of_lines)))
        width = len(str(num_of_lines))

        self.configure(state='normal', width=width)
        self.delete(1.0, tk.END)
        self.insert(1.0, line_numbers_string)
        self.configure(state='disabled')

class interpreter():
    def __init__(self):
        self.states = {}
        self.errors = []
        self.EMHALT = False
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
        try:
            if self.states["a"] == self.states["b"]:
                self.goto(line)
        except:
            self.errors.append(("Register A and B are not saved/set yet", self.pointer),)

    def goto(self, line):
        self.pointer = int(line)-1

    def setstate(self, state, val):
        self.states[state] = val

    def lsta(self):
        pass

    def findfirstcom(self, target):
        for i in range(self.pointer, -1, -1):
            if self.lines[i] != "":
                if self.lines[i].split(" ")[0] == target:
                    return i
        return False

    def lsto(self):
        try:
            if self.states["d"] != "0":
                temp = self.findfirstcom("lsta")
                if temp == False:
                    self.errors.append(("lsta wasn't found", self.pointer),)
                    raise TypeError("lsta wasn't found")
                else:
                    self.pointer = self.findfirstcom("lsta")
        except KeyError:
            self.errors.append(("Register D is not saved/set yet", self.pointer),)
            raise TypeError("Register D is not saved/set yet")

    def lsetstate(self, state, val):
        self.states[state] = self.lines[int(val)]

    def pri(self):
        try:
            print(self.states["c"])
        except:
            self.errors.append(("Register C has not been saved/set yet", self.pointer),)

    def inp(self):
        self.setstate("c", input("in: "))

    def add(self):
        if self.states["a"].isnumeric() == True and self.states["b"].isnumeric() == True:
            self.setstate("c", str(int(self.states["a"])+int(self.states["b"])))
        else:
            self.errors.append(("non-numeric registers", self.pointer),)
            raise ValueError("non-numeric registers")

    def halt(self):
        self.pointer = 9999999999999999999999999999999999999999999

    def sub(self):
        if self.states["a"].isnumeric() == True and self.states["b"].isnumeric() == True:
            self.setstate("c", str(int(self.states["a"])-int(self.states["b"])))
        else:
            self.errors.append(("non-numeric registers", self.pointer),)
            raise ValueError("non-numeric registers")

    def writestate(self, state, line):
        try:
            self.lines[int(line)] = self.states[state]
        except:
            self.errors.append(("Register {} is not saved/set yet".format(state), self.pointer),)

    def listtostr(self, target):
        temp = ""
        for i in target:
            temp = temp + i + " "
        temp = temp[:-1]
        return temp

    def execline(self, line, error_message=True):
        if self.EMHALT == False:
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
                if error_message == True:
                    print("error at line {}, error: {}.".format(self.pointer, e))
                    input("press enter to continue ")
                else:
                    return (True, e, self.pointer+1)

    def execcode(self, code):
        self.EMHALT = False
        self.lines = code.split("\n")
        self.pointer = 0
        while self.pointer < len(self.lines):
            if self.lines[self.pointer] != "":
                temp = self.execline(self.pointer, False)
                if temp != None:
                    if temp[0] == True:
                        print("ERROR: {} at line {}".format(temp[1], temp[2]))
                        break
            self.pointer += 1
        print()
        print("program finished")

    def PHpri(self):
        pass

    def PHinp(self):
        self.states["c"] = "0"

    def geterrors(self, code):
        self.instructions["inp"] = self.PHinp
        self.instructions["pri"] = self.PHpri
        self.errors = []
        self.states = {}
        self.lines = code.split("\n")
        self.pointer = 0
        while self.pointer < len(self.lines):
            if self.lines[self.pointer] != "":
                self.execline(self.pointer, False)
            self.pointer += 1
        self.instructions["inp"] = self.inp
        self.instructions["pri"] = self.pri
        return self.errors


class JemblyIDE:
    def __init__(self, root):
        self.root = root
        self.root.title("Jembly IDE")
        self.root.resizable(False, False)

        self.text_editor = tk.Text(self.root, wrap="none")
        self.ln = LineNumbers(self.root, self.text_editor, width=2)
        #self.ln.pack(side=tk.LEFT)
        self.ln.grid(row=0, column=0)
        #self.text_editor.pack(side=tk.LEFT, expand=True)
        self.text_editor.grid(row=0, column=1)

        self.run_button = tk.Button(self.root, text="Run", command=self.run_jembly_code)
        self.run_button.grid(row=1, column=0)
        self.lines_button = tk.Button(self.root, text="Update lines", command=self.updatelines)
        self.lines_button.grid(row=1, column=3)
        self.error_button = tk.Button(self.root, text="Find errors", command=lambda: threading.Thread(target=self.geterrors).start())
        self.error_button.grid(row=1, column=2)
        self.EMHALT_button = tk.Button(self.root, text="Emergency Halt", command=self.EMHALT)
        self.EMHALT_button.grid(row=1, column=1)
        #self.run_button.pack(side=tk.LEFT)

        self.output_text = tk.Text(self.root, wrap="word")
        self.output_text.grid(row=2, column=1)
        self.output_text.config(height=23, width=80)
        #self.output_text.pack(side=tk.RIGHT)

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

    def EMHALT(self):
        runner.EMHALT = True

    def CETS(self, errors):
        out = ""
        for i in errors:
            out = out + "{} at line {}, ".format(i[0], i[1])
        return out

    def geterrors(self):
        self.output_text.delete("1.0", tk.END)
        self.output_text.insert(tk.END, "finding errors...")
        errors = runner.geterrors(self.text_editor.get("1.0", "end-1c"))
        if errors == []:
            self.output_text.insert(tk.END, "\nNo errors found.")
        else:
            self.output_text.insert(tk.END, "\nErrors: {}".format(self.CETS(errors)))
        self.output_text.see("end")

    def updatelines(self):
        self.output_text.focus_set()
        self.text_editor.focus_set()

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
        self.text_editor.focus_set()

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
        input_value = easygui.enterbox("In:", "Input")
        runner.setstate("c", input_value)
        sys.stdout = self.output_stream

    def custom_pri(self):
        print(runner.states["c"], file=self.output_stream)
        sys.stdout.flush()
        output = self.output_stream.getvalue()
        self.output_text.delete("1.0", tk.END)
        self.output_text.insert(tk.END, output)
        self.output_text.see("end")

    def run_jembly_code(self):
        self.output_text.delete("1.0", tk.END)
        code = self.text_editor.get("1.0", "end-1c")
        self.output_stream = StringIO()
        sys.stdout = self.output_stream

        runner.instructions["inp"] = lambda: self.custom_inp()
        runner.instructions["pri"] = lambda: self.custom_pri()

        threading.Thread(target=runner.execcode(code)).start()

        runner.instructions["inp"] = runner.inp
        runner.instructions["pri"] = runner.pri

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
