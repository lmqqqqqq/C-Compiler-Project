import re


# 最终项目族的DFA
class ItemSetSpecificationFamily:
    def __init__(self, cfg):
        self.TerminalSymbols = cfg.TerminalSymbols  # 终结符表
        self.NonTerminalSymbols = cfg.NonTerminalSymbols  # 非终结符表
        self.StartSymbol = cfg.StartSymbol  # 是program_
        self.EndSymbol = cfg.EndSymbol  # 是#
        self.Epsilon = cfg.Epsilon

        self.symbols = self.TerminalSymbols + self.NonTerminalSymbols
        self.itemPool = cfg.items  # itemPool：由产生式加点后的项目池
        self.itemSets = []  # 从pool中用GO函数划分  DFA不同的状态
        self.edges = []  # 项目集之间的转移  {'start': I.name, 'symbol': X, 'end': tempItemSet.name}
        self.firstSet = cfg.firstSet
        return

    # 获取左边为NT，dot=0的产生式，用于计算闭包
    def getLeftNT(self, NT):
        rst = []
        for item in self.itemPool:
            if item.left == NT and item.dotPos == 0:
                rst.append(item)
        return rst

    # 获取字符串的first
    def getFirstSet(self, symbols):
        rst = []
        hasEpsAllBefore = 0

        for s in symbols:  # 遍历字符串中的每一个NT和T
            tempSet = [i for i in self.firstSet[s]]  # 该元素的first集
            if self.Epsilon in tempSet:  # 该元素的first集中有eps
                if hasEpsAllBefore == 0:
                    hasEpsAllBefore = 1
                rst.extend([i for i in tempSet if i != self.Epsilon])  # 在列表后追加多个值
            else:
                hasEpsAllBefore = -1
                rst.extend(tempSet)
                break  # 该元素的first集中有无eps，可以终止遍历了

        if hasEpsAllBefore == 1:  # 字符串中的所有元素的first集全有eps
            rst.append(self.Epsilon)
        return rst

    # 求包含item的闭包里的其他项目
    def extendItem(self, item):
        rst = []
        if item.right[item.dotPos]['class'] != 'NT':  # dot后面那个字符不是非终结符
            return rst

        str2BgetFirstSet = []  # dot指向元素的下一个元素开始的字符串
        for rightIdx in range(item.dotPos + 1, len(item.right)):  # 遍历dot指向元素的下一个元素 至 末尾
            str2BgetFirstSet.append(item.right[rightIdx]['type'])
        nextItem = self.getLeftNT(item.right[item.dotPos]['type'])  # 获取左边为NT，dot=0的产生式，用于计算闭包
        str2BgetFirstSet.append(item.terms[0])  # 展望的字符也加上
        tempFirsts = self.getFirstSet(str2BgetFirstSet)  # 求dot指向元素的下一个元素开始的字符串的first集
        for i in nextItem:
            for j in tempFirsts:
                rst.append(Item(i.left, i.right, 0, [j]))  # 往item的闭包里的添加其他项目

        return rst

    # 计算闭包
    def getLR1Closure(self, I):
        rst = []
        rst.extend(I)  # I项目自己肯定在闭包里

        # toString 已包含terms信息
        rstStr = [item.toString() for item in rst]  # 作为key值进行比对是否已有了
        while True:
            isAddItem = 0
            for item in rst:
                right = item.right  # 引用 为了缩短变量长度

                for i in range(len(right) + 1):
                    if item.dotPos == len(right):  # 产生式的dot在最后面
                        continue
                    if right[item.dotPos]['class'] == 'T':
                        continue
                    tempRst = self.extendItem(item)  # 求包含item的闭包里的其他项目
                    for i in tempRst:  # i可能会重复定义
                        tempStr = i.toString()
                        if tempStr not in rstStr:
                            rstStr.append(tempStr)
                            rst.append(i)  # tempRst已经求出闭包里的所有项目，但它是字符串，仅仅是为了方便比对，我们需要的还是rst
                            isAddItem = 1
            if isAddItem == 0:
                break

        return rst

    # 状态转换函数GO GO(I，X) ＝ CLOSURE(J)
    def GO(self, I, X):
        J = []

        # 求GOTO函数的时候不要把ε当终结符/非终结符处理，不要引出ε边
        if len(I.items) == 0 or X == self.Epsilon:  # 项目集里没有项目或者转移为eps
            return J

        for item in I.items:
            if item.dotPos == len(item.right):
                continue
            # 空产生式
            if len(item.right) == 1 and item.right[0] == self.Epsilon:
                continue

            if item.right[item.dotPos]['type'] == X:
                temp = item.nextItem()
                if temp is not None:
                    J.append(temp)
        return self.getLR1Closure(J)

    # 构造项目集规范族
    # 从起始状态的闭包出发，不断调用GO函数生成新的项目族并计算闭包
    def buildFamily(self):
        iS = self.itemSets  # DFA不同的状态
        startI = []
        startI.append(self.itemPool[0])  # 添加起始项目
        iS.append(ItemSet('s0', self.getLR1Closure([startI[0]] + self.extendItem(startI[0]))))  # 起始项目集

        setCnt = 1
        setStrings = {}
        setStrings['s0'] = iS[0].toString()  # dot被去掉了,并加了\n分隔项目
        edgeStrings = []

        while True:
            isBigger = 0  # 是否有加新边或者状态
            for I in iS:  # 遍历当前的所有项目集
                for X in self.symbols:  # 遍历所有的字符(非终结符和终结符)
                    rstGO = self.GO(I, X)  # 生成了一个新的项目集
                    if len(rstGO) == 0:
                        continue
                    tempItemSet = ItemSet('s' + str(setCnt), rstGO)  # 新的项目集

                    if tempItemSet.toString() in setStrings.values():  # 新生成的项目集已经存在了
                        tempItemSet.name = list(setStrings.keys())[list(setStrings.values()).index(tempItemSet.toString())]
                    else:
                        setStrings[tempItemSet.name] = tempItemSet.toString()
                        iS.append(tempItemSet)  # 添加新的项目集
                        isBigger = 1
                        setCnt = setCnt + 1

                    tempEdge = {'start': I.name, 'symbol': X, 'end': tempItemSet.name}
                    tempEdgeStr = tempEdge['start'] + '->' + tempEdge['symbol'] + '->' + tempEdge['end']

                    if tempEdgeStr not in edgeStrings:
                        self.edges.append(tempEdge)
                        edgeStrings.append(tempEdgeStr)
                        isBigger = 1
            if isBigger == 0:
                break
        return

    def prtFamily(self):
        print(' ----------- 打印项目集族 --------------')
        for itemSet in self.itemSets:
            print(itemSet.name)
            for item in itemSet.items:
                rightList = [r['type'] for r in item.right]
                # print(item.left, rightList, item.dotPos, item.terms)
        print('\n')
        for edge in self.edges:
            print(edge['start'], edge['symbol'], edge['end'])
        return


