#ifndef DFA_NFA_DFA_H
#define DFA_NFA_DFA_H

#include "NFA.h"

class DFA : public NFA {
public:
    DFA() = default;
    DFA(std::ifstream& f) : NFA(f) {}

    bool valideaza() override;
};



#endif //DFA_NFA_DFA_H