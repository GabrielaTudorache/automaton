from collections import deque


def citeste_pda(filename):
    with open(filename) as f:
        linii = [line.strip() for line in f if line.strip()]

    stari = set(linii[0].split())
    alfabet = set(linii[1].split())
    alfabet_stiva = set(linii[2].split())
    n = int(linii[3])

    # delta[(stare, simbol_citit, varf_stiva)] = lista de (stare_urmatoare, sir_de_pus)
    # lista pentru ca PDA-ul e nedeterminist
    delta = {}
    for k in range(n):
        stare, simbol, varf, stare_urm, sir_push = linii[4 + k].split()
        cheie = (stare, simbol, varf)
        if cheie not in delta:
            delta[cheie] = []
        delta[cheie].append((stare_urm, sir_push))

    stare_initiala = linii[4 + n]
    simbol_stiva_initial = linii[5 + n]
    stari_finale = set(linii[6 + n].split())
    mod_acceptare = linii[7 + n]
    sir_intrare = linii[8 + n]

    return (
        stari,
        alfabet,
        alfabet_stiva,
        delta,
        stare_initiala,
        simbol_stiva_initial,
        stari_finale,
        mod_acceptare,
        sir_intrare,
    )


def este_acceptata(configuratie, stari_finale, mod_acceptare, lungime_intrare):
    stare, pozitie, stiva = configuratie
    if pozitie != lungime_intrare:
        return False
    if mod_acceptare == "stare finala":
        return stare in stari_finale
    if mod_acceptare == "stiva goala":
        return len(stiva) == 0
    if mod_acceptare == "ambele":
        return stare in stari_finale and len(stiva) == 0
    raise ValueError(f"mod de acceptare necunoscut: {mod_acceptare}")


def succesori(configuratie, delta, sir_intrare):
    stare, pozitie, stiva = configuratie
    # daca stiva e goala, nicio tranzitie nu se mai poate aplica (orice tranzitie cere un varf)
    if len(stiva) == 0:
        return []

    varf = stiva[0]
    rezultate = []

    # tranzitii lambda (nu consuma input)
    for stare_urm, sir_push in delta.get((stare, "lambda", varf), []):
        if sir_push == "lambda":
            stiva_noua = stiva[1:]
        else:
            # primul caracter din sir_push ajunge in varful stivei
            stiva_noua = tuple(sir_push) + stiva[1:]
        rezultate.append((stare_urm, pozitie, stiva_noua))

    # tranzitii care consuma simbolul curent din input
    if pozitie < len(sir_intrare):
        simbol = sir_intrare[pozitie]
        for stare_urm, sir_push in delta.get((stare, simbol, varf), []):
            if sir_push == "lambda":
                stiva_noua = stiva[1:]
            else:
                stiva_noua = tuple(sir_push) + stiva[1:]
            rezultate.append((stare_urm, pozitie + 1, stiva_noua))

    return rezultate


def simuleaza(
    delta,
    stare_initiala,
    simbol_stiva_initial,
    stari_finale,
    mod_acceptare,
    sir_intrare,
    stari,
    alfabet_stiva,
):
    # configuratia: (stare, pozitie_in_input, stiva)
    # stiva[0] = varful
    configuratie_initiala = (stare_initiala, 0, (simbol_stiva_initial,))

    # o tranzitie de tip (q, lambda, A) -> (q, AA) creste stiva la infinit fara sa avanseze in input
    limita_stiva = (
        len(sir_intrare) * len(stari) * len(alfabet_stiva) + len(alfabet_stiva) + 1
    )

    coada = deque([configuratie_initiala])
    vizitate = {configuratie_initiala}

    while coada:
        configuratie = coada.popleft()

        if este_acceptata(configuratie, stari_finale, mod_acceptare, len(sir_intrare)):
            return True

        for urm in succesori(configuratie, delta, sir_intrare):
            if urm in vizitate:
                continue
            if len(urm[2]) > limita_stiva:
                continue
            vizitate.add(urm)
            coada.append(urm)

    return False


def main():
    (
        stari,
        _alfabet,
        alfabet_stiva,
        delta,
        stare_initiala,
        simbol_stiva_initial,
        stari_finale,
        mod_acceptare,
        sir_intrare,
    ) = citeste_pda("input.txt")

    acceptat = simuleaza(
        delta,
        stare_initiala,
        simbol_stiva_initial,
        stari_finale,
        mod_acceptare,
        sir_intrare,
        stari,
        alfabet_stiva,
    )

    with open("output.txt", "w") as f:
        f.write("ACCEPTAT\n" if acceptat else "RESPINS\n")

    print("Rezultatul a fost scris in output.txt")


if __name__ == "__main__":
    main()
