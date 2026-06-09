from collections import deque


def citeste_automat(filename):
    with open(filename) as f:
        linii = [line.strip() for line in f if line.strip()]

    stari = set(linii[0].split())
    alfabet = set(linii[1].split())
    n = int(linii[2])

    #dictionar de seturi pt ca NFA-ul poate merge in mai multe stari pe acelasi simbol
    tranzitii = {}
    for k in range(n):
        stare_plecare, stare_finala, litera = linii[3 + k].split()
        if (stare_plecare, litera) not in tranzitii:
            tranzitii[(stare_plecare, litera)] = set()
        tranzitii[(stare_plecare, litera)].add(stare_finala)

    stare_initiala = linii[3 + n]
    stari_finale = set(linii[4 + n].split())

    return stari, alfabet, tranzitii, stare_initiala, stari_finale

#Fac un BFS care urmareste doar tranzitiile lambda.
#Practic din starea q,unde pot ajunge fara sa citesc nimic? 
#Toate starile pe care le gasesc astfel le adaug in inchidere, 
# pentru ca daca pot ajunge acolo fara sa citesc nimic,
# inseamna ca pot fi considerate echivalente cu starea q.
# Daca am gasit o stare noua, o adaug in coada ca sa verific si tranzitiile lambda din ea. 
# Returnez un frozenset pentru ca vreau sa folosesc rezultatul ca si cheie in dictionar.

#Exemplu: Daca din q0 ajungi in q1 prin lambda, si din q1 ajungi in q2 prin lambda,
# atunci lambda-inchiderea lui q0 = {q0, q1, q2}.
def calcul_lambda_inchidere(stare, tranzitii):
    inchidere = {stare}
    coada = deque([stare])

    while coada:
        stare_curenta = coada.popleft()
        for stare_urmatoare in tranzitii.get((stare_curenta, "lambda"), set()):
            if stare_urmatoare not in inchidere:
                inchidere.add(stare_urmatoare)
                coada.append(stare_urmatoare)

    return frozenset(inchidere)

# o stare din DFA-ul echivalent e un set de stari din NFA, 
#care reprezinta toate starile in care poate fi NFA-ul dupa ce citeste un cuvant.
def constructie_submultimi(stare_initiala, alfabet, tranzitii, stari_finale, inchideri):
    multime_initiala = inchideri[stare_initiala]

    # nume[multime] = "q0", "q1", ...
    # cheile sunt si starile vizitate
    nume = {multime_initiala: "q0"}
    coada = deque([multime_initiala])
    tranzitii_dfa = {}
    stari_finale_dfa = set()

    while coada:
        #incep cu prima multime din coada, care reprezinta o stare din DFA
        multime_curenta = coada.popleft()

        # o stare DFA e finala daca contine cel putin o stare finala NFA
        if multime_curenta & stari_finale:
            stari_finale_dfa.add(nume[multime_curenta])

        
        for simbol in alfabet:
            # pas 1: pentru fiecare litera din alfabet, calculez unde ajunge DFA-ul
            destinatii_directe = set()

            #din fiecare stare NFA din multimea curenta, vad unde pot ajunge pe simbolul curent
            # si adun toate destinatiile. 
            #Daca nici o tranzitie nu este posibila, trec la urmatorul simbol.
            # (stare moarta care va fi adaugata mai tarziu)
            for stare in multime_curenta:
                destinatii_directe |= tranzitii.get((stare, simbol), set())
            if not destinatii_directe:
                continue

            #Exemplu: mulțimea curenta e {q0, q1}, simbolul e a:
            #din q0 pe a ajungi in {q1}
            #din q1 pe a ajungi in {q2}
            #destinatii_directe = {q1, q2}
            
            # pas 2: Aplic lambda-inchiderea pe toate starile din destinatii_directe,
            # pentru ca DFA-ul poate ajunge acolo fara sa citeasca nimic si trebuie sa includ toate starile.
            multime_urmatoare = set()
            for stare in destinatii_directe:
                multime_urmatoare |= inchideri[stare]
            multime_urmatoare = frozenset(multime_urmatoare)

            #Exemplu: destinatii_directe = {q1, q2}:
            # inchideri[q1] = {q1}
            # inchideri[q2] = {q2}
            # multime_urmatoare = {q1, q2}

            # daca multimea e noua, ii dam un nume si o adaugam in coada ca sa o procesam si pe ea mai tarziu
            if multime_urmatoare not in nume:
                nume[multime_urmatoare] = f"q{len(nume)}"
                coada.append(multime_urmatoare)

            tranzitii_dfa[(nume[multime_curenta], simbol)] = nume[multime_urmatoare]

    return set(nume.values()), nume[multime_initiala], stari_finale_dfa, tranzitii_dfa

