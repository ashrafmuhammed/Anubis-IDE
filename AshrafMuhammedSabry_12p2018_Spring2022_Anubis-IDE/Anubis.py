"""
author => Anubis Graduation Team
this project is part of my graduation project and it intends to make a fully functioned IDE from scratch
I've borrowed a function (serial_ports()) from a guy in stack overflow that I can't remember his name
and I gave hime the copyrights of this function, thank you.
"""

# pyqt imports
import Python_Coloring
import CSharp_Coloring
import Default_coloring
from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

# other necessary imports
import sys
import os
import glob
import serial
import time


def serial_ports():
    """ Lists serial port names
        :raises EnvironmentError:
            On unsupported or unknown platforms
        :returns:
            A list of the serial ports available on the system
    """
    if sys.platform.startswith('win'):
        ports = ['COM%s' % (i + 1) for i in range(256)]
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        # this excludes your current terminal "/dev/tty"
        ports = glob.glob('/dev/tty[A-Za-z]*')
    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/tty.*')
    else:
        raise EnvironmentError('Unsupported platform')

    result = []
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            result.append(port)
        except (OSError, serial.SerialException):
            pass
    return result


# signal class
class Signal(QObject):
    """The Signal class provides a way to declare and connect Qt signals in a pythonic way."""
    # initializing a Signal which will take (string) as an input
    reading = pyqtSignal(str)

    # init Function for the Signal class
    def __init__(self):
        QObject.__init__(self)


# Logger Class
class Logger():
    """The Logger class is used to capture stdout so it can be displayed later in the output window."""
    stdout = sys.stdout
    messages = []

    def start(self):
        sys.stdout = self

    def stop(self):
        sys.stdout = self.stdout

    def write(self, text):
        self.messages.append(text)


# Logger object
log = Logger()


# code editor and output fields
editor_code = QTextEdit
text_output = QTextEdit

# initializing filename and language (should be assigned a value when a file is opened or clicked)
filename = None
language = 'Not specified'


# code_widget class
class code_widget(QWidget):
    """The code_widget class is responsible for the main code text editor."""

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        global editor_code
        editor_code = QTextEdit()
        vbox = QVBoxLayout()
        hbox = QHBoxLayout()
        vbox.addLayout(hbox)

        # checkbox for using parameters or not
        has_params = QCheckBox("has parameters?")
        has_params.setChecked(True)
        self.has_params = True
        has_params.stateChanged.connect(lambda: self.check_state(has_params))

        # displaying selected language
        self.lang_label = QLabel()
        self.lang_label.setText(f"Language: {language}")
        self.lang_label.setAlignment(
            QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)

        # highlighting
        if language == 'Python':
            Python_Coloring.PythonHighlighter(editor_code)
            self.lang_label.setStyleSheet("color: #0a8216")
        elif language == 'C#':
            CSharp_Coloring.CSharpHighlighter(editor_code)
            self.lang_label.setStyleSheet("color: #0a8216")
        else:
            Default_coloring.DefaultHighlighter(editor_code)
            self.lang_label.setStyleSheet("color: #a32a0b")

        # highlighting
        if language == 'Python':
            Python_Coloring.PythonHighlighter(editor_code)
            self.lang_label.setStyleSheet("color: #0a8216")
        elif language == 'C#':
            CSharp_Coloring.CSharpHighlighter(editor_code)
            self.lang_label.setStyleSheet("color: #0a8216")
        else:
            Default_coloring.DefaultHighlighter(editor_code)
            self.lang_label.setStyleSheet("color: #a32a0b")

        # adding to the hbox
        hbox.addWidget(has_params)
        hbox.addWidget(self.lang_label)

        # editor
        vbox.addWidget(editor_code)
        self.setLayout(vbox)

    # the function associated with the 'has parameters?' checkbox
    def check_state(self, check_box):
        """this function enables for tracking the state of the 'has parameters?' checkbox
        to be used later while running functions whith/without parameters."""
        self.has_params = check_box.isChecked()


# params_widget class
class params_widget(QWidget):
    """The params_widget class is responsible for the parameters text editor."""

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        global editor_params
        editor_params = QTextEdit()
        hbox = QHBoxLayout()
        hbox.addWidget(editor_params)
        self.setLayout(hbox)


