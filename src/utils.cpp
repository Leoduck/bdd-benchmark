#include <algorithm>
#include <cstddef>
#include <iostream>
#include <random>
#include <vector>

enum class map_opt : signed char {
    RANDOM = 0,
    REVERSE = 1,
    JUMP_DOWN = 2,
    ADJ_SWAP = 3,
    ODD_SPLIT = 4,
    MEMO_SPEC = 5,
    JUMP_UP = 6
};


class Permutation {
private: 
  std::vector<unsigned> perm;


public:
    //random seeded permutation
    Permutation(int N, int seed, map_opt po, int number_jumps=0){
        perm.resize(N);
        for (int i = 0; i < N; i++){
            perm[i] = i;
        };

        std::mt19937 gen(seed);
        switch (po) {
            case map_opt::RANDOM : {
                //gen random permutation
                std::shuffle(perm.begin(), perm.end(), gen);
                break;}
            case map_opt::REVERSE : {
                //gen reverse permutation
                std::reverse(perm.begin(), perm.end());
                break;}
            case map_opt::ODD_SPLIT : {
                int n = perm.size();
                std::vector<unsigned> result(n);

                int i = 0;
                int evenIndex = 0;
                int oddIndex = n / 2;

                for (unsigned x : perm) {
                    if (x % 2 == 0) {
                        result[i] = evenIndex++;
                    } else {
                        result[i] = oddIndex++;
                    }
                    ++i;
                }
                perm = result;
                break;}
            case map_opt::JUMP_DOWN :{
                //assume only even layers present in bdd
                for (int i = 0; i < N; i++){
                    perm[i] = 2*i;
                };
                //plan: pass amount of jumps to do
                //then segment map into that many parts
                //do a random jump in each
                int segment_size = N/number_jumps;
                for (int i = 0; i < N; i += segment_size){
                    std::uniform_int_distribution<int> tdis(i, i+segment_size-1);
                    int j1 = tdis(gen);
                    int j2 = tdis(gen);
                    int start = std::min(j1,j2);
                    perm[start] = (j1 == start) ? j2*2+1 : j1*2+1 ;
                }
                break;
            }

            case map_opt::JUMP_UP :{
                //assume only even layers present in bdd
                for (int i = 0; i < N; i++){
                    perm[i] = 2*i;
                };
                //plan: pass amount of jumps to do
                //then segment map into that many parts
                //do a random jump up in each
                int segment_size = N/number_jumps;
                for (int i = 0; i < N; i += segment_size){
                    std::uniform_int_distribution<int> tdis(i, i+segment_size-1);
                    int j1 = tdis(gen);
                    int j2 = tdis(gen);
                    int start = std::max(j1,j2);
                    perm[start] = (j1 == start) ? j2*2+1 : j1*2+1 ;
                }
                break;
            }
            case map_opt::ADJ_SWAP : {
                // pick a number of layers randomly 
                //swap them with their lower neighbour
                //number of swaps
                std::uniform_int_distribution<int> dis(0, (N/2)-1);
                int number_of_swaps = dis(gen);
                int segment_size = N/number_of_swaps;
                for(int i = 0 ; i < N ; i+=segment_size){
                    std::uniform_int_distribution<int> tdis(i, i+segment_size-2);
                    int swap_top = tdis(gen);
                    perm[swap_top] = swap_top+1;
                    perm[swap_top+1] = swap_top;
                }
                break;
            }
            case map_opt::MEMO_SPEC : {
                // Move all odd layers to the bottom
                perm.resize(N*2+2);
                  for (int i = 0; i < N*2+2; i++){
                      perm[i] = i;
                  };
                int counter = N + 1;
                for(int i = 1 ; i < (N*2 + 2) ; i += 1){
                    if (i % 2 == 0) {perm[i] = i/2;}
                    else if (i == N*2 +1) {perm[i] = ((i-1)/2) +1;} //last layer
                    else { perm[i] = i + counter--;}
                }
                break;
            }
        }
    }

  //identity (based on vector)
  Permutation(std::vector<unsigned> p){
    perm = p;
  }

  void print_it(){
    std::cout << "permutation is: ";
    for (size_t i = 0; i < perm.size(); ++i) {std::cout << i << ":" << perm[i] <<"; ";}
    std::cout << '\n';
  }

  //perm is func :D
  int operator()(int x) const {
    return perm[x];
    }
};


// For testing the permutations...
 // int main(int argc, char **argv){
 //   int N, seed;
 //   while(true) {
 //     std::cin >> N;
 //     std::cin >> seed;
 //     Permutation p = Permutation(N, seed, map_opt::MEMO_SPEC);
 //     for (int i = 0; i < N; i++) {
 //       std::cout << p(i) << ", ";
 //     }
 //     std::cout << '\n';
 //   }
 // }
