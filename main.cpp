#include <iostream>
#include <fstream>
#include <string>
#include "LambdaNFA.h"
#include "NFA.h"
#include "DFA.h"

int main() {
    std::cout<<"Enter the input file name: ";
    std::string filename;
    std::cin>>filename;

    std::ifstream f(filename);

    std::cout<<"Enter the type (LambdaNFA/NFA/DFA): ";
    std::string type;
    std::cin>>type;

    LambdaNFA* automaton;
    if (type == "LambdaNFA") {
        automaton = new LambdaNFA(f);
    }else if (type == "NFA") {
        automaton = new NFA(f);
    }else if (type == "DFA") {
        automaton = new DFA(f);
    }else {
        std::cout<<"Invalid\n";
        return 0;
    }

    if (!automaton->valideaza()) {
        std::cout<<"Invalid\n";
        delete automaton;
        return 0;
    }

    int numar_cuvinte;
    f>>numar_cuvinte;
    for (int i = 0; i < numar_cuvinte; ++i) {
        std::string cuvant;
        f>>cuvant;

        auto rez=automaton->accepta(cuvant);
        if (rez.first) {
            std::cout<<"DA\n";
        }else {
            std::cout<<"NU\n";
        }
    }

    delete automaton;
}