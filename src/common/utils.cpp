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
    JUMP_UP = 6,
    ERROR = 7
};

enum class instance_opt : signed char {
    QUADRATIC = 0,
    DIAMOND = 1,
    MEMO = 2,
    ERROR = 3
};

instance_opt
inst_o_of_string(std::string t){
    if (t == "quadratic" || t == "QUADRATIC") {return instance_opt::QUADRATIC;}
    if (t == "diamond" || t == "DIAMOND") {return instance_opt::DIAMOND;}
    if (t == "memo" || t == "MEMO") {return instance_opt::MEMO;}
    return instance_opt::ERROR; //invalid   
}

map_opt
mo_of_string(std::string o){
  if (o == "random" || o == "RANDOM") {return map_opt::RANDOM;}
  if (o == "reverse" || o == "REVERSE") {return map_opt::REVERSE;}
  if (o == "jump_down" || o == "JUMP_DOWN") {return map_opt::JUMP_DOWN;}
  if (o == "adj_swap" || o == "ADJ_SWAP") {return map_opt::ADJ_SWAP;}
  if (o == "jump_up" || o == "JUMP_UP") {return map_opt::JUMP_UP;}
  if (o == "odd_split" || o == "ODD_SPLIT") {return map_opt::ODD_SPLIT;}
  if (o == "memo_spec" || o == "MEMO_SPEC") {return map_opt::MEMO_SPEC;}
  return map_opt::ERROR; // invalid! 
} 

template <typename Adapter>
typename Adapter::dd_t
create_diamond(Adapter& adapter, int N, int scale = 1)
{
  const auto top = adapter.build_node(true);
  const auto bot = adapter.build_node(false);

  auto a = top;

  for (int i = N-1; 0 <= i; --i) {
    const int a_var = (2 * i) * scale;
    const int b_var = (2 * i + 1) * scale;
    auto t1 = adapter.build_node(b_var, bot, a);
    auto t2 = adapter.build_node(b_var, a, bot);
    a = adapter.build_node(a_var, t2, t1);
  }
  return adapter.build();
}
template <typename Adapter>
typename Adapter::dd_t
create_memo(Adapter& adapter, int N, int scale = 1)
{
  const auto bot = adapter.build_node(false);
  const auto top = adapter.build_node(true);

  auto b = adapter.build_node((N*2 + 1) * scale, bot, top);
  auto a = adapter.build_node((N*2 + 1) * scale, top, bot);
    for (int i = (N * 2-1); 0 <= i; i -= 2) {
      auto t1 = adapter.build_node((i+1) * scale, b, top);
      auto t2 = adapter.build_node((i+1) * scale, a, bot);
      auto t3 = adapter.build_node((i+1) * scale, a, top);
      a = adapter.build_node(i * scale, t1, t2);
      b = adapter.build_node(i * scale, t1, t3);
    }
    b = adapter.build_node(0, b, a);
  return adapter.build();
}

template <typename Adapter>
typename Adapter::dd_t
create_quadratic(Adapter& adapter, int N, int scale = 1)
{
  const auto bot = adapter.build_node(false);
  const auto top = adapter.build_node(true);

  auto a = top;
  auto b = top;

  for (int i = N-1; 0 <= i; --i) {
    const int a_var = (2 * i + 1) * scale;
    a = adapter.build_node(a_var, bot, a);

    const int b_var = (2 * i) * scale;
    b = adapter.build_node(b_var, b, a);
  }

  return adapter.build();
}


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
                perm.resize(N*2);
                for (int i = 0; i < N * 2; i++){
                    perm[i] = i;
                };
                // New plan make maximal jump in segments
                int segment_size = (N*2)/number_jumps;
                for (int i = 0; i < number_jumps; i++) {
                    int from = i * segment_size;
                    int to = from + segment_size - 1;
                    from = from % 2 == 0 ? from : from + 1;
                    to = to % 2 == 0 ? to - 1 : to;
                    perm[from] = to; 
                }

                //plan: pass amount of jumps to do
                //then segment map into that many parts
                //do a random jump in each
                // int segment_size = (N*2 - 1)/number_jumps;
                // for (int i = 0; i < (N*2-1); i += segment_size){
                //     std::cout << "for loop started for " << i << "\n";
                //     std::uniform_int_distribution<int> tdis(i, i + (segment_size-1));
                //     int j1 = tdis(gen);
                //     int j2 = tdis(gen);
                //     std::cout << "found j1 " << j1 << ", j2: " << j2 << "\n";
                //     int start = std::min(j1,j2);
                //     int to    = std::max(j1,j2);
                //     start = start % 2 == 0 ? start : start - 1 ;
                //     to    = to % 2    == 0 ? to + 1 : to;
                //     std::cout << "found j1 " << start << ", j2: " << to << "\n";
                //     perm[start] = to;
                // }
                break;
            }

            case map_opt::JUMP_UP :{
                perm.resize(N*2);
                //assume only even layers present in bdd
                for (int i = 0; i < N * 2; i++){
                    perm[i] = i;
                };
                int segment_size = (N*2)/number_jumps;
                for (int i = 0; i < number_jumps; i++) {
                    int to = i * segment_size;
                    int from = to + segment_size;
                    from = from % 2 == 0 ? from : from - 1;
                    to = to % 2 == 0 ? to + 1 : to;
                    perm[from] = to; 
                }
                //plan: pass amount of jumps to do
                //then segment map into that many parts
                //do a random jump up in each
                // int segment_size = N/number_jumps;
                // for (int i = 0; i < N; i += segment_size){
                //     std::uniform_int_distribution<int> tdis(i, i+segment_size-1);
                //     int j1 = tdis(gen);
                //     int j2 = tdis(gen);
                //     int start = std::max(j1,j2);
                //     perm[start] = (j1 == start) ? j2*2+1 : j1*2+1 ;
                // }
                break;
            }
            case map_opt::ADJ_SWAP : {
                //makes number of jumps swaps
                for(int j = 0; j < number_jumps; j++) {
                    int pos = (j * N) / number_jumps;

                    // force even index
                    pos = (pos / 2) * 2;
                    if(pos >= N - 1)
                        pos = N - 2;
                    std::swap(perm[pos], perm[pos + 1]);
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
            case map_opt::ERROR : { break; }
        }
    }

  //identity (based on vector)
  Permutation(std::vector<unsigned> p){
    perm = p;
  }

  void print_it(){
    std::cout << "permutation is: ";
    /*int number_mods = 0;
    for (size_t i = 0; i < perm.size(); ++i) { if (i != perm[i]) number_mods++;}
    std::cout << "we change " << number_mods << "layers, should be " << number_mods/2 << "swaps?\n" ;*/
    for (size_t i = 0; i < perm.size(); ++i) { if (i != perm[i]) std::cout << i << ":" << perm[i] <<"; ";}
    std::cout << '\n';
  }
  void print_it(size_t limit){
    std::cout << "permutation is: ";
    for (size_t i = 0; i < perm.size() && i < limit; ++i) {std::cout << i << ":" << perm[i] <<"; ";}
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
