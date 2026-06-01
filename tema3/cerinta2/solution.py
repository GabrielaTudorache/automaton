from collections import deque
from itertools import combinations


def citire(filename):
    with open(filename) as f:
        linii = [line.strip() for line in f if line.strip()]

    neterminale = set(linii[0].split())
    terminale = set(linii[1].split())
    n = int(linii[2])

    # multime de reguli (stanga, sir_simboluri); fiecare sir e un tuplu de simboluri
    # lambda este tuplul vid ()
    productii = set()
    for k in range(n):
        stanga, *rest = linii[3 + k].split()
        sir = rest[0] if rest else "lambda"
        sir_simboluri = () if sir == "lambda" else tuple(sir)
        productii.add((stanga, sir_simboluri))

    simbol_start = linii[3 + n]

    return neterminale, terminale, productii, simbol_start


def calcul_anulabile(neterminale, productii):
    # N este anulabil daca N -> lambda sau N -> sir de neterminale toate anulabile
    anulabile = set()
    schimbat = True
    while schimbat:
        schimbat = False
        for stanga, sir_simboluri in productii:
            if stanga in anulabile:
                continue
            if all(simbol in anulabile for simbol in sir_simboluri):
                anulabile.add(stanga)
                schimbat = True
    return anulabile


def elimina_lambda(productii, anulabile):
    # pentru fiecare productie generam toate variantele in care omitem submultimi de neterminale anulabile
    # pastram doar variantele nevide
    productii_noi = set()
    for stanga, sir_simboluri in productii:
        pozitii_anulabile = []
        for i in range(len(sir_simboluri)):
            if sir_simboluri[i] in anulabile:
                pozitii_anulabile.append(i)
        for k in range(len(pozitii_anulabile) + 1):
            for de_sters in combinations(pozitii_anulabile, k):
                varianta = []
                for i in range(len(sir_simboluri)):
                    if i not in de_sters:
                        varianta.append(sir_simboluri[i])
                if varianta:
                    productii_noi.add((stanga, tuple(varianta)))
    return productii_noi


def elimina_unitare(neterminale, productii):
    # perechi unitare (A, B) inseamna ca A => B prin productii unitare
    perechi = {(N, N) for N in neterminale}
    schimbat = True
    while schimbat:
        schimbat = False
        for stanga, sir_simboluri in productii:
            if len(sir_simboluri) == 1 and sir_simboluri[0] in neterminale:
                B = sir_simboluri[0]
                for A, X in list(perechi):
                    if X == stanga and (A, B) not in perechi:
                        perechi.add((A, B))
                        schimbat = True

    # A primeste toate productiile ne-unitare ale fiecarui B cu (A, B) pereche
    productii_noi = set()
    for A, B in perechi:
        for stanga, sir_simboluri in productii:
            if stanga != B:
                continue
            este_unitara = len(sir_simboluri) == 1 and sir_simboluri[0] in neterminale
            if not este_unitara:
                productii_noi.add((A, sir_simboluri))
    return productii_noi


def elimina_neproductive(neterminale, terminale, productii):
    # un neterminal e productiv daca poate deriva un sir doar de terminale
    productive = set()
    schimbat = True
    while schimbat:
        schimbat = False
        for stanga, sir_simboluri in productii:
            if stanga in productive:
                continue
            if all(
                simbol in terminale or simbol in productive for simbol in sir_simboluri
            ):
                productive.add(stanga)
                schimbat = True

    productii_noi = set()
    for stanga, sir_simboluri in productii:
        if stanga not in productive:
            continue
        if all(simbol in terminale or simbol in productive for simbol in sir_simboluri):
            productii_noi.add((stanga, sir_simboluri))
    return productive, productii_noi


def elimina_inaccesibile(simbol_start, terminale, productii):
    accesibile = {simbol_start}
    coada = deque([simbol_start])
    while coada:
        N = coada.popleft()
        for stanga, sir_simboluri in productii:
            if stanga != N:
                continue
            for simbol in sir_simboluri:
                if simbol not in terminale and simbol not in accesibile:
                    accesibile.add(simbol)
                    coada.append(simbol)

    productii_noi = set()
    for stanga, sir_simboluri in productii:
        if stanga in accesibile:
            productii_noi.add((stanga, sir_simboluri))
    return accesibile, productii_noi


def nume_neterminal_nou(neterminale, prefix):
    i = 0
    while f"{prefix}{i}" in neterminale:
        i += 1
    nume = f"{prefix}{i}"
    neterminale.add(nume)
    return nume


def transforma_cnf(neterminale, terminale, productii):
    # pas 1: in productiile cu cel putin doua simboluri,
    # inlocuim fiecare terminal cu un neterminal nou T_a c are are doar productia T_a -> a
    terminal_la_neterminal = {}
    productii_pas1 = set()
    for stanga, sir_simboluri in productii:
        if len(sir_simboluri) == 1:
            productii_pas1.add((stanga, sir_simboluri))
            continue
        sir_nou = []
        for simbol in sir_simboluri:
            if simbol in terminale:
                if simbol not in terminal_la_neterminal:
                    nume = nume_neterminal_nou(neterminale, "T_")
                    terminal_la_neterminal[simbol] = nume
                    productii_pas1.add((nume, (simbol,)))
                sir_nou.append(terminal_la_neterminal[simbol])
            else:
                sir_nou.append(simbol)
        productii_pas1.add((stanga, tuple(sir_nou)))

    # pas 2: spargem productiile cu peste doua neterminale in lant de productii binare
    # A -> B1 B2 ... Bk devine A -> B1 C1, C1 -> B2 C2, ..., C(k-2) -> B(k-1) Bk
    productii_cnf = set()
    for stanga, sir_simboluri in productii_pas1:
        if len(sir_simboluri) <= 2:
            productii_cnf.add((stanga, sir_simboluri))
            continue
        stanga_curenta = stanga
        for i in range(len(sir_simboluri) - 2):
            nume = nume_neterminal_nou(neterminale, "X")
            productii_cnf.add((stanga_curenta, (sir_simboluri[i], nume)))
            stanga_curenta = nume
        productii_cnf.add((stanga_curenta, sir_simboluri[-2:]))

    return productii_cnf


def formateaza_gramatica(productii):
    linii = []
    for stanga, sir_simboluri in productii:
        sir = " ".join(sir_simboluri)
        linii.append(f"{stanga} -> {sir}")
    return "\n".join(sorted(linii))


def main():
    neterminale, terminale, productii, simbol_start = citire("input.txt")

    anulabile = calcul_anulabile(neterminale, productii)
    productii = elimina_lambda(productii, anulabile)
    productii = elimina_unitare(neterminale, productii)
    _, productii = elimina_neproductive(neterminale, terminale, productii)
    _, productii = elimina_inaccesibile(simbol_start, terminale, productii)
    productii = transforma_cnf(neterminale, terminale, productii)

    with open("output.txt", "w") as f:
        f.write(formateaza_gramatica(productii))
        f.write("\n")


if __name__ == "__main__":
    main()
