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

 

 
