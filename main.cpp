#include <iostream>
#include <fstream>
#include <string>
#include "NFA.h"

int main() {
    std::cout<<"Enter the input file name: ";
    std::string filename;
    std::cin>>filename;

    std::ifstream f(filename);

    std::cout<<"Enter the type (DFA/NFA): ";
    std::string type;
    std::cin>>type;

    NFA automaton(f);

    int numar_cuvinte;
    f>>numar_cuvinte;
    for (int i = 0; i < numar_cuvinte; ++i) {
        std::string cuvant;
        f>>cuvant;

        auto rez=automaton.accepta(cuvant);
        if (rez.first) {
            std::cout<<"DA\n";
        }else {
            std::cout<<"NU\n";
        }
    }

}