#Kalpazidis Alexandros  A.M. 2985 cse52985
#Grigorios Makris       A.M. 3022 cse53022

import sys

F = open(sys.argv[1] , "r")

cleanToken = 100
extraToken = 101
lineCounter = 1
inComment = False
alpbt = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890+-*/<>=:;,[]() \n \t \r"
reservedWords = ["program","endprogram","declare","function","endfunction","in","inout","inandout","if","then","endif","else","enddowhile","endwhile","while","dowhile","loop","endloop","exit","forcase","default","enddefault","endforcase","incase","endincase","return","print","input","or","and","not","when"]
quadList = []
asmList = []
loopList = []
funcLevel = [0]
funcLabel = {}
newTempCounter = 1
parCounter = -1
main_block_name = ""
scope = []
offset = 12
compiledCounter = 0


def get_linenumber():
    cf = currentframe()
    return cf.f_back.f_lineno

#============================================================= LEX =============================================================

def lex():
    global lineCounter
    global inComment
    tmp = 0
    state = 0
    lastChar = ""
    tmp_token = ""
    tmp_tokenId = None

    while (state != cleanToken and state != extraToken):
        flag_wspc = False
        ch = F.read(1)
        if(ch == '\r' or ch == '\n' ):
            lineCounter += 1

        if(alpbt.find(ch) == -1 and inComment == False):
            print("Line " + str(lineCounter) + " ---> Error: " + ch + " is not recongised by Starlet")
            exit()

        if(state == 0 ):
            if(ch ==''):
                return (tmp_token, tmp_tokenId)
            elif(ch == ' ' or ch == '\t' or ch == '\r' or ch == '\n'):
                flag_wspc = True
                state = 0
            elif(ch.isalpha()):
                state = 1
            elif(ch.isdigit()):
                state = 2
            elif(ch == '<'):
                state = 3
            elif(ch == '>'):
                state = 4
            elif(ch == ':'):
                state = 5
            elif(ch == '/'):
                state = 6
            elif(ch == '*'):
                state = 10
            elif(ch == '+'):
                state = 100
                tmp_tokenId = "addtk"
            elif(ch == '-'):
                state = 100
                tmp_tokenId = "addtk"
            elif(ch == '='):
                state = 100
                tmp_tokenId = "relationaltk"
            elif(ch == ','):
                state = 100
                tmp_tokenId = "commatk"
            elif(ch == ';'):
                state = 100
                tmp_tokenId = "semicolontk"
            elif(ch == '('):
                state = 100
                tmp_tokenId = "op_parenthtk"
            elif(ch == ')'):
                state = 100
                tmp_tokenId = "cl_parenthtk"
            elif(ch == '['):
                state = 100
                tmp_tokenId = "op_bracketk"
            elif(ch == ']'):
                state = 100
                tmp_tokenId = "cl_brackettk"
        elif(state == 1): # This state is for alpharithmetics
            if((not ch.isalpha()) and (not ch.isdigit())):
                state = 101
                tmp_tokenId = "idtk"
        elif(state ==2): # This state is for numerics
            if(ch.isalpha()):
                print ("Line " + str(lineCounter) + " ---> Error: Number followed by letter is not legal")
                exit()
            elif(not ch.isdigit()):
                state = 101
                tmp_tokenId = "constanttk"
        elif(state == 3): # This state is for tokens starting with <
            if(ch == '=' or ch == '>'):
                state = 100
            else:
                state = 101
            tmp_tokenId = "relationaltk"
        elif(state == 4): # This state is for tokens starting with >
            if(ch == '='):
                state = 100
            else:
                state = 101
            tmp_tokenId = "relationaltk"
        elif(state == 5): # This state is for tokens starting with :
            if(ch == '='):
                state = 100
                tmp_tokenId = "assignmenttk"
            else:
                state = 101
                tmp_tokenId = "colontk"
        elif(state == 6):  # This state is for tokens starting with /
            if(ch == '*'):
                state = 7
            elif(ch == '/'):
                state = 9
            else:
                state = 101
                tmp_tokenId = "multk"
        elif(state == 7):  # This state is for multiple line comment (/*)
            inComment = True
            if(lastChar == "/" and (ch =="/" or ch == "*")):
                print("Line " + str(lineCounter) + " ---> Error: Starlet does not support a comment within a comment")
                exit()

            if(ch == '*'):
                lastChar = ""
                state = 8
            elif(ch ==''):
                lastChar = ""
                print("Line " + str(lineCounter) + " ---> Error: Program ended while in a comment")
                exit()
            elif(ch == "/"):
                lastChar = ch
            else:
                state = 7
        elif(state == 8): # This state is for when * come after /*
            if(ch == '/'):
                inComment = False # Out of comment area
                state = 100
                tmp_tokenId = "commenttk"
            elif(ch == '*'):
                state = 8
            elif(ch == ''):
                print("Line " + str(lineCounter) + " ---> Error: Program ended while in a comment")
                exit()
            else:
                state = 7
        elif(state == 9): # This state is for line comment (//)
            inComment = True
            if(ch == '\n'):
                inComment = False # Out of comment area
                state = 101
                tmp_tokenId = "commenttk"
            elif(ch == ''):
                print("Line " + str(lineCounter) + " ---> Error: Program ended while in a comment")
                exit()
            else:
                state = 9
        elif(state == 10 ): # This state is for tokens starting with *
            if(ch == '/'):
                print("Line " + str(lineCounter) + " ---> Error: You have to start a comment with \"/*\" in order to close it with \"*/\"")
                exit()
            else:
                state = 101
                tmp_tokenId = "multk"

        if(not flag_wspc):
            tmp_token = tmp_token + ch

    if(state == 101):
        if(ch == "\n"):
            lineCounter -= 1
        tmp_token = tmp_token[:-1]
        tmp = F.tell()
        F.seek(tmp - 1, 0)

    if( tmp_tokenId == "idtk"):
        if(len(tmp_token) > 30):
            tmp_token = tmp_token[:30]

        if(tmp_token in reservedWords):
            tmp_tokenId = tmp_token + "tk"

    if( tmp_tokenId == "consttk"):
        if( int(tmp_token) > abs(32767) ):
            print("Line " + str(lineCounter) + " ---> Error: Starlet does not support number out of [-32767 , 32767]")
            exit()

    if( tmp_tokenId != "commenttk"):
        return (tmp_token, tmp_tokenId)
    else:
        return lex()