# 最终项目族的DFA的状态, 一个状态可能含有多个项目
class ItemSet:
    def __init__(self, name, items):
        self.name = name  # s0,s1...  该状态的编号
        self.items = items  # 复数个项目 Production  该状态包含的项目

        # 将所有item用string连起来, 方便比较
        self.string = []

        for item in self.items:
            itemStr = item.toString()  # 把产生式的dot进行转化，使产生式变成一个字符串
            if itemStr not in self.string:
                self.string.append(itemStr)

        self.string = sorted(self.string)
        return

    def toString(self):
        return "\n".join(self.string)  # 返回 通过\n连接序列中元素后 生成的新字符串。


# 项目(带点产生式)
# LR0项目集类
class Item:
    def __init__(self, left, right, dotPos=0, terms=['#']):  # terms的默认是[],不是None
        self.right = right  # Node的集合 LR0项目的左侧
        self.left = left  # LR0项目的右侧
        self.dotPos = dotPos  # LR0项目点的位置 用点所在的位置表示同一产生式的不同项目
        self.terms = terms  # LR(1)
        return

    # 返回下一个LR0项目  碰到只产生eps的产生式可能会出问题
    def nextItem(self):
        return Item(self.left, self.right, self.dotPos + 1, self.terms) if self.dotPos <= len(self.right) else None

    # 把产生式的dot进行转化，使产生式变成一个字符串
    def toString(self):
        rst = self.left + '->'
        pos = 0
        for right in self.right:
            if pos == self.dotPos:
                rst += '@'  # 代替点
            rst += right['type'] + ' '
            pos += 1

        if pos == self.dotPos:  # dot在产生式末尾
            rst += '@'

        for term in self.terms:
            rst += term + ' '
        return rst


