def citire(filename):
    with open(filename) as f:
        linii = [line.strip() for line in f if line.strip()]

    neterminale = set(linii[0].split())
    terminale = set(linii[1].split())
    n = int(linii[2])

    # gramatica e in FNC: fiecare regula e N -> sir (un terminal a sau neterminalele BC)
    # productii_terminale[a] = neterminalele cu regula N -> a
    # productii_binare = lista (A, B, C) pentru regula A -> BC
    productii_terminale = {}
    productii_binare = []
    for k in range(n):
        stanga, *rest = linii[3 + k].split()
        sir = rest[0]
        if len(sir) == 1:
            if sir not in productii_terminale:
                productii_terminale[sir] = set()
            productii_terminale[sir].add(stanga)
        else:
            B, C = sir[0], sir[1]
            productii_binare.append((stanga, B, C))

    simbol_start = linii[3 + n]
    cuvant = linii[4 + n]

    return (
        neterminale,
        terminale,
        productii_terminale,
        productii_binare,
        simbol_start,
        cuvant,
    )

#Exemplu: daca avem S -> AB si S -> a:
# productii_terminale = {'a': {'S'}}
# productii_binare    = [('S', 'A', 'B')]




def cyk(productii_terminale, productii_binare, cuvant):
    n = len(cuvant)

    # tabela[lungime][start] = neterminalele care deriva subsirul cuvant[start:start+lungime]
    # lungime merge de la 1 la n, start de la 0 la n-lungime
    tabela = [[set() for _ in range(n)] for _ in range(n + 1)]

    for start in range(n):
        tabela[1][start] = set(productii_terminale.get(cuvant[start], set()))

    #Pentru fiecare caracter din cuvant, punem in tabela neterminalele care produc acel caracter.

  #Exemplu pentru cuvantul abc:
  #tabela[1][0] = neterminalele care produc 'a'
  #tabela[1][1] = neterminalele care produc 'b'
  #tabela[1][2] = neterminalele care produc 'c'

    for lungime in range(2, n + 1):
        for start in range(n - lungime + 1):
            for taietura in range(1, lungime):
                stanga = tabela[taietura][start]
                dreapta = tabela[lungime - taietura][start + taietura]
                for A, B, C in productii_binare:
                    if B in stanga and C in dreapta:
                        tabela[lungime][start].add(A)

    #Pentru fiecare subsir de lungime lungime care incepe la start, incercam toate
  #taieturile posibile — il impartim in doua bucati si vedem ce neterminale pot
  #produce fiecare bucata.

  #Exemplu: pentru cuvantul abcd, subsir abc (start=0, lungime=3):

  #taietura=1: stanga = tabela[1][0] (cine produce 'a')
  #           dreapta = tabela[2][1] (cine produce 'bc')

  #taietura=2: stanga = tabela[2][0] (cine produce 'ab')
  #           dreapta = tabela[1][2] (cine produce 'c')

  #Daca gasim o regula A -> B C unde B e in stanga si C e in dreapta, atunci A poate
  # produce subsirul abc : il adaugam in tabela[3][0].



    return tabela

#Fiecare rand corespunde unei lungimi, fiecare
#coloana unui subsir. Daca nicio neterminal nu poate produce acel subsir, afiseaza "-" 
def output(tabela, cuvant):
    n = len(cuvant)
    linii = []
    for lungime in range(1, n + 1):
        rand = []
        for start in range(n - lungime + 1):
            continut = tabela[lungime][start]
            if continut:
                rand.append(",".join(sorted(continut)))
            else:
                rand.append("-")
        linii.append(" ".join(rand))
    return "\n".join(linii)


def main():
    (
        neterminale,
        terminale,
        productii_terminale,
        productii_binare,
        simbol_start,
        cuvant,
    ) = citire("input.txt")

    tabela = cyk(productii_terminale, productii_binare, cuvant)
    apartine = simbol_start in tabela[len(cuvant)][0]

    with open("output.txt", "w") as f:
        f.write("DA\n" if apartine else "NU\n")
        f.write(output(tabela, cuvant))
        f.write("\n")


if __name__ == "__main__":
    main()