#============================================================= Syntax Analysis =============================================================

def program():
    global token
    global tokenId
    global main_block_name
    global asmList
    token, tokenId = lex()
    if(tokenId == "programtk"):
        asmList.append("L:")
        asmList.append("    j Lmain")
        addScope()
        token, tokenId = lex()
        if(tokenId == "idtk"):
            main_block_name = token
            token, tokenId = lex()
            block(main_block_name)
            if(tokenId == "endprogramtk" ):
                token, tokenId = lex()
                if(token != ''): # EOF
                    print("Line " + str(lineCounter) + " ---> Error: Program must end with keyword 'endprogram' followed by nothing")
                    exit()
                else:
                    print("---------------------------------")
                    print("Compilation completed succesfully")
                    print("---------------------------------")
                    produce()
                    exit()
            else:
                print("Line " + str(lineCounter) + " ---> Error: Expected 'endprogram' ")
                exit()
        else:
            print("Line " + str(lineCounter) + " ---> Error: Expected program name")
            exit()
    else:
        print("Line " + str(lineCounter) + " ---> Error: Program must start with keyword \"program\" ")
        exit()

def block(name):
    global token
    global tokenId
    global main_block_name
    declarations()
    subprograms()
    genQuad("begin_block",name,"_","_")
    statements()
    if(name == main_block_name):
        genQuad("halt","_","_","_")
        for i in range(compiledCounter, len(quadList)):
            translate(quadList[i], i, offset, 0)
    genQuad("end_block",name,"_","_")

def declarations():
    global token
    global tokenId
    while(tokenId == "declaretk"):
        token, tokenId = lex()
        varlist()
        if(tokenId != "semicolontk"):
            token, tokenId = lex()
            print("Line " + str(lineCounter) + " ---> Error: Semicolon missing after variables ====> " + token)
            exit()
        else:
            token, tokenId = lex()

def varlist():
    global token
    global tokenId
    global offset
    if(tokenId == "idtk"):
        for x in scope[len(scope)-1].list:
            if( (x.name == token) and (x.type == "var") ):
                print("Line " + str(lineCounter) + " ---> Error: A variable can not be declared multiple times in same scope ====> " + token)
                exit()
        addEntity(varEntity(token, offset))
        token, tokenId = lex()
        while(tokenId == "commatk"):
            token, tokenId = lex()
            if(tokenId == "idtk"):
                for x in scope[len(scope)-1].list:
                    if( (x.name == token) and (x.type == "var") ):
                        print("Line " + str(lineCounter) + " ---> Error: A variable can not be declared multiple times in same scope ====> " + token)
                        exit()
                addEntity(varEntity(token, offset))
                token, tokenId = lex()
            else:
                print("Line " + str(lineCounter) + " ---> Error: After comma expected name of variable")
                exit()

def subprograms():
    global token
    global tokenId
    while(tokenId == "functiontk"):
        funcLevel.append(0)
        token, tokenId = lex()
        subprogram()

def subprogram():
    global token
    global tokenId
    global compiledCounter
    if(tokenId == "idtk"):
        func_name = token
        token, tokenId = lex()
        funcbody(func_name)
        if(tokenId == "endfunctiontk"):
            ent, nst_lvl = findEntity(func_name)
            ent.frameLength = offset
            for i in range(compiledCounter, len(quadList)):
                translate(quadList[i], i, ent.frameLength, nst_lvl)
            compiledCounter = len(quadList)
            deleteScope()
            if(funcLevel[len(funcLevel)-1] < 1 ):
                print("Line " + str(lineCounter) + " ---> Error: Every function should have at least one 'return' =====> " + token)
                exit()
            del funcLevel[len(funcLevel)-1]
            token, tokenId = lex()
        else:
            print("Line " + str(lineCounter) + " ---> Error: Keyword endfunction expected =====> " + token)
            exit()
    else:
        print("Line " + str(lineCounter) + " ---> Error: Function name expected")
        exit()

def funcbody(func_name):
    global token
    global tokenId
    global offset
    parList, modeList = formalpars()
    funcEnt = (funcEntity(func_name, nextQuad() , 0))
    for x in scope[len(scope)-1].list:
        if( (x.name == func_name) and (x.type == "func") ):
            print("Line " + str(lineCounter) + " ---> Error: A function can not be declared multiple times in same scope ====> " + token)
            exit()
    addEntity(funcEnt)
    if(len(modeList)>0):
        for mode in modeList:
            addArgument(funcEnt,mode)
    addScope()
    if(len(modeList)>0):
        for mode,par in zip(modeList, parList):
            addEntity(parEntity(par,mode,offset))
    block(func_name)

