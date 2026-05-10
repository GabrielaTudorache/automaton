# ("empty",) -- limbajul vid
# ("lambda",) -- {lambda}, cuvantul vid
# ("sym", c) -- un singur simbol
# ("concat", r1, r2) -- r1 . r2
# ("union", r1, r2) -- r1 | r2
# ("star", r) -- r*

EMPTY = ("empty",)
LAMBDA = ("lambda",)


# constructori cu simplificare automata
# fara ei, output-ul iese plin de (lambda|lambda), (a|a), paranteze inutile etc
def concat(r1, r2):
    if r1 == EMPTY or r2 == EMPTY:
        return EMPTY
    if r1 == LAMBDA:
        return r2
    if r2 == LAMBDA:
        return r1
    return ("concat", r1, r2)


def union(r1, r2):
    if r1 == EMPTY:
        return r2
    if r2 == EMPTY:
        return r1
    if r1 == r2:
        return r1
    return ("union", r1, r2)


def star(r):
    if r == EMPTY or r == LAMBDA:
        return LAMBDA
    if r[0] == "star":
        return r
    return ("star", r)


# precedenta: union < concat < star < atom (literal/paranteza)
PREC_UNION = 0
PREC_CONCAT = 1
PREC_STAR = 2
PREC_ATOM = 3


def regex_la_string(r):
    text, _ = formateaza(r)
    return text


def formateaza(r):
    # intoarce (string, precedenta) ca sa stie parintele cand sa puna paranteze
    if r == EMPTY:
        return "vid", PREC_ATOM
    if r == LAMBDA:
        return "lambda", PREC_ATOM
    if r[0] == "sym":
        return r[1], PREC_ATOM
    if r[0] == "star":
        s, p = formateaza(r[1])
        if p < PREC_STAR:
            s = f"({s})"
        return f"{s}*", PREC_STAR
    if r[0] == "concat":
        s1, p1 = formateaza(r[1])
        s2, p2 = formateaza(r[2])
        if p1 < PREC_CONCAT:
            s1 = f"({s1})"
        if p2 < PREC_CONCAT:
            s2 = f"({s2})"
        return f"{s1}{s2}", PREC_CONCAT
    if r[0] == "union":
        s1, _ = formateaza(r[1])
        s2, _ = formateaza(r[2])
        return f"{s1}|{s2}", PREC_UNION
    raise ValueError(f"nod regex necunoscut: {r}")


def citeste_automat(filename):
    with open(filename) as f:
        linii = [line.strip() for line in f if line.strip()]

    stari = set(linii[0].split())
    alfabet = set(linii[1].split())
    n = int(linii[2])

    # R[(p, q)] = expresia regulata curenta pentru muchia p -> q
    # daca o pereche nu apare in dict, eticheta e EMPTY (limbaj vid)
    R = {}
    for k in range(n):
        stare_plecare, stare_finala, simbol = linii[3 + k].split()
        if simbol == "lambda":
            eticheta = LAMBDA
        else:
            eticheta = ("sym", simbol)
        cheie = (stare_plecare, stare_finala)
        if cheie in R:
            R[cheie] = union(R[cheie], eticheta)
        else:
            R[cheie] = eticheta

    stare_initiala = linii[3 + n]
    stari_finale = set(linii[4 + n].split())

    return stari, alfabet, R, stare_initiala, stari_finale


def nume_unic(prefix, stari):
    i = 0
    while f"{prefix}{i}" in stari:
        i += 1
    return f"{prefix}{i}"


def adauga_stari_auxiliare(stari, R, stare_initiala, stari_finale):
    # vrem o singura intrare si o singura iesire, ca la final raspunsul sa fie exact R[(q_start, q_final)]
    # legam q_start de vechea stare initiala printr-o muchie lambda, si fiecare veche stare finala de q_final la fel
    q_start = nume_unic("S", stari)
    stari.add(q_start)
    q_final = nume_unic("F", stari)
    stari.add(q_final)

    R[(q_start, stare_initiala)] = LAMBDA
    for stare_f in stari_finale:
        R[(stare_f, q_final)] = LAMBDA

    return q_start, q_final


def elimina_stare(R, stari, q):
    bucla = R.get((q, q), EMPTY)
    star_bucla = star(bucla)

    predecesori = [p for p in stari if p != q and R.get((p, q), EMPTY) != EMPTY]
    succesori = [r for r in stari if r != q and R.get((q, r), EMPTY) != EMPTY]

    for p in predecesori:
        for r in succesori:
            # drumul p -> q -> (self-loop la q) -> r devine o noua eticheta directa p -> r
            drum_prin_q = concat(R[(p, q)], concat(star_bucla, R[(q, r)]))
            existent = R.get((p, r), EMPTY)
            R[(p, r)] = union(existent, drum_prin_q)

    chei_de_sters = [cheie for cheie in R if q in cheie]
    for cheie in chei_de_sters:
        del R[cheie]


def state_elimination(stari, R, q_start, q_final):
    # eliminam pe rand toate starile intermediare (in ordine sortata)
    intermediare = sorted(stari - {q_start, q_final})

    for q in intermediare:
        elimina_stare(R, stari, q)
        stari.discard(q)

    return R.get((q_start, q_final), EMPTY)


def main():
    stari, _alfabet, R, stare_initiala, stari_finale = citeste_automat("input.txt")

    q_start, q_final = adauga_stari_auxiliare(stari, R, stare_initiala, stari_finale)
    regex_final = state_elimination(stari, R, q_start, q_final)

    with open("output.txt", "w") as f:
        f.write(regex_la_string(regex_final))
        f.write("\n")

    print("Rezultatul a fost scris in output.txt")


if __name__ == "__main__":
    main()
