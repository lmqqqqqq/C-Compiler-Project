# C-Compiler-Project

## 1 Requirements Analysis

### 1.1 Function

- Conduct lexical and syntax analysis, outputting First sets, Follow sets, Action table, Goto table, LR1 parsing table, and code parsing process, saving them as files
- Include symbol table and function table, capable of generating intermediate code
- Generate assembly code based on the generated intermediate code using register selection algorithms
- Support for arrays and function calls in source code

### 1.2 Input & Output Example

#### 1.2.1 Input

```c
int program(int a,int b,int c)
{
    int i;
    int j;
    i=0;
    if(a>(b+c))
    {
        j=a+(b*c+1);
    }
    else
    {
        j=a;
    }
    while(i<=100)
    {
        i=j*2;
        j=j+1;
    }
    return i;
}
int demo(int a)
{
    a=a+2;
    return a*2;
}
void main(void)
{
    int a[2][2];
    a[0][0]=3;
    a[0][1]=a[0][0]+1;
    a[1][0]=a[0][0]+a[0][1];
    a[1][1]=program(a[0][0],a[0][1],demo(a[1][0]));
    return;
}
```

#### 1.2.2 Output

```assembly
.data

.text
    addiu $sp, $zero, 0x10018000
    or $fp, $sp, $zero
    jal  main
    jal  programEnd

f1:
    lw $7, 0($fp)
    lw $8, 4($fp)
    lw $9, 8($fp)
    sub $fp,$fp,12
    add $10,$zero,0
    add $11,$8,$9
    sgt $12,$7,$11
    bgt $12,$zero,l1
    j l2
l1:
    mul $13,$8,$9
    add $14,$13,1
    add $15,$7,$14
    add $16,$zero,$15
    j l3
l2:
    add $16,$zero,$7
l3:
l6:
    add $a2,$zero,100
    sgt $17,$10,$a2
    xori $17,$17,1
    bgt $17,$zero,l4
    j l5
l4:
    add $a2,$zero,2
    mul $18,$16,$a2
    add $10,$zero,$18
    add $19,$16,1
    add $16,$zero,$19
j l6
l5:
    add $v0,$zero,$10
    jr $ra

f2:
    lw $20, 0($fp)
    sub $fp,$fp,4
    add $21,$20,2
    add $20,$zero,$21
    add $a2,$zero,2
    mul $22,$20,$a2
    add $v0,$zero,$22
    jr $ra
main:
    add $23,$zero,3
    add $24,$zero,4
    add $25,$zero,2
    sub $sp,$sp,4
    sw $ra, 0($sp)
    sub $sp,$sp,4
    sw $ra, 0($sp)
    add $fp,$fp,4
    sw $25, 0($fp)
    jal  f2
    lw $ra, 0($sp)
    add $sp,$sp,4
    add $7,$zero,$v0
    add $fp,$fp,12
    sw $23, 0($fp)
    sw $24, 4($fp)
    sw $7, 8($fp)
    jal  f1
    lw $ra, 0($sp)
    add $sp,$sp,4
    add $8,$zero,$v0
    add $23,$zero,$8
    jr $ra

programEnd:
    nop

```

## 2 Outline Design

### 2.1 Task Breakdown

Based on the requirements analysis, the compiler should be divided into the following modules:

1. Lexical Analyzer
2. Syntax Analyzer
3. Semantic Analyzer
4. Intermediate Code Generator
5. Assembly Code Generator
6. Graphical User Interface Module  

### 2.2 Data Structure Design

#### 2.2.1 Lexical Analyzer

Lexical analysis is the first step in the processing pipeline. It sequentially scans the characters in the source file, matching them with a finite automaton corresponding to lexical tokens. This process generates various lexical tokens such as identifiers, keywords, constants, as well as operators, commas, semicolons, and other delimiters.

![img](./img/1.png)

#### 2.2.2 Syntax Analyzer