def formalpars():
    global token
    global tokenId
    parList = []
    modeList = []
    if(tokenId == "op_parenthtk"):
        token, tokenId = lex()
        parList, modeList = formalparlist()
        if(tokenId == "cl_parenthtk"):
            token, tokenId = lex()
        else:
            print("Line " + str(lineCounter) + " ---> Error: Expected closing parenthesis ----> "+token)
            exit()
    else:
        print("Line " + str(lineCounter) + " ---> Error: Expected opening parenthesis")
        exit()
    return parList, modeList

def formalparlist():
    global token
    global tokenId
    parList = []
    modeList = []
    if(tokenId == "intk" or tokenId == "inouttk" or tokenId == "inandouttk"):
        parName, parMode = formalparitem()
        parList.append(parName)
        modeList.append(parMode)
        while(tokenId == "commatk"):
            token, tokenId = lex()
            if(tokenId == "intk" or tokenId == "inouttk" or tokenId == "inandouttk"):
                parName, parMode = formalparitem()
                parList.append(parName)
                modeList.append(parMode)
            else:
                print("Line " + str(lineCounter) + " ---> Error: Expected name for the variable and got " + token)
                exit()
    return parList, modeList

def formalparitem():
    global token
    global tokenId
    global offset
    if(tokenId == "intk" or tokenId == "inouttk" or tokenId == "inandouttk"):
        parMode = token
        token, tokenId = lex()
        if(tokenId == "idtk"):
            parName = token
            token, tokenId = lex()
        else:
            print("Line " + str(lineCounter) + " ---> Error: Expected name for the variable and got " + token)
            exit()
    else:
        print("Error: Expected in,inout,inandout")
        exit()
    return parName, parMode

def statements():
    global token
    global tokenId
    statement()
    while(tokenId == "semicolontk"):
        token, tokenId = lex()
        statement()

def statement():
    global token
    global tokenId
    if(tokenId == "idtk"):
        assignmentStat()
    elif(tokenId == "iftk"):
        ifStat()
    elif(tokenId == "whiletk"):
        whileStat()
    elif(tokenId == "dowhiletk"):
        doWhileStat()
    elif(tokenId == "looptk"):
        loopStat()
    elif(tokenId == "exittk"):
        exitStat()
    elif(tokenId == "forcasetk"):
        forcaseStat()
    elif(tokenId == "incasetk"):
        incaseStat()
    elif(tokenId == "returntk"):
        returnStat()
    elif(tokenId == "inputtk"):
        inputStat()
    elif(tokenId == "printtk"):
        printStat()

def assignmentStat():
    global token
    global tokenId
    if(tokenId == "idtk"):
        id = token
        token, tokenId = lex()
        if(tokenId == "assignmenttk"):
            token, tokenId = lex()
            E = expression()
            genQuad(":=", E, "_", id)
        else:
            print("Line " + str(lineCounter) + " ---> Error: After variable expected :=")
            exit()

def ifStat():
    global token
    global tokenId
    if(tokenId == "iftk"):
        token, tokenId = lex()
        if(tokenId == "op_parenthtk"):
            token, tokenId = lex()
            B_true, B_false = condition()
            if(tokenId == "cl_parenthtk"):
                token, tokenId = lex()
                if(tokenId == "thentk"):
                    backpatch(B_true,nextQuad())
                    token, tokenId = lex()
                    statements()
                    ifList = makeList(nextQuad())
                    genQuad("jump", "_", "_", "_")
                    backpatch(B_false,nextQuad())
                    if(tokenId == "elsetk"):
                        elsepart()
                    backpatch(ifList, nextQuad())
                    if(tokenId == "endiftk"):
                        token, tokenId = lex()
                    else:
                        print("Line " + str(lineCounter) + " ---> Error: expected 'endif'")
                        exit()
            else:
                print("Line " + str(lineCounter) + " ---> Error: expected ')'")
                exit()
        else:
            print("Line " + str(lineCounter) + " ---> Error: expected '('" + token)
            exit()

def elsepart():
    global token
    global tokenId
    if(tokenId == "elsetk"):
        token, tokenId = lex()
        statements()

def whileStat():
    global token
    global tokenId
    if (tokenId == "whiletk"):
        token, tokenId = lex()
        Bquad = nextQuad()
        if(tokenId == "op_parenthtk"):
            token, tokenId = lex()
            B_true, B_false = condition()
            if(tokenId == "cl_parenthtk"):
                backpatch(B_true, nextQuad())
                token, tokenId = lex()
                statements()
                genQuad("jump", "_", "_", Bquad)
                backpatch(B_false, nextQuad())
                if(tokenId == "endwhiletk"):
                    token, tokenId = lex()
                else:
                    print("Line " + str(lineCounter) + " ---> Error: expected 'endwhile'")
                    exit()
            else:
                print("Line " + str(lineCounter) + " ---> Error: expected ')'")
                exit()
        else:
            print("Line " + str(lineCounter) + " ---> Error: expected '('")
            exit()

def doWhileStat():
    global token
    global tokenId
    if(tokenId == "dowhiletk"):
        sQuad = nextQuad()
        token, tokenId = lex()
        statements()
        if(tokenId == "enddowhiletk"):
            token, tokenId = lex()
            if(tokenId == "op_parenthtk"):
                token, tokenId = lex()
                cond_True, cond_False = condition()
                if(tokenId == "cl_parenthtk"):
                    backpatch(cond_False, sQuad)
                    backpatch(cond_True, sQuad)
                    token, tokenId = lex()
                else:
                    print("Line " + str(lineCounter) + " ---> Error: expected ')'")
                    exit()
            else:
                print("Line " + str(lineCounter) + " ---> Error: expected '('")
                exit()
        else:
            print("Line " + str(lineCounter) + " ---> Error: expected 'enddowhile'")
            exit()

