from PyQt5 import QtCore, QtWidgets
from PyQt5.QtGui import *
import qtawesome
from PyQt5.QtWidgets import *
from Lexical import *
from File import *
from Syntactic import *
from ObjectCode import *
import os


class myUI(QtWidgets.QMainWindow):
    def __init__(self):
        super(myUI, self).__init__()
        self.init_ui()

    def init_ui(self):
        self.init_ui_main()
        self.init_ui_top()
        self.init_ui_left()
        self.init_ui_right()
        self.init_ui_stack1()
        self.init_ui_stack2()
        self.init_ui_stack3()
        self.init_ui_stack4()
        self.init_ui_stack5()
        self.init_ui_stack6()

    def init_ui_main(self):
        self.setFixedSize(1000, 720)
        self.mainWidget = QtWidgets.QWidget()
        self.mainLayout = QtWidgets.QGridLayout()
        self.mainWidget.setLayout(self.mainLayout)
        self.setCentralWidget(self.mainWidget)  # 设置窗口主部件
        self.mainLayout.setContentsMargins(0, 0, 0, 0)
        self.setWindowFlag(QtCore.Qt.FramelessWindowHint)  # 隐藏边框

    def init_ui_top(self):
        # 创建顶部部件
        self.topWidget = QtWidgets.QWidget()
        self.topLayout = QtWidgets.QGridLayout()  # 创建头部部件的网格布局层
        self.topWidget.setLayout(self.topLayout)  # 设置头部部件布局为网格
        self.topLayout.setSpacing(0)
        # 设置应用标题和登出按钮
        self.title = QtWidgets.QLabel("    类C语言编译器")
        self.signOut = QtWidgets.QPushButton(qtawesome.icon('fa.sign-out', color='#808080'), "退出")
        self.signOut.clicked.connect(self.close)  # 点击按钮之后关闭窗口
        # 设置顶部内组件在顶部的布局
        self.topLayout.addWidget(self.title, 0, 0, 1, 15)
        self.topLayout.addWidget(self.signOut, 0, 16, 1, 1)
        # 设置顶部在整个界面的布局
        self.mainLayout.addWidget(self.topWidget, 0, 0, 1, 13)  # 右侧部件在第0行第0列，占1行13列
        # 设置顶部组件的QSS
        self.topWidget.setStyleSheet(
            '''
            *{background-color:#000080;}
            QLabel{
                color:#ffffff;
                border:none;
                font-weight:600;
                font-size:20px;
                font-family:'微软雅黑';
            }
            QPushButton{
                color:#ffffff;
                border:none;
                font-weight:600;
                font-size:20px;
                font-family:'微软雅黑';
             }
            ''')
        self.signOut.setStyleSheet(
            '''
            QPushButton{ text-align:right;padding-right:30px;color:#C71682;font-size:20px;}
            ''')
        self.title.setStyleSheet(
            '''
            QLabel{ text-align:left;padding-left:30px;color:#C71682;font-size:20px;}
            ''')

    def init_ui_left(self):
        # 创建左侧部件
        self.leftWidget = QtWidgets.QWidget()
        self.leftLayout = QtWidgets.QGridLayout()  # 创建左侧部件的网格布局层
        self.leftWidget.setLayout(self.leftLayout)  # 设置左侧部件布局为网格
        # 左侧部件由三部分组成
        self.leftWidget1 = QtWidgets.QWidget()
        self.leftLayout1 = QtWidgets.QGridLayout()
        self.leftWidget1.setLayout(self.leftLayout1)
        self.leftWidget2 = QtWidgets.QWidget()
        self.leftLayout2 = QtWidgets.QGridLayout()
        self.leftWidget2.setLayout(self.leftLayout2)
        self.leftWidget3 = QtWidgets.QWidget()
        self.leftLayout3 = QtWidgets.QGridLayout()
        self.leftWidget3.setLayout(self.leftLayout3)
        # 左侧三个部分的布局
        self.leftLayout.addWidget(self.leftWidget1, 0, 0, 3, 3)  # 左侧部件在第0行第0列，占3行3列
        self.leftLayout.addWidget(self.leftWidget2, 3, 0, 6, 3)  # 左侧部件在第3行第0列，占6行3列
        self.leftLayout.addWidget(self.leftWidget3, 9, 0, 2, 3)  # 左侧部件在第9行第0列，占2行3列
        # 创建左侧上部的logo
        self.logo = QPixmap('logo.png')
        self.logoLabel = QtWidgets.QLabel()
        self.logoLabel.setPixmap(self.logo)
        # self.logoLabel.setScaledContents(True)
        self.logoLabel.setFixedSize(180, 150)
        # logo的布局
        self.leftLayout1.addWidget(self.logoLabel, 0, 0, 1, 1)
        # 创建左侧中部的选择按钮
        self.leftButton1 = QtWidgets.QPushButton("代码编辑")
        self.leftButton2 = QtWidgets.QPushButton("词法分析结果")
        self.leftButton3 = QtWidgets.QPushButton("语法分析结果")
        self.leftButton4 = QtWidgets.QPushButton("中间代码")
        self.leftButton5 = QtWidgets.QPushButton("函数表&符号表")
        self.leftButton6 = QtWidgets.QPushButton("目标代码")
        # 先设置这些按钮不可用
        self.leftButton1.setEnabled(True)
        self.leftButton2.setEnabled(False)
        self.leftButton3.setEnabled(False)
        self.leftButton4.setEnabled(False)
        self.leftButton5.setEnabled(False)
        self.leftButton6.setEnabled(False)
        # 创建按钮对于页面的切换事件
        self.leftButton1.clicked.connect(lambda: self.change_stack(1))
        self.leftButton2.clicked.connect(lambda: self.change_stack(2))
        self.leftButton3.clicked.connect(lambda: self.change_stack(3))
        self.leftButton4.clicked.connect(lambda: self.change_stack(4))
        self.leftButton5.clicked.connect(lambda: self.change_stack(5))
        self.leftButton6.clicked.connect(lambda: self.change_stack(6))
        # 左侧中部的按钮的布局
        self.leftLayout2.addWidget(self.leftButton1, 0, 0, 1, 3)
        self.leftLayout2.addWidget(self.leftButton2, 1, 0, 1, 3)
        self.leftLayout2.addWidget(self.leftButton3, 2, 0, 1, 3)
        self.leftLayout2.addWidget(self.leftButton4, 3, 0, 1, 3)
        self.leftLayout2.addWidget(self.leftButton5, 4, 0, 1, 3)
        self.leftLayout2.addWidget(self.leftButton6, 5, 0, 1, 3)
        # 设置布局的边缘
        self.leftLayout.setContentsMargins(0, 0, 0, 0)
        self.leftLayout1.setContentsMargins(0, 0, 0, 0)
        self.leftLayout2.setContentsMargins(0, 0, 0, 0)
        self.leftLayout3.setContentsMargins(0, 0, 0, 0)
        # 设置整个左侧的布局
        self.mainLayout.addWidget(self.leftWidget, 1, 0, 12, 3)  # 左侧部件在第1行第0列，占12行3列
        # 设置左侧部件的QSS
        self.leftWidget.setStyleSheet(
            '''
            *{background-color:#fafafa;}
            QPushButton{
                border:none; 
                font-size:20px; 
                text-align:left; 
                padding-left:30px; 
                height:70px; 
                font-family:'微软雅黑'; }
            QPushButton:hover{background:red;}
            ''')
        self.leftWidget1.setStyleSheet(
            '''
            *{color:#2c3a45;}
            QToolButton{
                border:none;
                font-weight:600;
                font-size:14px;
                font-family:'微软雅黑';
            }
            ''')
        self.leftWidget2.setStyleSheet(
            '''
            QPushButton:hover{background:#e6e6e6;}
            ''')

    def init_ui_right(self):
        # 创建右部部件
        self.rightWidget = QtWidgets.QStackedWidget()
        self.rightWidget.setContentsMargins(0, 0, 0, 0);
        # 设置右部在整个界面的布局
        self.mainLayout.addWidget(self.rightWidget, 1, 3, 12, 9)
        # 右部QSS
        self.rightWidget.setStyleSheet(
            '''
            *{background-color:#f2f2f2;}
            ''')

    def init_ui_stack1(self):
        # 创建右部堆栈1
        self.rightStack1 = QtWidgets.QWidget()
        self.rightStack1Layout = QtWidgets.QGridLayout()
        self.rightStack1.setLayout(self.rightStack1Layout)
        # 代码输入标签
        self.codeInputLabel = QtWidgets.QLabel("输入代码：")
        self.rightStack1Layout.addWidget(self.codeInputLabel, 0, 0, 1, 1)
        # 代码输入框
        self.codeBox = QtWidgets.QTextEdit()
        self.rightStack1Layout.addWidget(self.codeBox, 1, 0, 1, 5)
        # 编译按钮
        self.compileButton = QtWidgets.QPushButton("编译")
        self.compileButton.setFixedSize(140, 40)
        self.compileButton.clicked.connect(self.compile)
        self.rightStack1Layout.addWidget(self.compileButton, 2, 2, 1, 1)
        # 设置右侧堆栈1在右侧的布局
        self.rightWidget.addWidget(self.rightStack1)

    def init_ui_stack2(self):
        # 创建右部堆栈2
        self.rightStack2 = QtWidgets.QWidget()
        self.rightStack2Layout = QtWidgets.QGridLayout()
        self.rightStack2.setLayout(self.rightStack2Layout)
        # 词法结果展示组件
        self.lexTableLabel = QtWidgets.QLabel("词法分析结果：")
        self.rightStack2Layout.addWidget(self.lexTableLabel, 0, 0, 1, 1)
        self.lexTable = QtWidgets.QTableWidget()
        self.lexTable.setRowCount(10)
        self.lexTable.setColumnCount(4)
        self.lexTable.setHorizontalHeaderLabels(["类型", "值", "行", "列"])
        self.rightStack2Layout.addWidget(self.lexTable, 1, 0, 10, 5)
        self.rightStack2Blank = QtWidgets.QLabel("")
        self.rightStack2Layout.addWidget(self.rightStack2Blank, 11, 0, 1, 5)
        # 设置右侧堆栈2在右侧的布局
        self.rightWidget.addWidget(self.rightStack2)

    def init_ui_stack3(self):
        # 创建右部堆栈3
        self.rightStack3 = QtWidgets.QWidget()
        self.rightStack3Layout = QtWidgets.QGridLayout()
        self.rightStack3.setLayout(self.rightStack3Layout)
        # 语法分析结果展示组件
        self.gramTableLabel = QtWidgets.QLabel("语法分析结果：")
        self.rightStack3Layout.addWidget(self.gramTableLabel, 0, 0, 1, 1)
        self.gramTable = QtWidgets.QTableWidget()
        self.gramTable.setRowCount(10)
        self.gramTable.setColumnCount(3)
        self.gramTable.setHorizontalHeaderLabels(["状态栈", "移进栈", "待移进栈"])
        self.rightStack3Layout.addWidget(self.gramTable, 1, 0, 10, 5)
        self.rightStack3Blank = QtWidgets.QLabel("")
        self.rightStack3Layout.addWidget(self.rightStack3Blank, 11, 0, 1, 5)
        # 设置右侧堆栈3在右侧的布局
        self.rightWidget.addWidget(self.rightStack3)

    def init_ui_stack4(self):
        # 创建右部堆栈4
        self.rightStack4 = QtWidgets.QWidget()
        self.rightStack4Layout = QtWidgets.QGridLayout()
        self.rightStack4.setLayout(self.rightStack4Layout)
        # 中间代码展示组件
        self.midCodeTableLabel = QtWidgets.QLabel("中间代码：")
        self.rightStack4Layout.addWidget(self.midCodeTableLabel, 0, 0, 1, 1)
        self.midCodeTable = QtWidgets.QTableWidget()
        self.midCodeTable.setRowCount(10)
        self.midCodeTable.setColumnCount(4)
        self.midCodeTable.setHorizontalHeaderLabels(["操作符", "源操作数1", "源操作数2", "结果"])
        self.rightStack4Layout.addWidget(self.midCodeTable, 1, 0, 10, 5)
        self.rightStack4Blank = QtWidgets.QLabel("")
        self.rightStack4Layout.addWidget(self.rightStack4Blank, 11, 0, 1, 5)
        # 设置右侧堆栈4在右侧的布局
        self.rightWidget.addWidget(self.rightStack4)

    def init_ui_stack5(self):
        # 创建右部堆栈5
        self.rightStack5 = QtWidgets.QWidget()
        self.rightStack5Layout = QtWidgets.QGridLayout()
        self.rightStack5.setLayout(self.rightStack5Layout)
        # 函数表标签
        self.funcTableLabel = QtWidgets.QLabel("函数表：")
        self.rightStack5Layout.addWidget(self.funcTableLabel, 0, 0, 1, 3)
        # 函数表展示组件
        self.funcTable = QtWidgets.QTableWidget()
        self.funcTable.setRowCount(10)
        self.funcTable.setColumnCount(4)
        self.funcTable.setHorizontalHeaderLabels(["标识符", "返回类型", "入口标签", "形参类型"])
        self.rightStack5Layout.addWidget(self.funcTable, 1, 0, 5, 3)
        # 空白1
        self.rightStack5Blank1 = QtWidgets.QLabel("")
        self.rightStack5Layout.addWidget(self.rightStack5Blank1, 6, 0, 1, 3)
        # 函数表标签
        self.symbolTableLabel = QtWidgets.QLabel("符号表：")
        self.rightStack5Layout.addWidget(self.symbolTableLabel, 7, 0, 1, 3)
        # 符号表展示组件
        self.symbolTable = QtWidgets.QTableWidget()
        self.symbolTable.setRowCount(10)
        self.symbolTable.setColumnCount(6)
        self.symbolTable.setHorizontalHeaderLabels(["标识符", "类型", "大小(字节)", "内存偏移量", "对应的中间变量", "所在函数"])
        self.rightStack5Layout.addWidget(self.symbolTable, 8, 0, 5, 3)
        # 空白2
        self.rightStack5Blank2 = QtWidgets.QLabel("")
        self.rightStack5Layout.addWidget(self.rightStack5Blank2, 14, 0, 1, 3)
        # 设置右侧堆栈5在右侧的布局
        self.rightWidget.addWidget(self.rightStack5)

    def init_ui_stack6(self):
        # 创建右部堆栈6
        self.rightStack6 = QtWidgets.QWidget()
        self.rightStack6Layout = QtWidgets.QGridLayout()
        self.rightStack6.setLayout(self.rightStack6Layout)
        # 目标代码展示组件
        self.objectCodeLabel = QtWidgets.QLabel("目标代码：")
        self.rightStack6Layout.addWidget(self.objectCodeLabel, 0, 0, 1, 1)
        self.objectCodeBox = QtWidgets.QTextEdit()
        self.rightStack6Layout.addWidget(self.objectCodeBox, 1, 0, 12, 5)
        self.rightStack6Blank = QtWidgets.QLabel("")
        self.rightStack6Layout.addWidget(self.rightStack6Blank, 13, 0, 1, 5)
        # 设置右侧堆栈6在右侧的布局
        self.rightWidget.addWidget(self.rightStack6)

    def change_stack(self, id):
        self.leftButton1.setStyleSheet('''*{background-color:#fafafa;}''')
        self.leftButton2.setStyleSheet('''*{background-color:#fafafa;}''')
        self.leftButton3.setStyleSheet('''*{background-color:#fafafa;}''')
        self.leftButton4.setStyleSheet('''*{background-color:#fafafa;}''')
        self.leftButton5.setStyleSheet('''*{background-color:#fafafa;}''')
        self.leftButton6.setStyleSheet('''*{background-color:#fafafa;}''')
        if id == 1:
            self.leftButton1.setStyleSheet('''*{background-color:#e6e6e6;}''')
        if id == 2:
            self.leftButton2.setStyleSheet('''*{background-color:#e6e6e6;}''')
        if id == 3:
            self.leftButton3.setStyleSheet('''*{background-color:#e6e6e6;}''')
        if id == 4:
            self.leftButton4.setStyleSheet('''*{background-color:#e6e6e6;}''')
        if id == 5:
            self.leftButton5.setStyleSheet('''*{background-color:#e6e6e6;}''')
        if id == 6:
            self.leftButton6.setStyleSheet('''*{background-color:#e6e6e6;}''')
        self.rightWidget.setCurrentIndex(id - 1)

    def compile(self):
        os.chdir(os.path.dirname(sys.argv[0]))  # 将工作路径改为该文件目录
        self.lex = LexicalAnalyzer()
        self.cfg = CFG()
        self.cfg.readGrammerFile('./productions.txt')
        self.cfg.getDotItems()
        self.cfg.calFirstSet()
        self.family = ItemSetSpecificationFamily(self.cfg)
        self.family.buildFamily()
        self.ana = SyntacticAnalyzer(self.lex, self.cfg, self.family)
        self.ana.getTables()
        self.originCode = self.codeBox.toPlainText()
        self.ana.isRecognizable(self.originCode)

        # 编译结果提示
        if self.ana.syntacticRst == False:
            Dialog = QMessageBox.question(self, "compile fail", self.ana.syntacticErrMsg, QMessageBox.Yes)
            self.leftButton2.setEnabled(False)
            self.leftButton3.setEnabled(False)
            self.leftButton4.setEnabled(False)
            self.leftButton5.setEnabled(False)
            self.leftButton6.setEnabled(False)
            return
        elif self.ana.semantic.semanticRst == False:
            Dialog = QMessageBox.question(self, "compile fail", self.ana.semantic.semanticErrMsg, QMessageBox.Yes)
            self.leftButton2.setEnabled(False)
            self.leftButton3.setEnabled(False)
            self.leftButton4.setEnabled(False)
            self.leftButton5.setEnabled(False)
            self.leftButton6.setEnabled(False)
            return
        else:
            self.ana.semantic.saveMidCodeToFile()
            Dialog = QMessageBox.information(self, "compile success", "编译成功。\n已生成目标代码！", QMessageBox.Yes)

        # 中间代码生成成功后的结果
        self.leftButton2.setEnabled(True)
        self.leftButton3.setEnabled(True)
        self.leftButton4.setEnabled(True)
        self.leftButton5.setEnabled(True)
        self.leftButton6.setEnabled(True)

        # 产生目标代码
        self.ocg = ObjectCodeGenerator(self.ana.semantic.middleCode, self.ana.semantic.symbolTable,
                                       self.ana.semantic.funcTable)
        self.ocg.genMips()
        self.mipsText = ''
        for code in self.ocg.mipsCode:
            self.mipsText += code + '\n'

        # 保存目标代码
        objectCodeFile = open("objectCode.txt", "w")
        objectCodeFile.write(self.mipsText)
        objectCodeFile.close()

        # 填充词法分析结果
        tokens = self.lex.genTokensFromInputBox(self.originCode)
        self.lexTable.setRowCount(len(tokens))
        for i in range(len(tokens)):
            lexItem_name = QTableWidgetItem(tokens[i]['name'])
            lexItem_data = QTableWidgetItem(tokens[i]['data'])
            lexItem_row = QTableWidgetItem(str(tokens[i]['row']))
            lexItem_colum = QTableWidgetItem(str(tokens[i]['colum']))
            self.lexTable.setItem(i, 0, lexItem_name)
            self.lexTable.setItem(i, 1, lexItem_data)
            self.lexTable.setItem(i, 2, lexItem_row)
            self.lexTable.setItem(i, 3, lexItem_colum)
        self.lexTable.setEditTriggers(QAbstractItemView.NoEditTriggers)

        # 填充语法分析结果
        parseResult = self.ana.getParseRst()
        self.gramTable.setRowCount(len(parseResult))
        for i in range(len(parseResult)):
            # 填充状态栈
            stateList = parseResult[i]['stateStack']
            state = ""
            for item in stateList:
                state = state + str(item) + " "
            gramItem_state = QTableWidgetItem(state)
            self.gramTable.setItem(i, 0, gramItem_state)
            # 填充移进栈
            shiftList = parseResult[i]['shiftStr']
            shift = ""
            for item in shiftList:
                shift = shift + str(item['type']) + " "
            gramItem_shift = QTableWidgetItem(shift)
            self.gramTable.setItem(i, 1, gramItem_shift)
            # 填充输入栈
            inputList = parseResult[i]['inputStr']
            input = ""
            for item in inputList:
                input = input + str(item['type']) + " "
            gramItem_input = QTableWidgetItem(input)
            self.gramTable.setItem(i, 2, gramItem_input)
        self.gramTable.setEditTriggers(QAbstractItemView.NoEditTriggers)

        # 填充中间代码
        midCode = self.ana.semantic.middleCode
        self.midCodeTable.setRowCount(len(midCode))
        for i in range(len(midCode)):
            self.midCodeTable.setItem(i, 0, QTableWidgetItem(midCode[i][0]))
            self.midCodeTable.setItem(i, 1, QTableWidgetItem(midCode[i][1]))
            self.midCodeTable.setItem(i, 2, QTableWidgetItem(midCode[i][2]))
            self.midCodeTable.setItem(i, 3, QTableWidgetItem(midCode[i][3]))
        self.midCodeTable.setEditTriggers(QAbstractItemView.NoEditTriggers)

        # 填充函数表
        func = self.ana.semantic.funcTable
        self.funcTable.setRowCount(len(func))
        for i in range(len(func)):
            self.funcTable.setItem(i, 0, QTableWidgetItem(func[i].name))
            self.funcTable.setItem(i, 1, QTableWidgetItem(func[i].type))
            self.funcTable.setItem(i, 2, QTableWidgetItem(func[i].label))
            self.funcTable.setItem(i, 3, QTableWidgetItem(str(func[i].params)))
        self.funcTable.setEditTriggers(QAbstractItemView.NoEditTriggers)

        # 填充符号表
        symbol = self.ana.semantic.symbolTable
        self.symbolTable.setRowCount(len(symbol))
        for i in range(len(symbol)):
            self.symbolTable.setItem(i, 0, QTableWidgetItem(symbol[i].name))
            self.symbolTable.setItem(i, 1, QTableWidgetItem(symbol[i].type))
            self.symbolTable.setItem(i, 2, QTableWidgetItem(str(symbol[i].size)))
            self.symbolTable.setItem(i, 3, QTableWidgetItem(str(symbol[i].offset)))
            self.symbolTable.setItem(i, 4, QTableWidgetItem(symbol[i].place))
            self.symbolTable.setItem(i, 5, QTableWidgetItem(symbol[i].function))
        self.symbolTable.setEditTriggers(QAbstractItemView.NoEditTriggers)

        # 填充目标代码
        self.objectCodeBox.setPlainText(self.mipsText)
        self.objectCodeBox.setReadOnly(True)
