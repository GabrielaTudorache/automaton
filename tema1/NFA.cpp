#include "NFA.h"

bool NFA::valideaza() {
    if (!LambdaNFA::valideaza()) return false;

    for (const auto& [stare_sursa, tranzitii_locale]: tranzitii) {
        for (const auto& [simbol, stari_destinatie]: tranzitii_locale) {
            if (simbol == "lambda") return false;
        }
    }

    return true;
}