def loopStat():
    global token
    global tokenId
    global loopList
    if(tokenId == "looptk"):
        exitList = emptyList()
        loopList.append(exitList)
        Lquad = nextQuad()
        token, tokenId = lex()
        statements()
        genQuad("jump", "_", "_", Lquad)
        if(tokenId == "endlooptk"):
            backpatch(loopList[len(loopList)-1],nextQuad())
            del loopList[len(loopList)-1]
            token, tokenId = lex()
        else:
            print("Line " + str(lineCounter) + " ---> Error: expected 'endloop'")
            exit()

def exitStat():
    global token
    global tokenId
    if(tokenId == "exittk"):
        # exit outside loop-endloop
        if(len(loopList) == 0):
            print("Line " + str(lineCounter) + " ---> Error: 'exit' must be used inside a loop-endloop")
            exit()
        quit = makeList(nextQuad())
        genQuad("jump", "_", "_", "_")
        loopList[len(loopList)-1] = merge(quit, loopList[len(loopList)-1])
        token, tokenId = lex()
        return quit

def forcaseStat():
    global token
    global tokenId
    if(tokenId == "forcasetk"):
        Fquad = nextQuad()
        exitList = emptyList()
        token, tokenId = lex()
        while(tokenId == "whentk"):
            token, tokenId = lex()
            if(tokenId == "op_parenthtk"):
                token, tokenId = lex()
                B_true, B_false = condition()
                if(tokenId == "cl_parenthtk"):
                    token, tokenId = lex()
                    if(tokenId == "colontk"):
                        backpatch(B_true, nextQuad())
                        token, tokenId = lex()
                        statements()
                        tmp = makeList(nextQuad())
                        genQuad("jump", "_", "_", "_")
                        exitList = merge(tmp,exitList)
                        backpatch(B_false,nextQuad())
                    else:
                        print("Line " + str(lineCounter) + " ---> Error: Expected ':' ")
                        exit()
                else:
                    print("Line " + str(lineCounter) + " ---> Error: expected ')' ")
                    exit()
            else:
                print("Line " + str(lineCounter) + " ---> Error: expected '('")
                exit()
        if(tokenId == "defaulttk"):
            token, tokenId = lex()
            if(tokenId == "colontk"):
                statements()
                if(tokenId == "enddefault"):
                    backpatch(exitList,nextQuad())
                    token, tokenId = lex()
                    if(tokenId == "endforcasetk"):
                        genQuad("jump", "_", "_", Fquad)
                        token, tokenId = lex()
                    else:
                        print("Line " + str(lineCounter) + " ---> Error: Expected 'endforcase' ")
                        exit()
                else:
                    print("Line " + str(lineCounter) + " ---> Error: Expected 'enddefault' ")
                    exit()
            else:
                print("Line " + str(lineCounter) + " ---> Error: Expected ':' ")
                exit()
        else:
            print("Line " + str(lineCounter) + " ---> Error: Expected 'default' ")
            exit()

def incaseStat():
    global token
    global tokenId
    if(tokenId == "incasetk"):
        t = newTemp()
        flagQuad = nextQuad()
        genQuad(":=", "0", "_", t)
        token, tokenId = lex()
        while(tokenId == "whentk"):
            token, tokenId = lex()
            if(tokenId == "op_parenthtk"):
                token, tokenId = lex()
                B_true, B_false = condition()
                if(tokenId == "cl_parenthtk"):
                    token, tokenId = lex()
                    if(tokenId == "colontk"):
                        backpatch(B_true, nextQuad())
                        genQuad(":=", "1", "_", t)
                        token, tokenId = lex()
                        statements()
                        backpatch(B_false,nextQuad())
                    else:
                        print("Line " + str(lineCounter) + " ---> Error: Expected ':' ")
                        exit()
                else:
                    print("Line " + str(lineCounter) + " ---> Error: expected ')' ")
                    exit()
            else:
                print("Line " + str(lineCounter) + " ---> Error: expected '('")
                exit()

        if(tokenId == "endincasetk"):
            genQuad("=", "1", t, flagQuad)
            token, tokenId = lex()
        else:
            print("Line " + str(lineCounter) + " ---> Error: Expected 'endincase' ")
            exit()

def returnStat():
    global token
    global tokenId
    if(tokenId == "returntk"):
        funcLevel[len(funcLevel)-1] += 1
        if(funcLevel[0] != 0):
            print("Line " + str(lineCounter) + " ---> Error: 'return' cant be used out of function ")
            exit()
        token, tokenId = lex()
        E = expression()
        genQuad("retv", E, "_", "_")

def printStat():
    global token
    global tokenId
    if(tokenId == "printtk"):
        token, tokenId = lex()
        E = expression()
        genQuad("out", E, "_", "_")

def inputStat():
    global token
    global tokenId
    if(tokenId == "imputtk"):
        token, tokenId = lex()
        if(tokenId == "idtk"):
            genQuad("inp", token, "_", "_")
            token, tokenId = lex()
        else:
            print("Line " + str(lineCounter) + " ---> Error: Expected input ")
            exit()

def actualpars():
    global token
    global tokenId
    modeList = []
    if(tokenId == "op_parenthtk"):
        token, tokenId = lex()
        modeList = actualparlist()
        if(tokenId == "cl_parenthtk"):
            token, tokenId = lex()
        else:
            print("Line " + str(lineCounter) + " ---> Error: expected ')' ")
            exit()
    else:
        print("Line " + str(lineCounter) + " ---> Error: expected '('")
        exit()
    return modeList

