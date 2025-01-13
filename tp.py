import numpy as np
import sys



class Argumentos:
	def __init__(self):
		self.filename = ""
		self.decimals = 3
		self.digits = 1
		self.policy = 'largest'

	def setFilename(self, i):
		self.filename = i

	def setDecimals(self, i):
		self.decimals = i

	def setDigits(self, i):
		self.digits = i

	def setPolicy(self, i):
		self.policy = i

	def getFilename(self):
		return self.filename

	def getDecimals(self):
		return self.decimals

	def getDigits(self):
		return self.digits

	def getPolicy(self):
		return self.policy

Argumentos = Argumentos()

def readEntry():
	
    global Argumentos

    try:
        args = sys.argv[1:]
        if len(args) < 1:
            raise ValueError("O argumento 'filename' é obrigatório.")

        Argumentos.setFilename(args[0])

        i = 1
        while i < len(args):
            if args[i] == "--decimals":
                i += 1
                Argumentos.setDecimals(int(args[i]))

            elif args[i] == "--digits":
                i += 1
                Argumentos.setDigits(int(args[i]))

            elif args[i] == "--policy":
                i += 1
                policy = args[i]
                if policy not in ['largest', 'bland', 'smallest']:
                    raise ValueError("Política inválida. Escolha entre 'largest', 'bland' ou 'smallest'.")
                Argumentos.setPolicy(policy)

            i += 1
	
    except Exception as e:
        print(f"Erro ao analisar argumentos: {e}")
        sys.exit(1)

def printMatrix(M):

    col_widths = [max(len([[formatacao_print.format(value) for value in row] for row in M ] [row] [col]) for row in range(len(M))) for col in range(len(M[0]))]

    for row in [[formatacao_print.format(value) for value in row] for row in M ]:
        print("[", end=" ")
        for i, value in enumerate(row):
            print(value.rjust(col_widths[i]), end=" ")
        print("]")

def printMatrixVariaveis(M):

    col_widths = [max(len([[formatacao_print.format(value) for value in row] for row in M ] [row] [col]) for row in range(len(M))) for col in range(len(M[0]))]

    for row in [[formatacao_print.format(value) for value in row] for row in M ]:
        print("[", end=" ")
        for i, value in enumerate(row):
            print(value.rjust(col_widths[i])+"x"+str(i), end=" ")
        print("]")

def getFuncaoObjetivo(file, qtd_variaveis, sinal):

	if not file:
		sys.exit("Erro no arquivo")

	line4 = file.readline().split()
	min_ou_max = (-1 if line4[0] == "min" else 1)

	objetivo = []
	for i in range(qtd_variaveis):
		objetivo.append(int(line4[i+1])*min_ou_max)

		if sinal[i] == -1:
			objetivo[-1] *= -1
		elif sinal[i] == 0:
			objetivo.append(-int(line4[i+1])*min_ou_max)

	return objetivo

def formataMatriz(file, qtd_restricoes, qtd_variaveis, sinal):

	if not file:
		sys.exit("Erro no arquivo")

	A = []
	b = []
	equal = []
	for i in range(qtd_restricoes):
		line = file.readline().split()
		sign = (1 if line[-2] != ">=" else -1)
		equal.append(1 if line[-2] == "==" else 0)

		A.append([]);
		for j in range(len(line)-2):
			A[i].append(int(line[j])*sign)
			if sinal[j] == -1:
				A[i][-1] *= -1
			elif sinal[j] == 0:
				A[i].append(-int(line[j])*sign)

		b.append(int(line[-1])*sign)

	qtd_variaveis += sinal.count(0)+1
	return A, b, equal, qtd_variaveis

def formataFormaPadraoDeIgualdades(qtd_restricoes, qtd_variaveis, A, c, b, equal):	
	for i in range(len(equal)):
		if not equal[i]:
			c.append(0)
			qtd_variaveis += 1
			for j in range(qtd_restricoes):
				A[j].append((1 if i == j else 0))

	for i in range(qtd_restricoes):
		A[i].append(b[i])

	return qtd_restricoes, qtd_variaveis, A, c, b