# Widget Class
class Widget(QWidget):
    """The Widget class is responsible for combining different widgets to form the final layout of the applications."""

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # code editor and parameters tabs
        tabs = QTabWidget()
        self.code_editor = code_widget()
        params_editor = params_widget()
        tabs.addTab(self.code_editor, "Code")
        tabs.addTab(params_editor, "Parameters")

        # output text field (for displaying output/errors/hints)
        global text_output
        text_output = QTextEdit()
        text_output.setReadOnly(True)

        # treeview for showing the directory included files
        self.treeview = QTreeView()

        # path for current directory
        path = QDir.currentPath()

        # making a Filesystem variable, setting its root path and applying somefilters (which I need) on it
        self.dirModel = QFileSystemModel()
        self.dirModel.setRootPath(QDir.rootPath())

        # NoDotAndDotDot => Do not list the special entries "." and "..".
        # AllDirs =>List all directories; i.e. don't apply the filters to directory names.
        # Files => List files.
        self.dirModel.setFilter(QDir.NoDotAndDotDot |
                                QDir.AllDirs | QDir.Files)
        self.treeview.setModel(self.dirModel)
        self.treeview.setRootIndex(self.dirModel.index(path))
        self.treeview.clicked.connect(self.on_clicked)

        # left and right boxes
        Left_hbox = QHBoxLayout()
        Right_hbox = QHBoxLayout()

        # Adding treeview to the left box and code editor to the right one
        Left_hbox.addWidget(self.treeview)
        Right_hbox.addWidget(tabs)

        # arranging left/right layouts
        Left_hbox_Layout = QWidget()
        Right_hbox_Layout = QWidget()
        Left_hbox_Layout.setLayout(Left_hbox)
        Right_hbox_Layout.setLayout(Right_hbox)

        # splitter for seperating left and right layouts and make it easier to change the spacing between them
        H_splitter = QSplitter(Qt.Horizontal)
        H_splitter.addWidget(Left_hbox_Layout)
        H_splitter.addWidget(Right_hbox_Layout)
        H_splitter.setStretchFactor(1, 1)

        # splitter for seperating the upper and lower sides of the window
        V_splitter = QSplitter(Qt.Vertical)
        V_splitter.addWidget(H_splitter)
        V_splitter.addWidget(text_output)

        # final layout
        Final_Layout = QHBoxLayout(self)
        Final_Layout.addWidget(V_splitter)
        self.setLayout(Final_Layout)

    # slot for saving the text inside the code editor into main.py file
    @pyqtSlot(str)
    def Saving(s):
        if language == 'Python':
            dest_filename = 'saved_file.py'
            with open(dest_filename, 'w') as f:
                TEXT = editor_code.toPlainText()
                f.write(TEXT)
                text_output.append(f'saved python file to {dest_filename}')
        elif language == 'C#':
            dest_filename = 'saved_file.cs'
            with open(dest_filename, 'w') as f:
                TEXT = editor_code.toPlainText()
                f.write(TEXT)
                text_output.append(f'saved C# file to {dest_filename}')
        else:
            text_output.append('Unsupported file extension!')

    # slot for opening a file and loading its contents to the code editor
    @pyqtSlot(str)
    def Open(s):
        global editor_code
        editor_code.setText(s)

    # function for handling clicking on a file in the treeview
    def on_clicked(self, index):
        """this function handles clicking on a file in the treeview
        it is responsible for two tasks:

        - loading and displaying the file content to the code editor.
        - updating the global variables filename and language."""

        global language, filename
        filepath = self.sender().model().filePath(index)
        filepath = tuple([filepath])

        if filepath[0]:
            try:
                f = open(filepath[0], 'r')
                filename = filepath[0].split('/')[-1]
                language = 'Python' if '.py' in filename else 'C#' if '.cs' in filename else 'Unsupported'
                self.code_editor.lang_label.setText(f"Language: {language}")
                with f:
                    data = f.read()
                    editor_code.setText(data)

                # highlighting
                if language == 'Python':
                    Python_Coloring.PythonHighlighter(editor_code)
                    self.code_editor.lang_label.setStyleSheet("color: #0a8216")
                elif language == 'C#':
                    CSharp_Coloring.CSharpHighlighter(editor_code)
                    self.code_editor.lang_label.setStyleSheet("color: #0a8216")
                else:
                    Default_coloring.DefaultHighlighter(editor_code)
                    self.code_editor.lang_label.setStyleSheet("color: #a32a0b")
            except Exception as e:
                pass