def actualparlist():
    global token
    global tokenId
    modeList = []
    if(tokenId == "intk" or tokenId == "inouttk" or tokenId == "inandouttk"):
        modeList.append(token)
        actualparitem()
        while(tokenId == "commatk"):
            token, tokenId = lex()
            if(tokenId == "intk" or tokenId == "inouttk" or tokenId == "inandouttk"):
                modeList.append(token)
                actualparitem()
            else:
                print("Line " + str(lineCounter) + " ---> Error: Expected name for the variable and got " + token)
                exit()
    return modeList

def actualparitem():
    global token
    global tokenId
    if(tokenId == "intk"):
        token, tokenId = lex()
        E = expression()
        genQuad("par", E, "CV", "_")
    elif(tokenId == "inouttk"):
        token, tokenId = lex()
        if(tokenId == "idtk"):
            genQuad("par", token, "REF", "_")
            token, tokenId = lex()
    elif(tokenId == "inandouttk"):
        token, tokenId = lex()
        if(tokenId == "idtk"):
            genQuad("par", token, "CP", "_")
            token, tokenId = lex()
        else:
            print("Line " + str(lineCounter) + " ---> Error: Expected name for the variable and got " + token)
            exit()
    else:
        print("Error: Expected in,inout,inandout")
        exit()

def condition():
    global token
    global tokenId
    Q1_true, Q1_false = boolterm()
    B_true = Q1_true
    B_false = Q1_false
    while(tokenId == "ortk"):
        backpatch(B_false, nextQuad())
        token, tokenId = lex()
        Q2_true, Q2_false = boolterm()
        B_true = merge(B_true, Q2_true)
        B_false = Q2_false
    return B_true, B_false

def boolterm():
    global token
    global tokenId
    R1_true, R1_false = boolfactor()
    Q_true = R1_true
    Q_false = R1_false
    while(tokenId == "andtk"):
        backpatch(Q_true, nextQuad())
        token, tokenId = lex()
        R2_true, R2_false = boolfactor()
        Q_false = merge(Q_false,R2_false)
        Q_true = R2_true
    return Q_true, Q_false

def boolfactor():
    global token
    global tokenId
    if(tokenId == "nottk"):
        token, tokenId = lex()
        if(tokenId == "op_bracketk"):
            token, tokenId = lex()
            B_true, B_false = condition()
            if(tokenId == "cl_brackettk"):
                token, tokenId = lex()
            else:
                print("Line " + str(lineCounter) + " ---> Error: expected ']' ")
                exit()
        else:
            print("Line " + str(lineCounter) + " ---> Error: expected '[' ")
            exit()
        R_true = B_false
        R_false = B_true
    elif(tokenId == "op_bracketk"):
        token, tokenId = lex()
        B_true, B_false = condition()
        if(tokenId == "cl_brackettk"):
            token, tokenId = lex()
        else:
            print("Line " + str(lineCounter) + " ---> Error: expected ']' ")
            exit()
        R_true = B_true
        R_false = B_false
    else:
        E_1 = expression()
        relop = relationalOper()
        E_2 = expression()
        R_true = makeList(nextQuad())
        genQuad(relop, E_1, E_2, "_")
        R_false = makeList(nextQuad())
        genQuad("jump", "_", "_", "_")
    return R_true, R_false

def expression():
    global token
    global tokenId
    optionalSign()
    T_1 = term()
    while(tokenId == "addtk"):
        oper = addOper()
        T_2 = term()
        w =  newTemp()
        genQuad(oper, T_1, T_2, w)
        T_1 = w
    return T_1

def term():
    global token
    global tokenId
    F_1 = factor()
    while(tokenId == "multk"):
        oper = mulOper()
        F_2 = factor()
        w = newTemp()
        genQuad(oper, F_1, F_2, w)
        F_1 = w
    return F_1

def factor():
    global token
    global tokenId
    rtn_value = None
    if(tokenId == "constanttk"):
        rtn_value = token
        token, tokenId = lex()
    elif(tokenId == "op_parenthtk"):
        token, tokenId = lex()
        rtn_value = expression()
        if(tokenId == "cl_parenthtk"):
            token, tokenId = lex()
        else:
            print("Line " + str(lineCounter) + " ---> Error: expected ')' ")
            exit()
    elif(tokenId == "idtk"):
        rtn_value = token
        forPrint = rtn_value
        token, tokenId = lex()
        tmp = idtail(rtn_value)
        if(tmp != None):
            ent, nst_lvl = findEntity(rtn_value)
            rtn_value = tmp
        else:
            ent, nst_lvl = findEntity(rtn_value)

        if(ent == None):
            print("Line " + str(lineCounter) + " ---> Error: " + forPrint + " is not declared")
            exit()
    else:
        print("Line " + str(lineCounter) + " ---> Error: expected number, letter or expression ====> " + token)
        exit()
    return rtn_value

def idtail(funcName):
    global token
    global tokenId
    rtn_value = None
    if(tokenId == "op_parenthtk"):
        w = newTemp()
        rtn_value = w
        modeList = actualpars()
        genQuad("par", w, "RET", "_")
        genQuad("call", funcName , "_", "_")
        ent, nst_lvl = findEntity_Type(funcName,"func")
        for x,y in zip(ent.arguments,modeList):
            if(x.parMode != y):
                print("Line " + str(lineCounter) + " ---> Error: In function '" + funcName + "' expected " + str(returnArgs(ent)) + " but we get " + str(modeList) )
                exit()
    return rtn_value

def relationalOper():
    global token
    global tokenId
    rtn_relop = token
    if(tokenId == "relationaltk"):
        token, tokenId = lex()
    else:
        print("Line " + str(lineCounter) + " ---> Error: expected relational operator ")
        exit()
    return rtn_relop

