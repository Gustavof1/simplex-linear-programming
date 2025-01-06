import argparse
import numpy as np

class SimplexSolver:
    def __init__(self, file_name, decimals=3, digits=7, policy='largest'):
        self.file_name = file_name
        self.decimals = decimals
        self.digits = digits
        self.policy = policy
        self.num_vars = 0
        self.num_constraints = 0
        self.objective = []
        self.constraints = []
        self.non_negative = []
        self.A = None
        self.b = None
        self.c = None
        self.base_vars = []

    def read_input(self):
        with open(self.file_name, 'r') as file:
            lines = file.read().splitlines()

        self.num_vars = int(lines[0])
        self.num_constraints = int(lines[1])
        self.non_negative = list(map(int, lines[2].split()))
        
        # Tratar a linha da função objetivo
        objective_line = lines[3]
        if objective_line.startswith("max"):
            objective_line = objective_line.replace("max", "").strip()
        self.objective = list(map(float, objective_line.split()))
        
        self.constraints = []
        for line in lines[4:]:
            parts = line.split()
            coeffs = list(map(float, parts[:-2]))
            sign = parts[-2]
            rhs = float(parts[-1])
            self.constraints.append((coeffs, sign, rhs))


    def to_fpi(self):
        A = []
        b = []
        c = list(self.objective)  # Coeficientes da função objetivo
        num_slack_vars = 0  # Contador para variáveis de folga/excesso

        for coeffs, sign, rhs in self.constraints:
            row = coeffs.copy()  # Copiar os coeficientes para evitar modificações inadvertidas

            if sign == '<=':
                # Adicionar variável de folga
                row += [1] + [0] * num_slack_vars
                num_slack_vars += 1
                c.append(0)  # Variáveis de folga não impactam a função objetivo
            elif sign == '>=':
                # Adicionar variável de excesso e ajustar o lado direito
                row += [-1] + [0] * num_slack_vars
                num_slack_vars += 1
                c.append(0)
                rhs = -rhs
            elif sign == '==':
                # Igualdade não precisa de variáveis adicionais
                row += [0] * (num_slack_vars + 1)
                c.append(0)

            A.append(row)
            b.append(rhs)

        # Garantir que todas as linhas de A tenham o mesmo comprimento
        num_columns = max(len(row) for row in A)  # Determinar o tamanho máximo das linhas
        A = [row + [0] * (num_columns - len(row)) for row in A]  # Preencher com zeros

        self.A = np.array(A, dtype=float)
        self.b = np.array(b, dtype=float)
        self.c = np.array(c + [0] * (num_columns - len(c)), dtype=float)  # Alinhar c ao tamanho de A
        self.base_vars = list(range(self.num_vars, self.num_vars + len(b)))



    def pivot(self):
        # Identificar variável de entrada
        if self.policy == 'largest':
            entering_var = np.argmax(self.c)
        elif self.policy == 'smallest':
            entering_var = np.argmin(self.c)
        elif self.policy == 'bland':
            entering_var = next(i for i, v in enumerate(self.c) if v > 0)

        # Identificar variável de saída
        ratios = [
            self.b[i] / self.A[i, entering_var] if self.A[i, entering_var] > 0 else float('inf') 
            for i in range(len(self.b))
        ]
        leaving_var = np.argmin(ratios)

        # Pivoteamento
        pivot_value = self.A[leaving_var, entering_var]
        self.A[leaving_var] /= pivot_value
        self.b[leaving_var] /= pivot_value

        for i in range(len(self.A)):
            if i != leaving_var:
                factor = self.A[i, entering_var]
                self.A[i] -= factor * self.A[leaving_var]
                self.b[i] -= factor * self.b[leaving_var]

        # Atualizar c considerando apenas as variáveis válidas
        self.c -= self.c[entering_var] * self.A[leaving_var]

        # Atualizar variáveis básicas
        self.base_vars[leaving_var] = entering_var

    def simplex(self):
        while any(v > 0 for v in self.c):
            self.print_step()
            self.pivot()

    def solve(self):
        self.read_input()
        self.to_fpi()

        
        

        
        self.simplex()

        
        primal = [0] * len(self.c)
        for i, var in enumerate(self.base_vars):
            if var < len(primal):
                primal[var] = self.b[i]

        z = -np.dot(self.c, primal)
        dual = [0] * len(self.b)  

        self.print_result("otimo", z=z, primal=primal, dual=dual)

    def print_step(self):
        print("Tabela Simplex Atual:")
        print("Base:", self.base_vars)
        print("A:")
        print(self.A)
        print("b:")
        print(self.b)
        print("c:")
        print(self.c)

    def print_result(self, status, z=None, primal=None, dual=None):
        if status == 'inviavel':
            print("Status: inviavel")
        elif status == 'ilimitado':
            print("Status: ilimitado")
        elif status == 'otimo':
            print("Status: otimo")
            print(f"Objetivo: {z:.{self.decimals}f}")
            print("Solucao:")
            print(" ".join(f"{v:.{self.decimals}f}" for v in primal))
            print("Dual:")
            print(" ".join(f"{w:.{self.decimals}f}" for w in dual))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Simplex Solver")
    parser.add_argument("filename", help="Nome do arquivo LP de entrada")
    parser.add_argument("--decimals", type=int, default=3, help="N. de casas decimais para imprimir valores numericos.")
    parser.add_argument("--digits", type=int, default=7, help="N. total de digitos para imprimir valores numericos.")
    parser.add_argument("--policy", choices=['largest', 'bland', 'smallest'], default='largest', help="Regra de pivoteamento.")
    args = parser.parse_args()

    solver = SimplexSolver(args.filename, args.decimals, args.digits, args.policy)
    solver.solve()