# slot that is connected to the Widget class (reading)
# it takes the (input string) and establishes a connection with the widget class, sends the string to it
@pyqtSlot(str)
def reading(s):
    b = Signal()
    b.reading.connect(Widget.Saving)
    b.reading.emit(s)


# slot that is connected to the Widget class (opening)
# it takes the (input string) and establishes a connection with the widget class, sends the string to it
@pyqtSlot(str)
def opening(s):
    b = Signal()
    b.reading.connect(Widget.Open)
    b.reading.emit(s)


# UI Class
class UI(QMainWindow):
    """The UI class is responsible for the main window
    and contains the functionality for running python/C# code."""

    def __init__(self):
        super().__init__()
        self.intUI()

    def intUI(self):
        self.port_flag = 1
        self.read_signal = Signal()
        self.open_signal = Signal()

        # connecting (self.open_signal) with opening function
        self.open_signal.reading.connect(opening)

        # connecting (self.read_signal) with reading function
        self.read_signal.reading.connect(reading)

        # creating menu items
        menu = self.menuBar()
        filemenu = menu.addMenu('File')
        Port = menu.addMenu('Port')
        Run = menu.addMenu('Run')

        # displaying ports from serial_ports() function
        # copyrights of serial_ports() function goes back to a guy from stackoverflow(whome I can't remember his name), so thank you (unknown)
        Port_Action = QMenu('port', self)
        res = serial_ports()
        for i in range(len(res)):
            s = res[i]
            Port_Action.addAction(s, self.PortClicked)

        # adding the menu which I made to the original (Port menu)
        Port.addMenu(Port_Action)

        # creating run actions
        RunAction = QAction("Run", self)
        RunAction.triggered.connect(self.Run)
        RunAction.setShortcut("Ctrl+R")
        # adding action
        Run.addAction(RunAction)

        # creating file handling actions
        Save_Action = QAction("Save", self)
        Save_Action.triggered.connect(self.save)
        Save_Action.setShortcut("Ctrl+S")
        Close_Action = QAction("Close", self)
        Close_Action.setShortcut("Alt+c")
        Close_Action.triggered.connect(self.close)
        Open_Action = QAction("Open", self)
        Open_Action.setShortcut("Ctrl+O")
        Open_Action.triggered.connect(self.open)
        # adding actions
        filemenu.addAction(Save_Action)
        filemenu.addAction(Close_Action)
        filemenu.addAction(Open_Action)

        # Seting the window Geometry
        self.setGeometry(200, 150, 800, 500)

        # centering the window
        qtRectangle = self.frameGeometry()
        centerPoint = QDesktopWidget().availableGeometry().center()
        qtRectangle.moveCenter(centerPoint)
        self.move(qtRectangle.topLeft())

        # window title and icon
        self.setWindowTitle('Anubis IDE')
        self.setWindowIcon(QtGui.QIcon('Anubis.png'))

        # Widget object
        self.widget = Widget()
        self.setCentralWidget(self.widget)
        self.show()

    # Run function definition
    def Run(self):
        """Run function is responsible for running python/C# functions.

        ### procedure is as following:

        - the user opens a python/C# file that contains a function difinition.
        - the content of the file is loaded to the code editor.
        - the `has prameters?` checkbox is checked by default assuming the function requires parameters.
        - if the function requires parameters, the user shoud add them in the `parameters` tab.
            - parameters should be added such that there is one parameter per line.
            - for python functions, keyword parameters can be used (one per line).
            - for more instructions, please follow the screenshots in the `documentation` pdf.
        - if the function does not require parameters, the user should simply uncheck the `has prameters?` checkbox.
        - the user can then run the code by clicking Run in the menu or using the shortcut `Ctrl+R`.
        - output, errors or hints should be displayed in the output field.
        - some exception handling was done, eg. displaying a hint when the user forgets to enter parameters.

        ### for the code to run, these steps are followed:
        #### python functions:
        - the code is excecuted right away by means of `exec` function.

        #### C# functions:
        - the function is wrapped inside a main function from the template `main.cs`.
        - the combination of the two files is saved to a temporary file `temp_code_runner.cs`
        - the code is excecuted by means of the `os` module as follows:
            - `csc temp_code_runner.cs` command is excecuted followed by `temp_code_runner`"""

        if self.port_flag == 0:
            func_text = editor_code.toPlainText()
            """Compiler Part"""
            text_output.append("Sorry, there is no attached compiler.")

        else:
            # executing the function
            # starting the logger to capture output
            log.start()
            try:
                # python file
                if language == 'Python':
                    try:
                        # function  input text by user
                        func_text = editor_code.toPlainText()
                        if func_text.strip() == '':
                            raise Exception("function definition missing!")
                        elif 'def' not in func_text:
                            raise Exception("Bad function definition!")

                        # parsing function definition
                        funcname_2_end = func_text.replace('def', '').strip()
                        funcname = funcname_2_end[:funcname_2_end.index(
                            '(')].strip()

                        # executing function definition
                        exec(func_text)

                        # executing function call
                        if self.widget.code_editor.has_params:
                            # parameters input text by user
                            params_text = editor_params.toPlainText()
                            joined_params = ','.join(line.strip()
                                                     for line in params_text.split('\n') if line)
                            if joined_params == '':
                                raise Exception(
                                    "parameters missing while has parameters is checked!")

                            # executing function with given parameters
                            exec(f'{funcname}({joined_params})')
                        else:
                            # executing parameterless function
                            exec(f'{funcname}()')
                    except ValueError:
                        print('Bad function definition!')

                # csharp file
                elif language == 'C#':
                    try:
                        # reading main.cs (a fixed template that's only usable combined with a function)
                        with open('main.cs', 'r') as f:
                            main_content = f.read()

                        # deleting old temp_code_runner.cs/temp_code_runner.exe files if exist
                        if 'temp_code_runner.cs' in ''.join(glob.glob("./*")):
                            os.remove("temp_code_runner.cs")
                        if 'temp_code_runner.exe' in ''.join(glob.glob("./*")):
                            os.remove("temp_code_runner.exe")

                        # saving code to temp file
                        with open('temp_code_runner.cs', 'w') as f:
                            TEXT = editor_code.toPlainText()
                            # adding function definition
                            main_content = main_content.replace(
                                'function_definition_placeholder', TEXT)
                            # getting function name
                            funcname = TEXT[:TEXT.index('(')].split()[-1]
                            # adding function call
                            if self.widget.code_editor.has_params:
                                # parameters input text by user
                                params_text = editor_params.toPlainText()
                                joined_params = ','.join(line.strip()
                                                         for line in params_text.split('\n') if line)
                                if joined_params == '':
                                    raise Exception(
                                        "parameters missing while has parameters is checked!")
                                main_content = main_content.replace(
                                    'function_call_placeholder', f'{funcname}({joined_params})')
                            else:
                                main_content = main_content.replace(
                                    'function_call_placeholder', f'{funcname}()')
                            f.write(main_content)
                            time.sleep(0.1)

                        # compiling the .cs file
                        os.popen(f'csc temp_code_runner.cs')

                        # waiting a bit for the combiler to finish
                        time.sleep(0.8)

                        # running the .cs file and capture the stdout
                        if 'temp_code_runner.exe' in ''.join(glob.glob("./*")):
                            cs_output = os.popen('temp_code_runner').read()
                        else:
                            cs_output = 'C# compile error\n'

                        # adding output to the logger
                        log.messages.append(cs_output)
                    except Exception as e:
                        print(e)
                # no file selected
                elif filename == None:
                    print('no file selected!')
                # unsupported language
                else:
                    print('Unsupported language!')
            except Exception as e:
                print(e)

            # stopping the logger
            log.stop()

            # adding logs to the output window text
            text_output.append(''.join(log.messages))
            log.messages = []

    # this function is made to get which port was selected by the user
    @QtCore.pyqtSlot()
    def PortClicked(self):
        action = self.sender()
        self.portNo = action.text()
        self.port_flag = 0

    # function for saving the code into a file
    def save(self):
        self.read_signal.reading.emit("name")

    # function for opening a file and exhibits it to the user in a text editor
    def open(self):
        global language, filename
        filepath = QFileDialog.getOpenFileName(
            self, 'Open File', '.')

        if filepath[0]:
            try:
                f = open(filepath[0], 'r')
                filename = filepath[0].split('/')[-1]
                language = 'Python' if '.py' in filename else 'C#' if '.cs' in filename else 'Unsupported'
                self.widget.code_editor.lang_label.setText(
                    f"Language: {language}")
                with f:
                    data = f.read()
                self.open_signal.reading.emit(data)
            except Exception as e:
                pass


# running the app
if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = UI()
    # ex = Widget()
    sys.exit(app.exec_())