def addOper():
    global token
    global tokenId
    oper = token
    if(tokenId == "addtk"):
        token, tokenId = lex()
    return oper


def mulOper():
    global token
    global tokenId
    oper = token
    if(tokenId == "multk"):
        token, tokenId = lex()
    return oper

def optionalSign():
    global token
    global tokenId
    if(tokenId == "addtk"):
        addOper()



#============================================================= Intermediate Code =============================================================

class Quad:

    def __init__(self,op,x,y,z):
        self.op = op
        self.x = x
        self.y = y
        self.z = z

    def __str__(self):
        return str(self.op) + ", " + str(self.x) + ", " + str(self.y) + ", " + str(self.z)

class Entity:

    def __init__(self,name, type):
        self.name = name
        self.type = type

class varEntity(Entity):

    def __init__(self, name, offset):
        Entity.__init__(self, name, "var")
        self.offset = offset

class funcEntity(Entity):

    def __init__(self, name, startQuad, frameLength):
        Entity.__init__(self, name, "func")
        self.startQuad = startQuad
        self.arguments = []
        self.frameLength = frameLength

class constEntity(Entity):

    def __init__(self, name, value):
        Entity.__init__(self, name, "const")
        self.value = value

class parEntity(Entity):

    def __init__(self, name, parMode , offset):
        Entity.__init__(self, name, "par")
        self.offset = offset
        self.parMode = parMode

class tmpEntity(Entity):

    def __init__(self, name, offset):
        Entity.__init__(self, name, "tmp")
        self.offset = offset

class Argument():

    def __init__(self, parMode):
        self.parMode = parMode
class RecordScope():

    def __init__(self, nst_lvl):
        self.list = []
        self.nst_lvl = nst_lvl


def nextQuad():
    return len(quadList)

def genQuad(op,x,y,z):
    newQuad = Quad(op,x,y,z)
    quadList.append(newQuad)

def newTemp():
    global newTempCounter
    global offset
    temp = "T_" + str(newTempCounter)
    newTempCounter += 1
    addEntity(tmpEntity(temp,offset))
    return temp

def emptyList():
    emList = []
    return emList

def makeList(x):
    mkList = []
    mkList.append(x)
    return mkList

def merge(list1,list2):
    list = list1 + list2
    return list

def backpatch(list,z):
    for x in list:
        quadList[x].z = z

    # List contains only the Line's Number of the quad
    # and not the whole Quad

def addScope():
    global offset
    tmpScope = RecordScope(len(scope))
    scope.append(tmpScope)
    offset = 12

def deleteScope():
    global offset
    del scope[len(scope)-1]
    offset = 12
    for rec in scope[len(scope)-1].list:
        if(rec.type != "func"):
            offset += 4

def addEntity(temp_ent):
    global offset
    entityList = scope[len(scope)-1].list
    entityList.append(temp_ent)
    if(temp_ent.type != "func"):
        offset += 4

def addArgument(funcEnt, parMode):
    tmp_arg = Argument(parMode)
    funcEnt.arguments.append(tmp_arg)

def returnArgs(funcEnt):
    list = []
    for x in funcEnt.arguments:
        list.append(x.parMode)
    return list

def findEntity(ent_name):
    for recScope in reversed(scope):
        for temp_ent in recScope.list:
            if(temp_ent.name == ent_name):
                return temp_ent , recScope.nst_lvl

def findEntity_Type(ent_name, ent_type):
    for recScope in reversed(scope):
        for temp_ent in recScope.list:
            if( (temp_ent.name == ent_name) and (temp_ent.type == ent_type) ):
                return temp_ent , recScope.nst_lvl

def produce():
    prefix = sys.argv[1].split(".")[0]
    i = str(prefix) + ".int"
    c = str(prefix) + ".c"
    a = str(prefix) + ".asm"

    i_f = open(i, "w")
    c_f = open(c, "w")
    a_f = open(a, "w")

    notVar = ["<",">",">=","<=","=","<>","_","+","-","*","/","jump",":=","RET","REF","CV","CP","halt","par","retv"]
    var=[]

    # Write Intermediate code ( .int file) and find Vars
    for i in range(len(quadList)):
        quad = str(i) + ": " + str(quadList[i])
        i_f.write(str(quad)+'\n')
        parts = str(quadList[i]).split(", ", 4)
        if(parts[0]!="begin_block" and parts[0]!="end_block" and parts[0]!="call"):
            for x in parts:
                if(not(x in notVar) and not(x.isdigit()) ):
                    if(not(x in var)):
                        var.append(x)
    i_f.close()

    # Write .c file
    c_f.write("int main()\n{\n")
    if ( len(var)!=0 ):
        c_f.write(" int " + var[0] )
    for i in range(1,len(var)):
        c_f.write(","+str(var[i]))
    c_f.write(";\n L_0:\n")
    for i in range(len(quadList)):
        quad = str(i) + ": " + str(quadList[i])
        #print(quad) # Print in Terminal
        parts = str(quadList[i]).split(", ", 4)

        if(parts[0]== "jump"):
            c_f.write(" L_"+str(i)+": "+"goto "+"L_"+str(parts[3])+";\n")
        if(parts[0]== ":="):
            c_f.write(" L_"+str(i)+": "+ str(parts[3])+ "=" + str(parts[1]) + ";\n")
        if(parts[0]== "+" or parts[0]== "-"  or parts[0]== "*"  or parts[0]== "/"):
            c_f.write(" L_"+str(i)+": "+ str(parts[3])+ "=" + str(parts[1]) + str(parts[0]) +str(parts[2]) + ";\n")
        if(parts[0]== "<" or parts[0]== ">" or parts[0]== ">=" or parts[0]== "<="):
            c_f.write(" L_"+str(i)+": if ("+ str(parts[1]) + str(parts[0]) + str(parts[2]) + ") goto L_"+ str(parts[3]) +  ";\n")
        if(parts[0]== "="):
            c_f.write(" L_"+str(i)+": if ("+ str(parts[1]) + "==" + str(parts[2]) + ") goto L_"+ str(parts[3]) +  ";\n")
        if(parts[0]== "<>"):
            c_f.write(" L_"+str(i)+": if ("+ str(parts[1]) + "!=" + str(parts[2]) + ") goto L_"+ str(parts[3]) +  ";\n")
        if(parts[0]== "halt"):
            c_f.write(" L_" + str(i) + ": {}\n}\n")
    c_f.close()

    # Write .asm file
    for asm in asmList:
        a_f.write(str(asm)+"\n")
        #print(asm) # Print in Terminal
    a_f.close()


