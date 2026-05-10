#ifndef DFA_NFA_NFA_H
#define DFA_NFA_NFA_H

#include "LambdaNFA.h"


class NFA : public LambdaNFA {
public:
    NFA() = default;
    NFA(std::ifstream& f) : LambdaNFA(f) {}

    bool valideaza() override;
};



#endif //DFA_NFA_NFA_H