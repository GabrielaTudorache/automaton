LAMBDA = ("lambda",)
#am acelasi sistem de date ca in cerinta2

# constructori cu simplificare automata
# diferenta e ca la concat si union nu mai au cazul empty(nu generam expresii vide, 
# plecam de la un string valid)
def concat(r1, r2):
    if r1 == LAMBDA:
        return r2
    if r2 == LAMBDA:
        return r1
    return ("concat", r1, r2)


def union(r1, r2):
    if r1 == r2:
        return r1
    return ("union", r1, r2)


def star(r):
    if r == LAMBDA:
        return LAMBDA
    if r[0] == "star":
        return r
    return ("star", r)


# tokeni produsi:
# ("sym", c)  -- un simbol din alfabet
# ("lambda",) -- cuvantul vid (keyword in input)
# ("(",), (")",), ("*",), ("|",) -- paranteze si operatori expliciti
# (".",) -- concat implicit, inserat ulterior de insereaza_concat
def tokenizeaza(regex):
    tokeni = []
    i = 0
    while i < len(regex):
        c = regex[i]
        if c.isspace():
            i += 1
        elif regex[i : i + 6] == "lambda":
            tokeni.append(LAMBDA)
            i += 6
        elif c in "*|()":
            tokeni.append((c,))
            i += 1
        else:
            tokeni.append(("sym", c))
            i += 1
    return tokeni

#Exemplu: "ab|c*" → [("sym","a"), ("sym","b"), ("|",), ("sym","c"), ("*",)]

#parcurg tokeni si colectez toate simblourile de tip "sym" - necesar pt a stii ce litere
#apar in expresie
def alfabet_din_tokeni(tokeni):
    alfabet = set()
    for t in tokeni:
        if t[0] == "sym":
            alfabet.add(t[1])
    return alfabet


def insereaza_concat(tokeni):
    # un atom e o subexpresie care produce o singura valoare .Poate incheia cu:
    # un simbol, lambda,orice intre paranteze,sau * . Poate deschide cu simbol, lambda,
    #sau paranteza deschisa.
    # intre doua atomuri adiacente trebuie un concat implicit, marcat cu "."
    inchide_atom = {"sym", "lambda", ")", "*"}
    deschide_atom = {"sym", "lambda", "("}
    rezultat = []
    for i, t in enumerate(tokeni):
        if i > 0 and tokeni[i - 1][0] in inchide_atom and t[0] in deschide_atom:
            rezultat.append((".",))
        rezultat.append(t)
    return rezultat

#Exemplu: [("sym","a"), ("sym","b")] → [("sym","a"), (".",), ("sym","b")]

# ordinea operatorilor: | < concat < *
PRECEDENTA = {"|": 1, ".": 2, "*": 3}

#converteste expresia din scrierea umana intr-o scriere mai usor de procesat de calculator
def shunting_yard(tokeni):
    iesire = []
    stiva = []
    for t in tokeni:
        tip = t[0]
        #Operanzii (simboluri, lambda) merg direct în output
        if tip in ("sym", "lambda"):
            iesire.append(t)
        #paranteza deschisa se pune pe stiva
        elif tip == "(":
            stiva.append(t)
        #paranteza inchisa scoate toti operatorii pana la paranteza deschisa
        elif tip == ")":
            while stiva[-1][0] != "(":
                iesire.append(stiva.pop())
            stiva.pop()
        #Cand gasim un operator, scoatem din stiva in output toti operatorii cu precedenta
        #mai mare sau egala, apoi punem operatorul curent pe stiva.
        else:
            while (
                stiva
                and stiva[-1][0] != "("
                and PRECEDENTA[stiva[-1][0]] >= PRECEDENTA[tip]
            ):
                iesire.append(stiva.pop())
            stiva.append(t)

    while stiva:
        iesire.append(stiva.pop())
    return iesire

#Exemplu: a.(b|c)* → a b c | * .

def construieste_ast(postfix):
    # daca expresia e vida, tratam ca {lambda} (accepta doar cuvantul vid)
    if not postfix:
        return LAMBDA
    stiva = []

    #Operanzii se pun pe stiva
    for t in postfix:
        tip = t[0]
        if tip == "sym":
            stiva.append(("sym", t[1]))
        elif tip == "lambda":
            stiva.append(LAMBDA)
        #Operatorii unari (*) iau un operand, cei binari (., |) iau doi. Ordinea conteaza:
        #r2 se scoate primul din stiva, r1 al doilea.
        elif tip == "*":
            stiva.append(star(stiva.pop()))
        elif tip == ".":
            r2 = stiva.pop()
            r1 = stiva.pop()
            stiva.append(concat(r1, r2))
        elif tip == "|":
            r2 = stiva.pop()
            r1 = stiva.pop()
            stiva.append(union(r1, r2))
    return stiva[0]
    #la final pe stiva ramane doar radacina arborelui