#============================================================= Final Code =============================================================
def gnvlcode(var):
    global scope
    global asmList
    ent, nst_lvl =  findEntity(var)
    asmList.append("    lw $t0, -4($sp)")
    for i in range (nst_lvl+1, len(scope)-1):
        asmList.append("    lw $t0, -4($t0)")
    asmList.append("    addi $t0, $t0, -" + str(ent.offset))

def loadvr(v, r):
    global scope
    global asmList
    if(v.isdigit()):
        asmList.append("    li $t"+str(r)+", "+str(v))
    else:
        ent, nst_lvl =  findEntity(v)
        #debug(ent, nst_lvl, len(scope)-1)
        if(nst_lvl == 0 and ent.type == "var"):
            #GLOBAL VARIABLE
            asmList.append("    lw $t"+str(r)+", -"+str(ent.offset)+"($s0)")
        elif(((nst_lvl == len(scope)-1) and (ent.type == "var")) or ((ent.type == "par") and (ent.parMode == "in") and (nst_lvl == len(scope)-1)) or (ent.type == "tmp")):
            asmList.append("    lw $t"+str(r)+", -"+str(ent.offset)+"($sp)")
        elif((ent.type == "par") and (ent.parMode == "inout") and (nst_lvl == len(scope)-1)):
            asmList.append("    lw $t0"+", -"+str(ent.offset)+"($sp)")
            asmList.append("    lw $t"+str(r)+", ($t0)")
        elif((ent.type == "var") or((ent.type == "par")and(nst_lvl < len(scope)-1))):
            gnvlcode(v)
            asmList.append("    lw $t"+str(r)+", ($t0)")
        elif((ent.type == "par") and (ent.parMode == "inout") and (nst_lvl < len(scope)-1) ):
            gnvlcode(v)
            asmList.append("    lw $t0, ($t0)")
            asmList.append("    lw $t"+str(r)+", ($t0)")


def storerv(r, v):
    global scope
    global asmList
    ent, nst_lvl =  findEntity(v)
    #debug(ent, nst_lvl,len(scope)-1)
    if((nst_lvl == 0) and (ent.type == "var")):
        asmList.append("    sw $t"+str(r)+", -"+str(ent.offset)+"($s0)")
    elif(((nst_lvl == len(scope)-1) and (ent.type == "var")) or ((ent.type == "par")and(nst_lvl == len(scope)-1) and (ent.parMode == "in")) or (ent.type == "tmp")):
        asmList.append("    sw $t"+str(r)+", -"+str(ent.offset)+"($sp)")
    elif(((ent.type == "par") and (nst_lvl == len(scope)-1) and (ent.parMode == "inout"))):
        asmList.append("    lw $t0, -"+str(ent.offset)+"($sp)")
        asmList.append("    sw $t"+str(r)+", ($t0)")
    elif((ent.type == "var") or ((ent.type == "par") and (nst_lvl < len(scope)-1) and (ent.parMode == "in"))):
        gnvlcode(v)
        asmList.append("    sw $t"+str(r)+", ($t0)")
    elif((ent.type == "par") and ( ent.parMode == "inout") and (nst_lvl < len(scope)-1)):
        gnvlcode(v)
        asmList.append("    lw $t0, ($t0)")
        asmList.append("    sw $t"+str(r)+", ($t0)")

