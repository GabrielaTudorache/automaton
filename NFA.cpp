#include "NFA.h"

#include <stack>



NFA::NFA(std::ifstream& f) {
    int n;
    f>>n;
    for (int i = 0; i < n; ++i) {
        std::string stare;
        f>>stare;
        stari.insert(stare);
    }

    int m;
    f>>m;
    for (int i = 0; i < m; ++i) {
        std::string stare_plecare,stare_finala,litera;
        f>>stare_plecare>>stare_finala>>litera;
        tranzitii[stare_plecare][litera].insert(stare_finala);
    }

    f>>stare_initiala;

    int o;
    f>>o;
    for (int i = 0; i < o; ++i) {
        std::string stare;
        f>>stare;
        stari_finale.insert(stare);
    }
}

std::set<std::string> NFA::calcul_lambda_inchidere(std::set<std::string> stari) {
    std::stack<std::string> stiva;
    for (const auto& stare: stari) {
        stiva.push(stare);
    }

    while (!stiva.empty()) {
        std::string stare_curenta = stiva.top();
        stiva.pop();

        auto it = tranzitii[stare_curenta].find("lambda");
        if (it!=tranzitii[stare_curenta].end()) {
            for (const auto& stare_urmatoare : it->second) {
                if (stari.insert(stare_urmatoare).second) {
                    stiva.push(stare_urmatoare);
                }
            }
        }
    }

    return stari;
}

std::set<std::string> NFA::actualizare_stari(const std::set<std::string>& stari,const std::string& simbol) {
    std::set<std::string> rezultat;

    for (const auto& stare: stari) {
        auto it = tranzitii[stare].find(simbol);
        if (it!=tranzitii[stare].end()) {
            for (const auto& stare_urm: it->second) {
                rezultat.insert(stare_urm);
            }
        }
    }

    return rezultat;
}

std::pair<bool,std::vector<std::string>> NFA::accepta(const std::string &input) {
    std::set<std::string> stari_curente = calcul_lambda_inchidere({stare_initiala});

    for (const auto& litera: input) {
        stari_curente=calcul_lambda_inchidere(actualizare_stari(stari_curente,std::string(1, litera)));

        if (stari_curente.empty()) {
            return {false,{}};
        }
    }

    for (const auto& stare: stari_curente) {
        if (stari_finale.contains(stare)) {
            return {true,{}};
        }
    }

    return {false,{}};
}