#DFA-ul construit poate avea lipsuri, adica combinatii (stare,simbol) fara tranzitie. 
# Pentru minimizare am nevoie ca functia de tranzitie sa fie totala,
# adica sa existe o tranzitie pentru orice combinatie stare-simbol.
def adauga_stare_moarta(stari_dfa, alfabet, tranzitii_dfa):
    # o functie de tranzitie completa este necesara pentru algoritmul de minimizare
    stare_moarta = "DEAD"
    a_fost_folosita = False

    #orice tranzitie care nu exista in DFA duce la starea moarta
    for stare in list(stari_dfa):
        for simbol in alfabet:
            if (stare, simbol) not in tranzitii_dfa:
                tranzitii_dfa[(stare, simbol)] = stare_moarta
                a_fost_folosita = True

    #daca starea moarta a fost folosita macar o data,
    #o adaug in multimea de stari si ii adaug tranzitii catre ea pentru toate simbolurile
    if a_fost_folosita:
        stari_dfa.add(stare_moarta)
        for simbol in alfabet:
            tranzitii_dfa[(stare_moarta, simbol)] = stare_moarta

    return stari_dfa, tranzitii_dfa

#Daca exista stari in DFA care nu pot fi atinse din starea initiala, 
#ele nu afecteaza limbajul recunoscut si pot fi eliminate pentru a simplifica automatul.
def elimina_inaccesibile(stare_initiala, stari_dfa, tranzitii_dfa, alfabet):
    accesibile = {stare_initiala}
    coada = deque([stare_initiala])
    #BFS pentru a gasi toate starile accesibile din starea initiala
    while coada:
        stare = coada.popleft()
        for simbol in alfabet:
            destinatie = tranzitii_dfa.get((stare, simbol))
            if destinatie and destinatie not in accesibile:
                accesibile.add(destinatie)
                coada.append(destinatie)
    #pastrez doar starile si tranzitiile accesibile, restul le elimin
    tranzitii_noii = {}
    for (stare, simbol), destinatie in tranzitii_dfa.items():
        if stare in accesibile:
            tranzitii_noii[(stare, simbol)] = destinatie
    return accesibile, tranzitii_noii



