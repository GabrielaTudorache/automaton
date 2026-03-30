#ifndef DFA_NFA_LAMBDA_NFA_H
#define DFA_NFA_LAMBDA_NFA_H
#include <fstream>
#include <map>
#include <set>
#include <string>
#include <vector>


class LambdaNFA {
protected:
    std::set<std::string> stari;
    std::set<std::string> alfabet;
    std::string stare_initiala;
    std::set<std::string> stari_finale;
    std::map<std::string,std::map<std::string,std::set<std::string>>> tranzitii;

    std::set<std::string> calcul_lambda_inchidere(std::set<std::string> stari);
    std::set<std::string> actualizare_stari(const std::set<std::string>& stari,const std::string& simbol);
public:
    LambdaNFA() = default;
    virtual ~LambdaNFA() = default;
    LambdaNFA(std::ifstream& f);

    virtual bool valideaza();
    const std::set<std::string>& getAlfabet();
    std::pair<bool,std::vector<std::string>> accepta(const std::string& input);
};



#endif //DFA_NFA_LAMBDA_NFA_H