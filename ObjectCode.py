import copy
import sys


# 目标代码生成器
class ObjectCodeGenerator:
    def __init__(self, middleCode, symbolTable, funcTable):
        self.middleCode = copy.deepcopy(middleCode)  # 中间代码
        self.symbolTable = copy.deepcopy(symbolTable)  # 符号表
        self.funcNameTable = []  # 函数名表
        for f in funcTable:
            self.funcNameTable.append(f.name)

        self.mipsCode = []  # 目标代码
        self.regTable = {'$' + str(i): '' for i in range(7, 26)}  # 寄存器状态表 如'$7': ''
        self.varStatus = {}  # 记录变量是在寄存器当中还是内存当中 变量状态表

        self.DATA_SEGMENT = 10010000  # 数据段偏移量
        self.STACK_OFFSET = 8000  # 堆栈偏移量
        return

    # 申请一个寄存器
    def getRegister(self, identifier, codes):
        if identifier[0] != 't':  # 即arg1 B在寄存器中 或者是常数
            return identifier
        if identifier in self.varStatus and self.varStatus[identifier] == 'reg':  # 中间变量在变量状态表中有并且中间变量在寄存器中
            for key in self.regTable:  # 遍历寄存器
                if self.regTable[key] == identifier:  # 寄存器中的是中间变量
                    return key
        # print('---------------')
        # print(identifier + '正在申请寄存器')
        # print(self.regTable)
        # print(self.varStatus)

        while True:
            for key in self.regTable:
                if self.regTable[key] == '':  # 找到一个空的寄存器
                    self.regTable[key] = identifier  # 该寄存器中存放中间变量
                    self.varStatus[identifier] = 'reg'
                    return key
            self.freeRegister(codes)  # 没找到空的,释放一个寄存器

    # 释放一个寄存器
    def freeRegister(self, codes):
        # 提取出使用了 reg 的变量, 形式如t1, t2, ...
        varRegUsed = list(filter(lambda x: x != '', self.regTable.values()))  # filiter筛选出来符合条件的数据

        # 统计这些变量后续的使用情况
        varUsageCnts = {}
        for code in codes:  # 遍历之后的中间代码
            # print(code)
            for item in code:  # 遍历每一条四元式中的元素
                # print(item)
                tmp = str(item)
                if tmp[0] == 't':  # 是个变量
                    if tmp in varRegUsed:  # 给tmp中间变量的后续使用情况计数
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
                        self.regTable[reg] = ''  # 寄存器清除那个之后不会使用的中间变量
                        self.varStatus[var] = 'memory'  # 中间变量存放在内存中了
                        flag = True
        if flag:  # 找到了之后不会使用的变量所在的寄存器
            return

        # 释放最少使用的寄存器，
        sorted(varUsageCnts.items(), key=lambda x: x[1])  # 按map的value来排序
        varFreed = list(varUsageCnts.keys())[0]
        for reg in self.regTable:
            if self.regTable[reg] == varFreed:
                for item in self.symbolTable:
                    if item.place == varFreed:  # t1, t2, ...
                        self.mipsCode.append('addi $at, $zero, 0x{}'.format(self.DATA_SEGMENT))  # $at 一号寄存器
                        self.mipsCode.append('sw {}, {}($at)'.format(reg, item.offset))  # 存数指令, reg->mem[at+offset]
                        self.regTable[reg] = ''
                        self.varStatus[varFreed] = 'memory'
                        return

        return

    # 生成mips目标代码
    def genMips(self):
        mc = self.mipsCode
        dc = self.middleCode

        dc.insert(0, ('call', '_', '_', 'programEnd'))
        dc.insert(0, ('call', '_', '_', 'main'))

        mc.append('.data')  # 数据段 存放数组
        for s in self.symbolTable:
            if s.type == 'int array':  # 数组的中间变量名
                size = 4  # 单位字节
                for dim in s.dims:
                    size *= int(dim)  # 数组大小
                mc.append('    ' + s.place + ': .space ' + str(size))

        mc.append('')
        mc.append('.text')  # 代码段
        mc.append('    addiu $sp, $zero, 0x{}'.format(self.DATA_SEGMENT + self.STACK_OFFSET))  # sp = 0 + DATA_SEGMENT + STACK_OFFSET
        mc.append('    or $fp, $sp, $zero')  # fp = sp or 0

        while dc:  # 中间代码还有
            code = dc.pop(0)
            tmp = []
            for item in code:
                if item == 'v0':  # 子程序返回值的寄存器
                    tmp.append('$v0')
                else:
                    tmp.append(item)
            code = tmp  # 仅仅是把含有v0的中间代码处理了一下

            if code[0] == ':=':
                src = self.getRegister(code[1], dc)
                dst = self.getRegister(code[3], dc)
                mc.append('    add {},$zero,{}'.format(dst, src))  # dst = 0 +src

            elif code[0] == '[]=':  # []=, t21, _, t17[t22]
                src = self.getRegister(code[1], dc)  # t21的寄存器
                base = code[3][: code[3].index('[')]  # t17
                offset = code[3][code[3].index('[') + 1: -1]  # t22
                dst_offset = self.getRegister(offset, dc)  # t22的寄存器
                mc.append('    la $v1,{}'.format(base))  # 将base地址的值加载到v1中
                mc.append('    mul {},{},4'.format(dst_offset, dst_offset))  # offset乘4
                mc.append('    addu {},{},$v1'.format(dst_offset, dst_offset))  # dst_offset += base
                mc.append('    sw {},'.format(src) + '0({})'.format(dst_offset))  # src -> mem[dst_offset+0]

            elif code[0] == '=[]':  # =[], t17[t23], -, t24
                dst = self.getRegister(code[3], dc)  # t24的寄存器
                base = code[1][: code[1].index('[')]  # t17
                offset = code[1][code[1].index('[') + 1: -1]  # t23
                src_offset = self.getRegister(offset, dc)  # t23的寄存器
                mc.append('    la $v1,{}'.format(base))  # 将base地址的值加载到v1中
                mc.append('    mul {},{},4'.format(src_offset, src_offset))  # offset乘4
                mc.append('    addu {},{},$v1'.format(src_offset, src_offset))  # src_offset += base
                mc.append('    lw {},'.format(dst) + '0({})'.format(src_offset))  # mem[src_offset+0] -> dst

            # function or label
            elif code[1] == ':':
                if code[0] in self.funcNameTable or code[0][0] == 'f':  # is a function definition
                    mc.append('')  # empty line
                mc.append('{}:'.format(code[0]))

            # 跳转到函数的label处
            elif code[0] == 'call':
                mc.append('    jal  {}'.format(code[3]))

            # actual arg of a function call
            elif code[0] == 'push':  # push, _, 0, t31
                if code[3] == 'ra':  # return addr
                    mc.append('    sw $ra, {}($fp)'.format(code[2]))  # ra -> mem[fp+ ]
                else:
                    register = self.getRegister(code[3], dc)
                    if str(register)[0] != '$':  # 将寄存器变为$a0
                        mc.append("    add $a0, $zero, {}".format(register))
                        register = '$a0'
                    mc.append('    sw {}, {}($fp)'.format(register, code[2]))

            # get args inside the function
            elif code[0] == 'pop':  # pop, _, 0, t1
                if code[3] == 'ra':
                    mc.append('    lw $ra, {}($fp)'.format(code[2]))  # ra <- mem[fp+ ]
                else:
                    register = self.getRegister(code[3], dc)
                    mc.append('    lw {}, {}($fp)'.format(register, code[2]))

            # store var from reg to memory
            elif code[0] == 'store':  # store, _, 0, ra
                if code[3] == 'ra':
                    mc.append('    sw $ra, {}($sp)'.format(code[2]))  # ra -> mem[sp+ ]
                else:
                    register = self.getRegister(code[3], dc)
                    if str(register)[0] != '$':
                        mc.append("    add $a0,$zero,{}".format(register))
                        register = '$a0'
                    mc.append('    sw {}, {}($sp)'.format(register, code[2]))

            # load var from memory to reg
            elif code[0] == 'load':  # load, _, 0, ra
                if code[3] == 'ra':
                    mc.append('    lw $ra, {}($sp)'.format(code[2]))
                else:
                    register = self.getRegister(code[3], dc)
                    mc.append('    lw {}, {}($sp)'.format(register, code[2]))

            # jump instruction
            elif code[0] == 'j':  # j, _, _, l6
                mc.append('    j {}'.format(code[3]))

            elif code[0] == 'j>':  # j>, t13, 0, l4
                arg1 = self.getRegister(code[1], dc)
                mc.append('    bgt {},$zero,{}'.format(arg1, code[3]))  # bgt: 大于0跳转

            elif code[0] == 'return':
                mc.append('    jr $ra')  # 寄存器绝对跳转

            # algorithm operations, has 3 oprand
            else:
                if code[0] == '+':  # +, t23, 1, t23
                    if code[1] == 'fp':
                        mc.append("    add $fp,$fp,{}".format(code[2]))
                    elif code[1] == 'sp':
                        mc.append("    add $sp,$sp,{}".format(code[2]))
                    else:
                        arg1 = self.getRegister(code[1], dc)
                        arg2 = self.getRegister(code[2], dc)
                        arg3 = self.getRegister(code[3], dc)
                        if str(arg1)[0] != '$':  # 分配的寄存器不是$7-25
                            mc.append("    add $a1,$zero,{}".format(arg1))
                            arg1 = '$a1'
                        mc.append("    add {},{},{}".format(arg3, arg1, arg2))

                elif code[0] == '-':
                    if code[1] == 'fp':
                        mc.append("    sub $fp,$fp,{}".format(code[2]))
                    elif code[1] == 'sp':
                        mc.append("    sub $sp,$sp,{}".format(code[2]))
                    else:
                        arg1 = self.getRegister(code[1], dc)
                        arg2 = self.getRegister(code[2], dc)
                        arg3 = self.getRegister(code[3], dc)
                        if str(arg1)[0] != '$':
                            mc.append("    add $a1,$zero,{}".format(arg1))
                            arg1 = '$a1'
                        if str(arg2)[0] != '$':
                            mc.append("    add $a2,$zero,{}".format(arg2))
                            arg2 = '$a2'
                        mc.append("    sub {},{},{}".format(arg3, arg1, arg2))

                elif code[0] == '*':
                    arg1 = self.getRegister(code[1], dc)
                    arg2 = self.getRegister(code[2], dc)
                    arg3 = self.getRegister(code[3], dc)
                    if str(arg1)[0] != '$':
                        mc.append("    add $a1,$zero,{}".format(arg1))
                        arg1 = '$a1'
                    if str(arg2)[0] != '$':
                        mc.append("    add $a2,$zero,{}".format(arg2))
                        arg2 = '$a2'
                    mc.append("    mul {},{},{}".format(arg3, arg1, arg2))

                elif code[0] == '/':
                    arg1 = self.getRegister(code[1], dc)
                    arg2 = self.getRegister(code[2], dc)
                    arg3 = self.getRegister(code[3], dc)
                    if str(arg1)[0] != '$':
                        mc.append("    add $a1,$zero,{}".format(arg1))
                        arg1 = '$a1'
                    if str(arg2)[0] != '$':
                        mc.append("    add $a2,$zero,{}".format(arg2))
                        arg2 = '$a2'
                    mc.append("    div {},{},{}".format(arg3, arg1, arg2))

                elif code[0] == '%':
                    arg1 = self.getRegister(code[1], dc)
                    arg2 = self.getRegister(code[2], dc)
                    arg3 = self.getRegister(code[3], dc)
                    if str(arg1)[0] != '$':
                        mc.append("    add $a1,$zero,{}".format(arg1))
                        arg1 = '$a1'
                    if str(arg2)[0] != '$':
                        mc.append("    add $a2,$zero,{}".format(arg2))
                        arg2 = '$a2'
                    mc.append("    div {},{},{}".format(arg3, arg1, arg2))
                    mc.append("    mfhi {}".format(arg3))

                elif code[0] == '<':
                    arg1 = self.getRegister(code[1], dc)
                    arg2 = self.getRegister(code[2], dc)
                    arg3 = self.getRegister(code[3], dc)
                    if str(arg1)[0] != '$':
                        mc.append("    add $a1,$zero,{}".format(arg1))
                        arg1 = '$a1'
                    if str(arg2)[0] != '$':
                        mc.append("    add $a2,$zero,{}".format(arg2))
                        arg2 = '$a2'
                    mc.append("    slt {},{},{}".format(arg3, arg1, arg2))  # if(arg1<arg2)  arg3=1 else arg3=0

                elif code[0] == '>':
                    arg1 = self.getRegister(code[1], dc)
                    arg2 = self.getRegister(code[2], dc)
                    arg3 = self.getRegister(code[3], dc)
                    if str(arg1)[0] != '$':
                        mc.append("    add $a1,$zero,{}".format(arg1))
                        arg1 = '$a1'
                    if str(arg2)[0] != '$':
                        mc.append("    add $a2,$zero,{}".format(arg2))
                        arg2 = '$a2'
                    mc.append("    sgt {},{},{}".format(arg3, arg1, arg2))

                elif code[0] == '!=':
                    arg1 = self.getRegister(code[1], dc)
                    arg2 = self.getRegister(code[2], dc)
                    arg3 = self.getRegister(code[3], dc)
                    if str(arg1)[0] != '$':
                        mc.append("    add $a1,$zero,{}".format(arg1))
                        arg1 = '$a1'
                    if str(arg2)[0] != '$':
                        mc.append("    add $a2,$zero,{}".format(arg2))
                        arg2 = '$a2'
                    mc.append("    sne {},{},{}".format(arg3, arg1, arg2))

                elif code[0] == '==':
                    arg1 = self.getRegister(code[1], dc)
                    arg2 = self.getRegister(code[2], dc)
                    arg3 = self.getRegister(code[3], dc)
                    if str(arg1)[0] != '$':
                        mc.append("    add $a1,$zero,{}".format(arg1))
                        arg1 = '$a1'
                    if str(arg2)[0] != '$':
                        mc.append("    add $a2,$zero,{}".format(arg2))
                        arg2 = '$a2'
                    mc.append("    seq {},{},{}".format(arg3, arg1, arg2))

                elif code[0] == '<=':
                    arg1 = self.getRegister(code[1], dc)
                    arg2 = self.getRegister(code[2], dc)
                    arg3 = self.getRegister(code[3], dc)
                    if str(arg1)[0] != '$':
                        mc.append("    add $a1,$zero,{}".format(arg1))
                        arg1 = '$a1'
                    if str(arg2)[0] != '$':
                        mc.append("    add $a2,$zero,{}".format(arg2))
                        arg2 = '$a2'
                    mc.append("    sgt {},{},{}".format(arg3, arg1, arg2))
                    mc.append("    xori {},{},1".format(arg3, arg3))  # ?

                elif code[0] == '>=':
                    arg1 = self.getRegister(code[1], dc)
                    arg2 = self.getRegister(code[2], dc)
                    arg3 = self.getRegister(code[3], dc)
                    if str(arg1)[0] != '$':
                        mc.append("    add $a1,$zero,{}".format(arg1))
                        arg1 = '$a1'
                    if str(arg2)[0] != '$':
                        mc.append("    add $a2,$zero,{}".format(arg2))
                        arg2 = '$a2'
                    mc.append("    slt {},{},{}".format(arg3, arg1, arg2))
                    mc.append("    xori {},{},1".format(arg3, arg3))  # ?

        mc.append('')
        mc.append('programEnd:')
        mc.append('    nop')

        # self.prtMips()
        sys.stdout.flush()
        return

    def prtMips(self):
        for code in self.mipsCode:
            print(code)
        return
