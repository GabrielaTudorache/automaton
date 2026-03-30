#include "DFA.h"

bool DFA::valideaza() {
    if (!NFA::valideaza()) return false;

    for (const auto& stare: stari) {
        if (!tranzitii.contains(stare)) return false;

        for (const auto& simbol: alfabet) {
            auto it = tranzitii[stare].find(simbol);
            if (it == tranzitii[stare].end()) return false;
            if (it->second.size() != 1) return false;
        }

        for (const auto& [simbol, stari_destinatie]: tranzitii[stare]) {
            if (!alfabet.contains(simbol)) return false;
            if (stari_destinatie.size() != 1) return false;
        }
    }

    return true;
}