def formataEntrada():
	file = open(Argumentos.getFilename(), "r")

	qtd_variaveis = int(file.readline().strip())
	qtd_restricoes = int(file.readline().strip())

	sinal_variaveis = list(map(int, file.readline().split()))

	funcao_objetivo = getFuncaoObjetivo(file, qtd_variaveis, sinal_variaveis)

	A, b, equal, qtd_variaveis = formataMatriz(file, qtd_restricoes, qtd_variaveis, sinal_variaveis)
	
	print("Para a equacao do tipo:")
	print()
	print("Max/Min c^t x")
	print("Ax = b")
	print()

	print("c (Funcao Objetivo)")
	result = [f"{num}x{index}" for index, num in enumerate(funcao_objetivo)]
	print("[", end=" ")
	print(" ".join(result)+" ]")
	print()
	print()

	print("Ax (Restricoes n-1 colunas)")
	printMatrixVariaveis(A)
	print()


	print("b (Restricoes coluna n)")
	for item in b:
		print("[ ",item, " ]")
	print()

	qtd_restricoes, qtd_variaveis, A, funcao_objetivo, b = formataFormaPadraoDeIgualdades(qtd_restricoes, qtd_variaveis, A, funcao_objetivo, b, equal)

	file.close()

	print("Matriz na forma padrão de igualdades")
	print("[", end=" ")
	for item in funcao_objetivo:
		print(f"{item:>{Argumentos.getDigits()}.{Argumentos.getDecimals()}f}", end=" ")
	print(" ]")
	printMatrix(A)
	print()

	

	return qtd_restricoes, qtd_variaveis, funcao_objetivo, A, sinal_variaveis

def getTableau(qtd_restricoes, qtd_variaveis, c, A):
    tableau = np.array([[0] * (qtd_variaveis + qtd_restricoes)] * (qtd_restricoes + 1))
    tableau = tableau.astype(float)

    for i in range(qtd_restricoes):
        tableau[i + 1][i] = 1

    for i in range(qtd_variaveis - 1):
        tableau[0][i + qtd_restricoes] = -c[i]

    for i in range(qtd_restricoes):
        for j in range(qtd_variaveis):
            tableau[i + 1][j + qtd_restricoes] = A[i][j]

    qtd_variaveis += qtd_restricoes
    qtd_restricoes += 1

    print("Tableau:")
    printMatrix(tableau)
    print()

    return tableau, qtd_restricoes, qtd_variaveis

def getBase(tableau, qtd_restricoes, qtd_variaveis):
    X = set()
    Y = []
    for i in range(1, qtd_restricoes):
        X.add(i)

    for i in range(qtd_restricoes - 1, qtd_variaveis - 1):
        cnt = 0
        idx = -1
        for j in range(1, qtd_restricoes):
            if tableau[j][i] < -quase_zero or tableau[j][i] > 1:
                cnt = 0
                break

            if tableau[j][i] == 1:
                cnt += 1
                idx = j
        if cnt == 1:
            if idx in X:
                X.remove(idx)
                Y.append(i)
                tableau[0] -= tableau[0][i] * tableau[idx]

    return tableau, X, Y

def getIndice(tableau, qtd_restricoes, qtd_variaveis):
    mn = 0
    y = -1
    for i in range(qtd_restricoes - 1, qtd_variaveis - 1):
        if tableau[0][i] < -quase_zero:
            if Argumentos.getPolicy() == "bland":
                return i
            elif (Argumentos.getPolicy() == "smallest" and (mn == 0 or mn < tableau[0][i])) or \
                 (Argumentos.getPolicy() == "largest" and (mn == 0 or mn > tableau[0][i])):
                mn = tableau[0][i]
                y = i
    return y

def pivoPrimal(tableau, qtd_restricoes, qtd_variaveis, x, y):
    tableau[x] /= tableau[x][y]
    for i in range(0, qtd_restricoes):
        if i != x and abs(tableau[i][y]) > quase_zero:
            tableau[i] -= tableau[x] * tableau[i][y]

def pivoDual(tableau, qtd_variaveis, qtd_restricoes, x, y):
    for i in range(len(tableau)):
        if i != x and abs(tableau[i][y]) > quase_zero:
            tableau[i] = [tableau[i][j] - tableau[x][j] * tableau[i][y] / tableau[x][y] for j in range(len(tableau[0]))]
    tableau[x] = [elem / tableau[x][y] for elem in tableau[x]]