def minimizeaza(
    stari_dfa, alfabet, stare_initiala_dfa, stari_finale_dfa, tranzitii_dfa
):
    # doua stari sunt echivalente daca, citind orice cuvant, ajung in stari de acelasi tip
    # incepem cu doua grupuri: stari finale si stari non-finale
    stari_finale_in_dfa = stari_finale_dfa & stari_dfa
    stari_non_finale = stari_dfa - stari_finale_in_dfa

    partitie = []
    if stari_finale_in_dfa:
        partitie.append(frozenset(stari_finale_in_dfa))
    if stari_non_finale:
        partitie.append(frozenset(stari_non_finale))

    alfabet_sortat = sorted(alfabet)

    while True:
        # mapare stare -> indexul grupului din care face parte
        stare_la_grup = {}
        for i, grup in enumerate(partitie):
            for stare in grup:
                stare_la_grup[stare] = i

        noua_partitie = []
        s_a_schimbat = False

        for grup in partitie:
            # impart starile dupa "semnatura": pe ce grup ajung pe fiecare simbol
            impartiri = {}
            for stare in grup:
                semnatura = tuple(
                    stare_la_grup[tranzitii_dfa[(stare, simbol)]]
                    for simbol in alfabet_sortat
                )
                if semnatura not in impartiri:
                    impartiri[semnatura] = set()
                impartiri[semnatura].add(stare)

            if len(impartiri) > 1:
                s_a_schimbat = True
            for grup_nou in impartiri.values():
                noua_partitie.append(frozenset(grup_nou))

        #Exemplu: pe a ajunge în grupa 0, pe b ajunge în grupa 1 → semnatura = (0, 1).
        #Daca doua stari din aceeasi grupa au semnaturi diferite, ele nu sunt echivalente deci grupa se sparge.

        partitie = noua_partitie
        if not s_a_schimbat:
            break

    # ordonam grupurile: cel cu starea initiala primul, restul alfabetic dupa cea mai mica stare
    def cheie_sortare(grup):
        if stare_initiala_dfa in grup:
            return (0, "")
        return (1, sorted(grup)[0])

    ordonate = sorted(partitie, key=cheie_sortare)

    # asignam nume r0, r1, r2, ... fiecarei stari din DFA-ul minim
    nume_partitie = {}
    for i, grup in enumerate(ordonate):
        for stare in grup:
            nume_partitie[stare] = f"r{i}"

    stari_min = set(nume_partitie.values())
    stare_initiala_min = nume_partitie[stare_initiala_dfa]
    stari_finale_min = {
        nume_partitie[s] for s in stari_finale_dfa if s in nume_partitie
    }

    # construim tranzitiile: luam un reprezentant din fiecare grup
    # (toate starile din grup au tranzitii echivalente)
    tranzitii_min = {}
    for grup in ordonate:
        reprezentant = min(grup)
        nume_grup = nume_partitie[reprezentant]
        for simbol in alfabet_sortat:
            destinatie = tranzitii_dfa.get((reprezentant, simbol))
            if destinatie in nume_partitie:
                tranzitii_min[(nume_grup, simbol)] = nume_partitie[destinatie]

    return stari_min, stare_initiala_min, stari_finale_min, tranzitii_min

#Scrierea in fisier 
def formateaza_dfa(stari, stare_initiala, stari_finale, tranzitii, alfabet):
    linii = [
        " ".join(sorted(stari)),
        " ".join(sorted(alfabet)),
        str(len(tranzitii)),
    ]
    for (stare, simbol), destinatie in sorted(tranzitii.items()):
        linii.append(f"{stare} {destinatie} {simbol}")
    linii.append(stare_initiala)
    linii.append(" ".join(sorted(stari_finale)))
    return "\n".join(linii)


def main():
    stari, alfabet, tranzitii, stare_initiala, stari_finale = citeste_automat(
        "input.txt"
    )

    inchideri = {stare: calcul_lambda_inchidere(stare, tranzitii) for stare in stari}

    stari_dfa, stare_initiala_dfa, stari_finale_dfa, tranzitii_dfa = (
        constructie_submultimi(
            stare_initiala, alfabet, tranzitii, stari_finale, inchideri
        )
    )
    stari_dfa, tranzitii_dfa = adauga_stare_moarta(stari_dfa, alfabet, tranzitii_dfa)
    stari_dfa, tranzitii_dfa = elimina_inaccesibile(
        stare_initiala_dfa, stari_dfa, tranzitii_dfa, alfabet
    )

    stari_min, stare_initiala_min, stari_finale_min, tranzitii_min = minimizeaza(
        stari_dfa, alfabet, stare_initiala_dfa, stari_finale_dfa, tranzitii_dfa
    )

    with open("output.txt", "w") as f:
        f.write("=== DFA echivalent ===\n")
        f.write(
            formateaza_dfa(
                stari_dfa, stare_initiala_dfa, stari_finale_dfa, tranzitii_dfa, alfabet
            )
        )
        f.write("\n\n=== DFA minim ===\n")
        f.write(
            formateaza_dfa(
                stari_min, stare_initiala_min, stari_finale_min, tranzitii_min, alfabet
            )
        )
        f.write("\n")

    print("Rezultatul a fost scris in output.txt")


if __name__ == "__main__":
    main()