#generez un nume unic
def nume_stare_noua(stari):
    nume = f"q{len(stari)}"
    stari.add(nume)
    return nume

#adaug tranzitia in dictionar 
def adauga_tranzitie(tranzitii, stare_plecare, stare_finala, simbol):
    cheie = (stare_plecare, simbol)
    if cheie not in tranzitii:
        tranzitii[cheie] = set()
    tranzitii[cheie].add(stare_finala)


# constructia Thompson: pentru fiecare nod returnam (stare_intrare, stare_iesire)
# si adaugam stari/tranzitii
def thompson(r, stari, tranzitii):
    #s --lambda--> f
    if r == LAMBDA:
        s = nume_stare_noua(stari)
        f = nume_stare_noua(stari)
        adauga_tranzitie(tranzitii, s, f, "lambda")
        return s, f
    #s --a--> f
    if r[0] == "sym":
        s = nume_stare_noua(stari)
        f = nume_stare_noua(stari)
        adauga_tranzitie(tranzitii, s, f, r[1])
        return s, f

    #Construieste fragmentele pentru r1 si r2, le leaga cu lambda. Iesirea lui r1
    #devine intrarea lui r2.
    #s1 --[r1]--> f1 --lambda--> s2 --[r2]--> f2
    if r[0] == "concat":
        s1, f1 = thompson(r[1], stari, tranzitii)
        s2, f2 = thompson(r[2], stari, tranzitii)
        adauga_tranzitie(tranzitii, f1, s2, "lambda")
        return s1, f2

    #stare noua s cu lambda spre ambele fragmente, ambeloe ies prin lambda spre starea noua f
    if r[0] == "union":
        s1, f1 = thompson(r[1], stari, tranzitii)
        s2, f2 = thompson(r[2], stari, tranzitii)
        s = nume_stare_noua(stari)
        f = nume_stare_noua(stari)
        adauga_tranzitie(tranzitii, s, s1, "lambda")
        adauga_tranzitie(tranzitii, s, s2, "lambda")
        adauga_tranzitie(tranzitii, f1, f, "lambda")
        adauga_tranzitie(tranzitii, f2, f, "lambda")
        return s, f

    if r[0] == "star":
        s1, f1 = thompson(r[1], stari, tranzitii)
        s = nume_stare_noua(stari)
        f = nume_stare_noua(stari)
        # din s putem intra in fragment (s -> s1) sau il sarim (s -> f, pentru 0 repetitii)
        # din f1 putem relua (f1 -> s1) sau iesi (f1 -> f)
        adauga_tranzitie(tranzitii, s, s1, "lambda")
        adauga_tranzitie(tranzitii, s, f, "lambda")
        adauga_tranzitie(tranzitii, f1, s1, "lambda")
        adauga_tranzitie(tranzitii, f1, f, "lambda")
        return s, f

    raise ValueError(f"nod regex necunoscut: {r}")


def cheie_stare(nume):
    # sortare naturala pe "qN": "q2" < "q10"
    i = 0
    while i < len(nume) and not nume[i].isdigit():
        i += 1
    prefix, sufix = nume[:i], nume[i:]
    return (prefix, int(sufix) if sufix else 0)

#foloseste cheie_stare pentru a sorta starile in output intr-o ordine naturala (q1, q2, q10, nu q1, q10, q2)
def cheie_muchie(muchie):
    stare_p, stare_f, simbol = muchie
    return (cheie_stare(stare_p), cheie_stare(stare_f), simbol)


def formateaza_lnfa(stari, alfabet, tranzitii, stare_initiala, stare_finala):
    muchii = []
    for (stare_p, simbol), destinatii in tranzitii.items():
        for stare_f in destinatii:
            muchii.append((stare_p, stare_f, simbol))
    muchii.sort(key=cheie_muchie)

    linii = [
        " ".join(sorted(stari, key=cheie_stare)),
        " ".join(sorted(alfabet)),
        str(len(muchii)),
    ]
    for stare_p, stare_f, simbol in muchii:
        linii.append(f"{stare_p} {stare_f} {simbol}")
    linii.append(stare_initiala)
    linii.append(stare_finala)
    return "\n".join(linii)


def main():
    with open("input.txt") as f:
        regex = f.read().strip()

    tokeni = tokenizeaza(regex)
    alfabet = alfabet_din_tokeni(tokeni)

    tokeni_cu_concat = insereaza_concat(tokeni)
    postfix = shunting_yard(tokeni_cu_concat)
    ast = construieste_ast(postfix)

    stari = set()
    tranzitii = {}
    stare_initiala, stare_finala = thompson(ast, stari, tranzitii)

    with open("output.txt", "w") as f:
        f.write(
            formateaza_lnfa(stari, alfabet, tranzitii, stare_initiala, stare_finala)
        )
        f.write("\n")

    print("Rezultatul a fost scris in output.txt")


if __name__ == "__main__":
    main()