def simplexPD(tableau, qtd_restricoes, qtd_variaveis):
    def simplexDual():
        print("Simplex Dual:\n")
        while True:
            x = -1
            y = -1

            for i in range(1, qtd_restricoes):
                if tableau[i][-1] < -quase_zero:
                    x = i

            if x < 0:
                print("Fim metodo Dual")
                print()
                break

            for i in range(qtd_restricoes - 1, qtd_variaveis - 1):
                if tableau[x][i] < -quase_zero:
                    y = i
                    break

            if y < 0:
                print("Encontrado inviabilidade\n\nStatus: inviavel")
                sys.exit()
                return tableau, "inviavel"

            print("Pivo", x, y)
            print()

            pivoDual(tableau, qtd_variaveis, qtd_restricoes, x, y)

            printMatrix(tableau)
            print()

    def simplexPrimal():
        print("Simplex Primal:\n")
        while True:
            x = -1
            y = getIndice(tableau, qtd_restricoes, qtd_variaveis)

            if y < 0:
                print("Fim metodo primal")
                print()
                break

            mn = 0
            for i in range(1, qtd_restricoes):
                if tableau[i][y] > quase_zero and (mn == 0 or tableau[i][-1] / tableau[i][y] < mn):
                    mn = tableau[i][-1] / tableau[i][y]
                    x = i

            if x < 0:
                print("Encontrado resultado ilimitado\n\nStatus: ilimitado")
                sys.exit()
                return tableau, "ilimitado"

            print("pivo", x, y)
            print()

            pivoPrimal(tableau, qtd_restricoes, qtd_variaveis, x, y)

            printMatrix(tableau)
            print()
		
    simplexDual()
    simplexPrimal()

    return tableau, "otimo"

def calcSolucao(tableau, qtd_restricoes, qtd_variaveis, sinal):
    tableau, X, Y = getBase(tableau, qtd_restricoes, qtd_variaveis)
    
    sol = {} 
    for y in Y:
        idx = -1
        for i in range(1, qtd_restricoes):
            if tableau[i][y]:
                idx = i
                break
        sol[y] = tableau[idx][-1]

    sols = [0] * len(sinal)
    j = qtd_restricoes - 1
    for i in range(len(sinal)):
        if sinal[i] == 0:
            sols[i] = (sol[j] if j in sol else 0) - (sol[j+1] if j+1 in sol else 0)
            j += 1
        else:
            sols[i] = (sol[j] if j in sol else 0)

        j += 1

    return sols

def get_aux(tableau, qtd_restricoes, qtd_variaveis, X):
    b = []
    aux, n1, m1 = tableau, qtd_restricoes, qtd_variaveis
    aux = aux.tolist()
    
    for i in range(qtd_restricoes):
        b.append(aux[i][-1])
        aux[i].pop()

    for i in range(n1 - 1, qtd_variaveis - 1):
        aux[0][i] = 0

    for x in X:
        m1 += 1
        aux[0].append(1)
        for i in range(1, qtd_restricoes):
            if x != i:
                aux[i].append(0)
            else:
                aux[i].append(1)

    for i in range(qtd_restricoes):
        aux[i].append(b[i])

    aux = np.array(aux)

    for x in X:
        aux[0] -= aux[x]

    return aux, n1, m1

def auxiliar(tableau, qtd_restricoes, qtd_variaveis):
    print("Matriz Auxiliar:")
    tableau, X, Y = getBase(tableau, qtd_restricoes, qtd_variaveis)

    if len(X) == 0:
        print("Ja existe base obvia para a matriz")
        print()
        return tableau, "otimo"

    aux, n1, m1 = get_aux(tableau, qtd_restricoes, qtd_variaveis, X)

    printMatrix(aux)
    print()

    print("Simplex:")
    aux, status = simplexPD(aux, n1, m1)

    if aux[0][-1] < 0:
        return tableau, "inviavel"

    return tableau, "otimo"

def calcSimplex(tableau, qtd_restricoes, qtd_variaveis):
    tableau, status = auxiliar(tableau, qtd_restricoes, qtd_variaveis)

    if status == "inviavel":
        return tableau, status

    tableau, status = simplexPD(tableau, qtd_restricoes, qtd_variaveis)
    
    return tableau, status

#Auxílios do chatGPT :)

#MAIN

#Argumentos
readEntry()

#Constante - Formatacao de Saída
formatacao_print = f"{{:>{Argumentos.getDigits()}.{Argumentos.getDecimals()}f}}"

#Constante - Número muito próximo de 0
quase_zero = 1e-9

qtd_restricoes, qtd_variaveis, c, A, sinal = formataEntrada()

tableau, qtd_restricoes, qtd_variaveis = getTableau(qtd_restricoes, qtd_variaveis, c, A)

tableau, status = calcSimplex(tableau, qtd_restricoes, qtd_variaveis)

if status == "otimo": 
	print()
	print("Tableau final:")
	printMatrix(tableau)
	print()

	print("Status: " + status)

	print("Objetivo: ", end = "")
	print(formatacao_print.format(tableau[0][-1]))

	print("Solucao: ")
	sols = calcSolucao(tableau, qtd_restricoes, qtd_variaveis, sinal)
	for x in sols:
		print(formatacao_print.format(x), end = " ")
	print()


	print("Dual: ")
	dualres = tableau[0][:qtd_restricoes-1]
	for x in dualres:
		print(formatacao_print.format(x), end = " ")
	print()