Its main function is to obtain the LR1 parsing table. This syntax analyzer processes the input productions, first transforming the grammar into an augmented grammar S'. It then utilizes the augmented grammar to generate the First set and Follow set, concurrently generating LR0 item sets. By computing the closure of the item sets, it generates a DFA, obtaining the GOTO table and ACTION table. This process results in obtaining the LR1 parsing table.

![img](./img/2.png)

#### 2.2.3 Semantic Analyzer

Perform semantic analysis based on the token stream and LR1 parsing table. During the semantic analysis with a single scan, it is necessary to generate a syntax tree where nodes are endowed with different attributes. Throughout the semantic analysis process, the variable table and function table need to be continually used and updated. Guided by semantic rules and LR1 parsing table, reduce the token stream to obtain intermediate code.

![img](./img/3.png) 

#### 2.2.3 Assembly Code Generator 

After obtaining the intermediate code, it can be translated into MIPS instructions, where register allocation is performed based on the register allocation algorithm.

## 3 Detailed Design

### 3.1 Lexical Analyzer

#### 3.1.1 Source Code Preprocessing

The implementation of the lexical analyzer relies primarily on the regular expression library `re` provided in Python to match token characters. For the source code file, the first step is to remove comments from the source code file, primarily achieved by using the function `findall`.

```python
def removeAnnotation(self, codes):  # 移除源代码中的注释
    annotation = re.findall('//.*?\n', codes, flags=re.DOTALL)  # .*?非贪婪
    if len(annotation) > 0:
        codes = codes.replace(annotation[0], "")  # 将注释替换成空白
    annotation = re.findall('/\*.*?\*/', codes, flags=re.DOTALL)
    if len(annotation) > 0:
        codes = codes.replace(annotation[0], "")
    ret = codes.strip()
    return ret

```

#### 3.1.2 Token Recognition

For recognizing syntax words in the preprocessed source code, a finite automaton is needed. Similarly, the `findall` function in the `re` library of Python can be used to identify all matching syntax words. 

Firstly, it is necessary to define regular expressions for potential syntax words. Define four regular expressions for syntax words that may appear in the source code: delimiters, operators, identifiers, and integers.

```python
self.regexs = [
    '\{|\}|\[|\]|\(|\)|,|;'  # 界符
    , '\+|-|\*|/|==|!=|>=|<=|>|<|='  # 操作符
    , '[a-zA-Z][a-zA-Z0-9]*'  # 标识符
    , '\d+'  # 整数
]

```

The words obtained through regular expression matching are classified based on their categories. The classification includes filling in the category of the word, the value of the word, and the position of the word in the source code file.

### 3.2 Syntax Analyzer

#### 3.2.1 First Set

LR1 algorithm requires the FIRST set for every left-hand side of the production. To obtain the FIRST set for all non-terminals, the algorithm for calculating the FIRST set for a single non-terminal (NT) is as follows:

Apply the following rules until the FIRST set for every non-terminal no longer increases:

1. If X is a terminal, then FIRST(X) = {X}.
2. If X is a non-terminal and has a production X → a…, add a to FIRST(X). If there is a production S → ε, add ε to FIRST(X).
3. If X → Y… is a production where Y is a non-terminal, add all non-empty elements from FIRST(Y) to FIRST(X). If X → Y1, Y2, …, Yk is a production, and Y<sub>1</sub>, Y<sub>2</sub>, …, Y<sub>i-1</sub> are all non-terminals, and for any 1 <= j <= i-1, FIRST(Y<sub>j</sub>) contains ε, then add all non-ε elements from FIRST(Y<sub>i</sub>) to FIRST(X). In particular, if all FIRST(Y<sub>j</sub>) for j = 1, 2, …, k contain ε, add ε to FIRST(X).

```python
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
```

After calculating the first set for a single non-terminal (NT), you can use these results to compute the first set for all terminals (T) and non-terminals (NT).

After calculating the first set for all terminals (T) and non-terminals (NT), you can use this result to compute the first set for a string, which is the ultimate goal.

#### 3.2.2 LR0 Items

