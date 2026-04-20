#include <algorithm>
#include <random>
#include <vector>

class Permutation {
private: 
  std::vector<unsigned> perm;

public:
  Permutation(int N, int seed){
  perm.resize(N);
  for (int i = 0; i < N; i++){
    perm[i] = i;
  };

    std::mt19937 gen(seed);
    std::shuffle(perm.begin(), perm.end(), gen);
  }

  Permutation(int N){
  perm.resize(N);
  for (int i = 0; i < N; i++){
    perm[i] = i;
  };
  std::reverse(perm.begin(), perm.end());
  }

  Permutation(std::vector<unsigned> p){
    perm = p;
  }

  int operator()(int x) const {
    return perm[x];
    }
};


// For testing the random order...
// int main(int argc, char **argv){
// 	int N;
// 	while(true) {
// 		std::cin >> N;
//
// 		Permutation p = Permuation(N, 10);
//
// 		for (int i = 0; i < N; i++) {
// 			std::cout << p(i) << ", ";
// 		}
// 		std::cout << '\n';
// 	}
// }
