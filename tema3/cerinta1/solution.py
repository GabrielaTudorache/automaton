from collections import deque


def citire(filename):
    with open(filename) as f:
        linii = [line.strip() for line in f if line.strip()]

    neterminale = set(linii[0].split())
    terminale = set(linii[1].split())
    n = int(linii[2])

    # productii[neterminal] = lista de tupluri de simboluri
    # lambda este reprezentat de tuplul vid ()
    productii = {}
    for k in range(n):
        stanga, *rest = linii[3 + k].split()
        sir = rest[0] if rest else "lambda"
        sir_simboluri = () if sir == "lambda" else tuple(sir)
        if stanga not in productii:
            productii[stanga] = []
        productii[stanga].append(sir_simboluri)

    simbol_start = linii[3 + n]
    lungime = int(linii[4 + n])

    return neterminale, terminale, productii, simbol_start, lungime

#calculez pentru fiecare neterminal cate terminale minim poate genera
#rezultat folosit ca sa omor mai devreme ramurile fara speranta
def lungimi_minime(neterminale, terminale, productii):
    # lungime_minima[N] = numarul minim de terminale care pot fi derivate din N
    # un terminal contribuie cu 1, lambda cu 0
    lungime_minima = {N: float("inf") for N in neterminale}

    schimbat = True
    while schimbat:
        schimbat = False
        for N, reguli in productii.items():
            for sir_simboluri in reguli:
                total = 0
                for simbol in sir_simboluri:
                    total += 1 if simbol in terminale else lungime_minima[simbol]
                if total < lungime_minima[N]:
                    lungime_minima[N] = total
                    schimbat = True

    return lungime_minima

#Calculeaza lungimea minima a unui cuvant care poate fi derivat dintr-o forma
# de genul : sir de simboluri mixte — terminale + neterminale. Sumeaza 1 pentru
#fiecare terminal si lungime_minima[N] pentru fiecare neterminal.
def lungime_minima_forma(forma, terminale, lungime_minima):
    total = 0
    for simbol in forma:
        total += 1 if simbol in terminale else lungime_minima[simbol]
    return total

#Genereaza toate cuvintele de lungime exacta derivabile din simbol_start.
#Foloseste BFS cu derivare la stanga (inlocuieste intotdeauna primul neterminal
#din forma). Daca lungimea minima a formei curente depaseste
#lungimea, ramura e taiata. La final, colecteaza formele care au ajuns la
#lungimea exacta ceruta si contin doar terminale.
def genereaza(neterminale, terminale, productii, simbol_start, lungime):
    #calculeaza in avans lungimea maxima pentru fiecare neterminal, ca sa pot taia 
    # ramurile fara speranta mai devreme
    lungime_minima = lungimi_minime(neterminale, terminale, productii)

    cuvinte = set()
    forma_initiala = (simbol_start,)
    coada = deque([forma_initiala])
    vizitate = {forma_initiala}


    #Daca nu am gasit niciun neterminal, forma contine doar terminale — e un cuvant
    #complet. Daca are exact lungimea ceruta, il adaugam in rezultate. Altfel il ignoram.
    while coada:
        forma = coada.popleft()

        # gasim primul neterminal (derivare la stanga)
        pozitie = None
        for i in range(len(forma)):
            if forma[i] in neterminale:
                pozitie = i
                break
        if pozitie is None:
            if len(forma) == lungime:
                cuvinte.add("".join(forma))
            continue

        
        #Luam neterminalul gasit si incercam toate productiile posibile pentru el.
        #Construim forma_noua inlocuind neterminalul cu ce produce.
        neterminal = forma[pozitie]
        for sir_simboluri in productii.get(neterminal, []):
            forma_noua = forma[:pozitie] + sir_simboluri + forma[pozitie + 1 :]

            # taiem derivarile care nu mai pot ajunge la lungimea ceruta
            if lungime_minima_forma(forma_noua, terminale, lungime_minima) > lungime:
                continue
            #daca forma nu a mai fost vasuta o adaugam in coada ca sa o procesam mai tarziu
            if forma_noua not in vizitate:
                vizitate.add(forma_noua)
                coada.append(forma_noua)

            #Exemplu: daca forma = ('a', 'S', 'b') si productia e S -> cd, 
            # obtinem forma_noua = ('a', 'c', 'd', 'b').

    return cuvinte


def main():
    neterminale, terminale, productii, simbol_start, lungime = citire("input.txt")

    cuvinte = genereaza(neterminale, terminale, productii, simbol_start, lungime)

    with open("output.txt", "w") as f:
        if cuvinte:
            for cuvant in sorted(cuvinte):
                f.write(cuvant + "\n")
        else:
            f.write("NU EXISTA\n")


if __name__ == "__main__":
    main()