Before constructing the DFA, it is necessary to add a dot to the productions to transform them into LR0 item sets. Adding a dot to a production is essentially indicating the position of the dot on the right-hand side of the production.

#### 3.2.3 Closure of LR1 Item Sets

The construction of the closure of LR1 item sets is crucial for generating the DFA. The algorithm for computing the closure is as follows:

1. Any item in I belongs to CLOSURE(I).
2. If A → α⋅Bβ belongs to CLOSURE(I), then B → ⋅γ also belongs to CLOSURE(I). Repeat the above steps until CLOSURE(I) no longer increases.

Loop through all productions and check each one. If the dot is at the end of a production, move to the next production. When there are non-terminals after the dot, compute the items for the non-terminals as if they were the left-hand side of the production, and add them to the closure. In other words, look for all productions of the form A → ⋅B and add them to the set. Repeat the process.

```python
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

```

#### **3.2.4** DFA

In the process of calculating the canonical collection of LR1 items, a state transition function `GO` is generated. This function indicates, for a given DFA state, the state to which it transitions when encountering a certain symbol.

Given the ability to compute the closure of LR1 item sets and implement the state transition function `GO`, the construction of the DFA is achieved by starting from the closure of the initial state. Repeatedly invoke the `GO` function to generate new item sets and compute their closures, continuing this process until no new item sets are generated. This completes the construction of the DFA.

```python
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

```

#### 3.2.5 LR1 Parsing Table

The essence of the LR1 parsing table is to establish the ACTION and GOTO tables based on the generated DFA, describing the actions (shift, reduce, accept, error) to be taken when encountering the next input character in the current state, as well as the next state.

The algorithm for constructing the LR1 parsing table is as follows:

