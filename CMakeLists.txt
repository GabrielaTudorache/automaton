cmake_minimum_required(VERSION 4.1)
project(dfa_nfa)

set(CMAKE_CXX_STANDARD 20)

add_executable(dfa_nfa main.cpp
        NFA.cpp
        NFA.h)

configure_file(dfa_example.txt dfa_example.txt COPYONLY)
configure_file(nfa_example.txt nfa_example.txt COPYONLY)
configure_file(lambda_nfa_example.txt lambda_nfa_example.txt COPYONLY)