# 穿线表节点
class CFG:
    def __init__(self):
        self.left = []
        self.prods = []  # 产生式
        self.items = []  # 所有item项 (dot不同的都算)
        self.startProd = None  # 广义文法起始符
        self.firstSet = {}  # first集，{symbol:[],}
        # 保留字
        self.reserved = {
            'if': 'IF',
            'else': 'ELSE',
            'while': 'WHILE',
            'int': 'INT',
            'return': 'RETURN',
            'void': 'VOID'
        }
        # 类别
        self.type = ['seperator', 'operator', 'identifier', 'int']
        # 词法分析所使用的正则表达式
        self.regexs = [
            '\{|\}|\[|\]|\(|\)|,|;'  # 界符
            , '\+|-|\*|/|==|!=|>=|<=|>|<|='  # 操作符
            , '[a-zA-Z][a-zA-Z0-9]*'  # 标识符
            , '\d+'  # 整数
        ]

        self.TerminalSymbols = []  # 终结符表
        self.NonTerminalSymbols = []  # 非终结符表
        self.StartSymbol = None
        self.OriginStartSymbol = None
        self.EndSymbol = None
        self.Epsilon = None
        return

    # 读取产生式
    def readGrammerFile(self, path):
        # 拓展成广义语法
        # 更改语法时需要修改此函数
        self.StartSymbol = 'program_'
        self.OriginStartSymbol = 'program'
        self.prods.append(Item(self.StartSymbol, [{'type': self.OriginStartSymbol, 'class': 'NT', 'name': ''}]))
        self.NonTerminalSymbols.append(self.StartSymbol)
        fd = open(path, 'r')
        self.cntProd = 0  # 产生式数量

        tokens = []  # {'left': token1, 'right': token3}
        while True:
            line = fd.readline().replace('\n', '')  # 读一行
            if not line:
                break
            token1 = []  # 产生式左边
            token3 = []  # 产生式右边(合并左边相同的产生式，因此可能有很多右边)
            token1.append({'type': line, 'class': 'NT', 'name': line})  # 产生式左边
            while True:
                token2 = []  # 一条产生式右边
                line = fd.readline().replace('\n', '')  # 读一行
                if not line:
                    break
                if line[0] == '\t':  # 开头一定得是/t
                    line = line.strip('\t').split(' ')  # 可能产生式右边有多个变量
                    if line[0] == '#':  # 产生式结束
                        tokens.append({'left': token1, 'right': token3})  # 加入一类产生式
                        break

                    self.cntProd = self.cntProd + 1  # 产生式数量+1
                    for item in line:
                        match = 0
                        for regex in self.regexs[0: 2]:  # 匹配是不是操作符和界符
                            result = re.match(regex, item)
                            if result:  # 是操作符和界符
                                match = 1
                                break

                        if match == 1:  # 界符 操作符
                            tempToken2 = {'type': item, 'class': 'T',
                                          'name': self.type[self.regexs.index(regex)].upper()}
                        elif item in self.reserved:  # 保留字
                            tempToken2 = {'type': item, 'class': 'T', 'name': item}
                        elif item == 'id':  # 标识符
                            tempToken2 = {'type': 'IDENTIFIER', 'class': 'T', 'name': 'IDENTIFIER'}
                        elif item == '$':  # 空
                            tempToken2 = {'type': item, 'class': 'T', 'name': item}
                        elif item == 'num':  # 整数
                            tempToken2 = {'type': 'INT', 'class': 'T', 'name': 'INT'}
                        else:  # 变元
                            tempToken2 = {'type': item, 'class': 'NT', 'name': item}
                        token2.append(tempToken2)
                    token3.append(token2)

        for t in tokens:  # {'left': token1, 'right': token3}
            if t['left'][0]['type'] not in self.NonTerminalSymbols:  # 添加变元 产生式左边不是终结符
                self.NonTerminalSymbols.append(t['left'][0]['type'])  # 0：因为token1中只有一个元素

            for rightIdx in range(len(t['right'])):  # 对同一个产生式的左边 遍历每一个右边
                self.prods.append(Item(t['left'][0]['type'], t['right'][rightIdx]))  # 添加每一条产生式
                for rightIdx2 in range(len(t['right'][rightIdx])):  # 添加非变元
                    if t['right'][rightIdx][rightIdx2]['class'] == 'T' and t['right'][rightIdx][rightIdx2]['type'] not in self.TerminalSymbols:
                        self.TerminalSymbols.append(t['right'][rightIdx][rightIdx2]['type'])

        self.EndSymbol = '#'  # 终止符
        self.TerminalSymbols.append(self.EndSymbol)
        self.Epsilon = '$'
        # self.prtGrammer()
        # print(tokens)

        #####
        # prodsFile = open("prods.txt", "w")
        # for prod in self.prods:
        #     prodsFile.write(prod.left)
        #     prodsFile.write(" --> ")
        #     for item in prod.right:
        #         prodsFile.write(item['type'])
        #         prodsFile.write(" ")
        #     prodsFile.write("\n")
        # prodsFile.close()
        #####
        return

    # 计算所有T和NT的first集
    def calFirstSet(self):
        for symbol in self.TerminalSymbols:  # 包括空串
            self.firstSet[symbol] = [symbol]
        for symbol in self.NonTerminalSymbols:
            self.firstSet[symbol] = []
        for symbol in self.NonTerminalSymbols:
            self.calNTFirstSet(symbol)
        return

    # 计算单个NT的first集
    def calNTFirstSet(self, symbol):
        eps = {'class': 'T', 'name': '', 'type': self.Epsilon}
        hasEpsAllBefore = -1  # 前面的非终结符是否全都能推出eps
        prods = [prod for prod in self.prods if prod.left == symbol]  # 左边符合条件的产生式
        if len(prods) == 0:
            return

        is_add = 1
        while is_add:
            is_add = 0
            for prod in prods:  # 遍历符合的产生式
                hasEpsAllBefore = 0

                for right in prod.right:  # 遍历产生式右边的每个符号
                    # 2. 若X∈VN，且有产生式X->a…，a∈VT，则 a∈FIRST(X)
                    #    X->ε,则ε∈FIRST(X)
                    if right['class'] == 'T' or (right['type'] == self.Epsilon and len(prod.right) == 1):  # A->epsilon
                        # 有就加
                        if right['type'] not in self.firstSet[symbol]:
                            self.firstSet[symbol].append(right['type'])
                            is_add = 1
                        break

                    # 3. 对NT, 之前已算出来过, 但有可能是算到一半的
                    if len(self.firstSet[right['type']]) == 0:
                        if right['type'] != symbol:  # 防止陷入死循环
                            self.calNTFirstSet(right['type'])  # 先算NT自己的first集

                    # X->Y…是一个产生式且Y ∈VN  则把FIRST(Y)中的所有非空符号串ε元素都加入到FIRST(X)中。
                    if self.Epsilon in self.firstSet[right['type']]:
                        hasEpsAllBefore = 1

                    for f in self.firstSet[right['type']]:
                        if f != self.Epsilon and f not in self.firstSet[symbol]:
                            self.firstSet[symbol].append(f)
                            is_add = 1

                # 到这里说明整个产生式已遍历完毕 看是否有始终能推出eps
                # 中途不能推出eps的已经break了   (例如Ba还是会来到这里，加e可能会有问题)
                # 所有right(即Yi) 能够推导出ε,(i=1,2,…n)，则
                if hasEpsAllBefore == 1:
                    if self.Epsilon not in self.firstSet[symbol]:
                        self.firstSet[symbol].append(self.Epsilon)
                        is_add = 1

        return

    # 给产生式加点，转化为项目item LR0
    def getDotItems(self):
        for prod in self.prods:
            if len(prod.right) == 1 and prod.right[0]['type'] == self.Epsilon:  # 产生式右边只有eps
                self.items.append(Item(prod.left, prod.right, 0, ['#']))  # 只用把dot加在eps前就行了
                continue
            for i in range(len(prod.right) + 1):
                self.items.append(Item(prod.left, prod.right, i, ['#']))
        return

    # 输出测试
    def prtGrammer(self):
        print('------------ 打印语法详情 --------------')
        print("产生式个数", len(self.prods), self.cntProd)

        print('非终结符个数:', len(self.NonTerminalSymbols), '终结符个数:', len(self.TerminalSymbols))
        print(self.NonTerminalSymbols)
        print(self.TerminalSymbols)

        for item in self.items:
            rightList = [r['type'] for r in item.right]
            print(item.left, rightList, item.dotPos)  #
        return

    # 输出测试
    def prtFirstSet(self):
        print('---------- 打印First集 --------------')
        for key in self.firstSet.keys():
            prtList = [value for value in self.firstSet[key]]
            print(key, prtList)
        return