1. If the item [A→α⋅aβ, b] belongs to I<sub>k</sub> and GO(I<sub>k</sub>, a) = I<sub>j</sub>, where a is a terminal, set ACTION[k, a] to s<sub>j</sub>, meaning shift to state j with symbol a.
2. If the item [A→α⋅, a] belongs to I<sub>k</sub>, set ACTION[k, a] to r<sub>j</sub>, meaning reduce with production A→α using the j-th production.
3. If the item [S'→S⋅,#] belongs to I<sub>k</sub>, set ACTION[k, #] to acc, meaning accept.
4. If GO(I<sub>k</sub>, A) = I<sub>j</sub>, set GOTO[k, A] to j, meaning go to state j with non-terminal A.
5. For other cases where the above rules do not apply, fill in with error, indicating an error.

```python
def getTables(self):
    self.rst = []
    for e in self.edges:
        if e['symbol'] in self.TerminalSymbols:  # symbol是终结符，构建ACTION表
            self.M[e['start']][e['symbol']] = 'shift ' + e['end']

        if e['symbol'] in self.NonTerminalSymbols:  # symbol是非终结符，构建GOTO表
            self.M[e['start']][e['symbol']] = 'goto ' + e['end']

    for I in self.itemSets:
        for item in I.items:
            if item.dotPos == len(item.right):  # dot在最后,要规约了
                if item.left == self.OriginStartSymbol and item.terms[0] == '#':
                    if self.M[I.name][item.terms[0]] != ' ':
                        print('LR(1)分析表有多重入口！')
                    self.M[I.name][item.terms[0]] = 'acc'
                else:
                    if self.M[I.name][item.terms[0]] != ' ':
                        print('LR(1)分析表有多重入口！')
                    self.M[I.name][item.terms[0]] = 'reduce ' + str(self.item2prodIdx(item))
                continue

            if len(item.right) == 1 and item.right[0]['type'] == '$':
                if item.left == self.OriginStartSymbol and item.terms[0] == '#':
                    if self.M[I.name][item.terms[0]] != ' ':
                        print('LR(1)分析表有多重入口！')
                    self.M[I.name][item.terms[0]] = 'acc'
                else:
                    if self.M[I.name][item.terms[0]] != ' ':
                        print('LR(1)分析表有多重入口！')
                    self.M[I.name][item.terms[0]] = 'reduce ' + str(self.item2prodIdx(item))
                continue
    return

```

#### 3.2.6 Token Stream Reduction

With the GOTO table and ACTION table, for a given state and the result of lexical analysis, we only need to consult the tables to determine the next action.

The specific process is as follows:

1. Read a symbol from the lexical analysis result.
2. Look up the tables to determine the next action:
   - If it is a shift, push the current symbol and the state to which it should be shifted onto the stack.
   - If it is an accept action, end the reduction process.
   - If it is a reduce action, determine which production to use for reduction. Pop symbols from the stack based on the number of symbols on the right-hand side of the production. Then, based on the current symbol and the top state on the stack, consult the GOTO table for the next state.
   - If the table lookup for the current state and symbol does not yield a valid action, report an error.

Continue this process until the grammar's start symbol is obtained through reduction.

### 3.3 Semantic Analyzer

During syntax analysis, semantic rules are calculated simultaneously without the need to explicitly construct a syntax tree. In bottom-up syntax analysis, when a production is used for reduction, the corresponding semantic rules are calculated, completing the semantic analysis and code generation tasks.

```python
if nt == 'arrayDeclaration':
    if len(r) == 3:
        n = Node()
        n.name = nt
        n.type = 'int array'
        n.dims = [int(shiftStr[-2]['data'])]  # 数组维度
        self.sStack.append(n)
        # self.prtNodeCode(n)
    elif len(r) == 4:
        n = self.sStack.pop(-1)
        n.name = nt
        n.type = 'int array'
        n.dims.insert(0, int(shiftStr[-3]['data']))  # 数组维度
        self.sStack.append(n)
        # self.prtNodeCode(n)

# array -> id [ expression ] | array [ expression ]
if nt == 'array':
    expression_n = self.sStack.pop(-1)
    self.calExpression(expression_n)  # 计算表达式的值
    array_n = copy.deepcopy(self.sStack[-1])  # 深拷贝

    if shiftStr[-4]['type'] == 'array':  # -> array [ expression ]
        self.sStack.pop(-1)
        expression_n.name = 'array'
        expression_n.arrname = array_n.arrname  # 数组原始变量名字
        expression_n.position = copy.deepcopy(array_n.position)
        expression_n.position.append(expression_n.place if expression_n.place else expression_n.data)
        expression_n.place = array_n.place  # 数组对应的中间变量名字
        expression_n.type = 'array'
        self.sStack.append(expression_n)

    else:  # -> id [ expression ]
        expression_n.name = 'array'
        expression_n.arrname = shiftStr[-4]['data']
        s = shiftStr[-4]['data']  # 拿到变量名称
        nTmp = self.findSymbol(s, self.curFuncSymbol.label)  # python 可变对象传引用
        if nTmp == None:
            print('使用未定义的数组变量!')
            self.semanticRst = False
            self.semanticErrMsg = "未定义的数组变量：" + shiftStr[-4][
                'data']  # 在" + str(shiftStr[-4]['row']) + "行" + str(shiftStr[-4]['colum']) + "列"
            return
        expression_n.position.append(expression_n.place if expression_n.place else expression_n.data)
        expression_n.place = s  # 数组对应的中间变量
        expression_n.type = 'array'
        self.sStack.append(expression_n)

```

### 3.4 Assembly Code Generator

The task of generating assembly code involves using the obtained intermediate code, allocating registers based on a register allocation algorithm, and gradually transforming the intermediate code into assembly code.

#### 3.4.1 Register Allocation and Deallocation

During the process of register allocation, the following principles are considered:

1. Preferably use a register exclusively occupied by variable B.
2. Preferably use an available register.
3. Preemptively use a non-available register.

The register allocation algorithm is as follows (assuming the intermediate code is in the form A := B op C):

1. If the current value of B is in a register R<sub>i</sub>, where RVALUE[R<sub>i</sub>] only contains B, and either B and A are the same identifier or the current value of B will not be referenced after executing the quadruple A := B op C, select R<sub>i</sub> as the required register R and proceed to step 4.
2. If there are still unallocated registers, choose one R<sub>i</sub> as the required register R and proceed to step 4.
3. Choose a register R<sub>i</sub> from the already allocated registers as the required register R. It is preferable to select R<sub>i</sub> such that the variable occupying R<sub>i</sub> has its value also stored in the variable's storage location or will not be referenced in the basic block until the distant future.
4. Generate store instructions for the variables in R<sub>i</sub>: If the address array AVALUE[V] for variable V indicates that V is also stored outside of register R, no store instruction is needed. If V is equal to A and not equal to B or C, no store instruction is needed. If V will not be used after this point, no store instruction is needed. Otherwise, generate the target code.

```python
def getRegister(self, identifier, codes):
    if identifier[0] != 't':
        return identifier
    if identifier in self.varStatus and self.varStatus[identifier] == 'reg':
        for key in self.regTable:
            if self.regTable[key] == identifier:
                return key
    # print('---------------')
    # print(identifier + '正在申请寄存器')
    # print(self.regTable)
    # print(self.varStatus)

    while True:
        for key in self.regTable:
            if self.regTable[key] == '':
                self.regTable[key] = identifier
                self.varStatus[identifier] = 'reg'
                return key
        self.freeRegister(codes)

# 释放一个寄存器
def freeRegister(self, codes):
    # 提取出使用了 reg 的变量, 形式如t1, t2, ...
    varRegUsed = list(filter(lambda x: x != '', self.regTable.values()))

    # 统计这些变量后续的使用情况
    varUsageCnts = {}
    for code in codes:
        # print(code)
        for item in code:
            # print(item)
            tmp = str(item)
            if tmp[0] == 't':  # 是个变量
                if tmp in varRegUsed:
                    if tmp in varUsageCnts:
                        varUsageCnts[tmp] += 1
                    else:
                        varUsageCnts[tmp] = 1

    # print('===\n', 'varUsageCnts:', varUsageCnts, '\n===\n')

    sys.stdout.flush()
    flag = False

    # 找出之后不会使用的变量所在的寄存器
    for var in varRegUsed:
        if var not in varUsageCnts:
            for reg in self.regTable:
                if self.regTable[reg] == var:
                    self.regTable[reg] = ''
                    self.varStatus[var] = 'memory'
                    flag = True
    if flag:
        return

    # 释放最少使用的寄存器，
    sorted(varUsageCnts.items(), key=lambda x: x[1])
    varFreed = list(varUsageCnts.keys())[0]
    for reg in self.regTable:
        if self.regTable[reg] == varFreed:
            for item in self.symbolTable:
                if item.place == varFreed:  # t1, t2, ...
                    self.mipsCode.append('addi $at, $zero, 0x{}'.format(self.DATA_SEGMENT))
                    self.mipsCode.append('sw {}, {}($at)'.format(reg, item.offset))
                    self.regTable[reg] = ''
                    self.varStatus[varFreed] = 'memory'
                    return

```

#### 3.4.2 Generate Assembly Code

The assembly code generation algorithm is as follows:

For each quadruple i: A := B op C, perform the following steps:

1. Call the function getReg with the quadruple i: A := B op C as a parameter, and obtain a register R to be used for storing A.

2. Determine the storage locations B' and C' for the current values of B and C using AVALUE[B] and AVALUE[C]. If their current values are in registers, take those registers as B' and C'.

3. If B' is not equal to R, generate the target code:

   ```assembly
   LD  R, B'
   OP  R, C'
   ```

   Otherwise, generate the target code 

   ```assembly
   OP R, C'
   ```

   If B' or C' is equal to R, remove R from AVALUE[B] or AVALUE[C].

4. Set AVALUE[A] = {R} and RVALUE[R] = {A}.

5. If the current values of B or C are not referenced in the basic block after this point, are not live variables after the basic block exit, and their current values are in some register R<sub>k</sub>, then remove B or C from RVALUE[R<sub>k</sub>] and R<sub>k</sub> from AVALUE[B] or AVALUE[C], ensuring that the register is no longer occupied by B or C.