def translate(quad, i, frameLength, funcNesting):
    global asmList
    global parCounter
    global main_block_name
    global funcLabel
    if(quad.op != "begin_block"):
        asmList.append("L"+str(i)+":")
    if(quad.op == "jump"):
        asmList.append("    j L" + str(quad.z))
    elif(quad.op == "<"):
        loadvr(quad.x, "1")
        loadvr(quad.y, "2")
        asmList.append("    blt $t1, $t2, L" + str(quad.z))
    elif(quad.op == ">"):
        loadvr(quad.x, "1")
        loadvr(quad.y, "2")
        asmList.append("    bgt $t1, $t2, L" + str(quad.z))
    elif(quad.op == "="):
        loadvr(quad.x, "1")
        loadvr(quad.y, "2")
        asmList.append("    beq $t1, $t2, L" + str(quad.z))
    elif(quad.op == "<="):
        loadvr(quad.x, "1")
        loadvr(quad.y, "2")
        asmList.append("    bet $t1, $t2, L" + str(quad.z))
    elif(quad.op == ">="):
        loadvr(quad.x, "1")
        loadvr(quad.y, "2")
        asmList.append("    bge $t1, $t2, L" + str(quad.z))
    elif(quad.op == "<>"):
        loadvr(quad.x, "1")
        loadvr(quad.y, "2")
        asmList.append("    bne $t1, $t2, L" + str(quad.z))
    elif(quad.op == ":="):
        loadvr(quad.x, "1")
        storerv("1", quad.z)
    elif(quad.op == "+"):
        loadvr(quad.x, "1")
        loadvr(quad.y, "2")
        asmList.append("    add $t1, $t1, $t2")
        storerv("1", quad.z)
    elif(quad.op == "-"):
        loadvr(quad.x, "1")
        loadvr(quad.y, "2")
        asmList.append("    sub $t1, $t1, $t2")
        storerv("1", quad.z)
    elif(quad.op == "*"):
        loadvr(quad.x, "1")
        loadvr(quad.y, "2")
        asmList.append("    mul $t1, $t1, $t2")
        storerv("1", quad.z)
    elif(quad.op == "/"):
        loadvr(quad.x, "1")
        loadvr(quad.y, "2")
        asmList.append("    div $t1, $t1, $t2")
        storerv("1", quad.z)
    elif(quad.op == "out"):
        loadvr(quad.x, "1")
        asmList.append("    li $v0, 1")
        asmList.append("    move $a0, $t1")
        asmList.append("    syscall")
    elif(quad.op == "in"):
        asmList.append("    li $v0, 5")
        asmList.append("    syscall")
    elif(quad.op == "retv"):
        loadvr(quad.x, "1")
        asmList.append("    lw $t0, -8($sp)")
        asmList.append("    sw $t1, ($t0)")
    elif(quad.op == "par"):
        ent, nst_lvl =  findEntity(quad.x)
        #debug(ent, nst_lvl,len(scope)-1)
        parCounter += 1
        if(quadList[i-1].op != "par"):
            j = i
            while quadList[j].op != "call" :
                j += 1
            callFuncName = quadList[j].x
            entFunc, func_nst_lvl = findEntity(callFuncName)
            #asmList.append("    addi $fp, $sp, " + str(frameLength))
            asmList.append("    addi $fp, $sp, " + str(entFunc.frameLength))
        if(quad.y == "CV"):
            loadvr(quad.x, "0")
            asmList.append("    sw $t0, -" + str(12 + 4 * parCounter) + "($fp)")
        elif(quad.y == "REF"):
            if(len(scope)-1 == nst_lvl):
                if( (ent.type == "var") or (ent.parMode == "in")):
                    asmList.append("    addi $t0, $sp, -" + str(ent.offset))
                    asmList.append("    sw $t0, -" + str(12 + 4 * parCounter) + "($fp)")
                elif(ent.parMode == "inout"):
                    asmList.append("    lw $t0, -" + str(ent.offset) + "($sp)")
                    asmList.append("    sw $t0, -" + str(12 + 4 * parCounter) + "($fp)")
            elif(len(scope)-1 != nst_lvl):
                if( (ent.type == "var") or (ent.parMode == "in")):
                    gnvlcode(quad.x)
                    asmList.append("    sw $t0, -" + str(12 + 4 * parCounter) + "($fp)")
                elif(ent.parMode == "inout"):
                    gnvlcode(x)
                    asmlist.append("    lw $t0, ($t0)")
                    asmList.append("    sw $t0, -" + str(12 + 4 * parCounter) + "($fp)")
        elif(quad.y == "RET"):
            asmList.append("    addi $t0, $sp, -" + str(ent.offset))
            asmList.append("    sw $t0, -8($fp)")
    elif(quad.op == "call"):
        parCounter = -1
        ent, nst_lvl =  findEntity_Type(quad.x,"func")
        #debug(ent, nst_lvl,funcNesting)
        if(funcNesting == nst_lvl):
            asmList.append("    lw $t0, -4($sp)")
            asmList.append("    sw $t0, -4($fp)")
        else:
            asmList.append("    sw $sp, -4($fp)")
        #asmList.append("    addi $sp, $sp, " + str(frameLength))
        asmList.append("    addi $sp, $sp, " + str(ent.frameLength))
        asmList.append("    jal " + funcLabel.get(quad.x))
        #asmList.append("    addi $sp, $sp, -" + str(frameLength))
        asmList.append("    addi $sp, $sp, -" + str(ent.frameLength))
    elif(quad.op == "begin_block"):
        if(main_block_name == quad.x):
            asmList.append("Lmain:")
            asmList.append("    addi $sp, $sp, "+ str(frameLength))
            asmList.append("    move $s0, $sp")
        funcLabel[str(quad.x)] = "L"+str(i)
        asmList.append("L"+str(i)+":")
        asmList.append("    sw $ra, ($sp)")
    elif(quad.op == "end_block"):
        asmList.append("    lw $ra, ($sp)")
        asmList.append("    jr $ra")
    elif(quad.op == "halt"):
        asmList.append("    li $v0, 10")
        asmList.append("    syscall")

#============================================================= Debuger ==========================================================


def debug(ent, ent_lvl, cur_lvl):
    print("-------------------------")
    print("Entity     : " + str(ent.name))
    print("Ent Level  : " + str(ent_lvl))
    print("Cur Level  : " + str(cur_lvl))
    print("Type       : " + str(ent.type))
    if(ent.type != "func"):
        print("Ent Offset : " + str(ent.offset))
    if(ent.type == "func"):
        print("FrameL   : " + str(ent.frameLength))
    if(ent.type == "par"):
        print("ParMode  : " + str(ent.parMode))
    print("-------------------------")


#============================================================= MAIN =============================================================


#BEGIN
token = ""
tokenId = None
program()

"""
\n Line Feed (LF)
\r Carriage Return (CR)
\r\n Carriage Return + Line Feed (CR+LF)
"""
