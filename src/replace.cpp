// Assertions
#include <cassert>

// Data Structures
#include <iostream>
#include <string>

// Other

#include "common/adapter.h"
#include "common/chrono.h"
#include "common/input.h"
#include "common/json.h"
#include "common/libbdd_parser.h"

#include "common/utils.cpp"

////////////////////////////////////////////////////////////////////////////////////////////////////
//                                        INPUT PARSING                                           //
////////////////////////////////////////////////////////////////////////////////////////////////////

unsigned int seed = 987654321u;

int N = 5;
int segments = 2;

int forced_nested = false;
std::string dummy_order = "";
std::string dummy_bdd = "";

map_opt o = map_opt::REVERSE;
instance_opt t = instance_opt::QUADRATIC;

class parsing_policy
{
public:
  static constexpr std::string_view name = "Replace_special_case_bench";
  static constexpr std::string_view args = "n:o:s:t:j:r:";

  static constexpr std::string_view help_text =
  "        -n N          N for chosen instance (e.g. #pairs for quadratic) \n"
  "        -o ORDER      the order to build and apply via replace (e.g. RANDOM)\n"
  "        -s Seed       Seed for the randomness in order \n"
  "        -j segments   Number of segments to split some special cases \n"
  "        -t bdd type   the shape of BDD to perform replace on (e.g. QUADRATIC)"
  "        -r int        1 for forcing nested sweeping algorithm ";

  static inline bool
  parse_input(const int c, const char* arg)
  {
    switch (c) {
    case 'n': {
      N = std::stoi(arg);
      if (N <= 0) {
        std::cerr << "  Must specify positive N\n";
        return true;
      }
      return false;
    }
    case 's': {
      seed = std::stoul(arg);
      return false;
    }
    case 'j': {
      segments = std::stoi(arg);
      if (segments > N) {
        std::cerr << "  Must have more variables (N) than segments\n";
        return true;
      }
      return false;
    }
    case 'o' : {
      o = mo_of_string(arg);
      if (o == map_opt::ERROR) {
        std::cerr << "unknown order " << arg << "\n";
        return true;
      }
      dummy_order = arg;
      return false;
    }
    case 't' : {
      t = inst_o_of_string(arg);
      if (t == instance_opt::ERROR){
        std::cerr << "unknown bdd type " << arg << "\n";
        return true;
      }
      dummy_bdd = arg;
      return false;
    }
    case 'r' : {
      forced_nested = std::stoi(arg) == 1;
      return false;
    }
    default: return true;
    }
  }
};



template <typename Adapter>
int run_replace(int argc, char** argv) {
  bool should_exit = parse_input<parsing_policy>(argc, argv);
  if (should_exit) { return -1; }

    int varcount = 0; 
    switch(t) {
    case instance_opt::DIAMOND: {varcount = N*2; break;}
    case instance_opt::QUADRATIC: {varcount = N*2; break;}
    case instance_opt::MEMO: {varcount = N * 2 + 2 ; break;}
    case instance_opt::ERROR: {return -1;}
    }
    int scale = 1;
    if (o == map_opt::JUMP_DOWN || o == map_opt::JUMP_UP) scale = 2;


  // =============================================================================================
  // Initialize BDD package
  return run<Adapter>("replace", varcount, [&](Adapter& adapter) {

      
    std::cout << json::field("specs") << json::brace_open << json::endl; 
      std::cout << json::field("n") << json::value(N) << json::comma << json::endl;
      std::cout << json::field("bdd type") << json::value(dummy_bdd) << json::comma << json::endl;
      std::cout << json::field("order") << json::value(dummy_order) << json::comma << json::endl;
      std::cout << json::field("segments") << json::value(segments) << json::comma << json::endl;
      std::cout << json::field("nested_sweeping") << json::value(forced_nested) << json::endl;
    std::cout << json::brace_close << json::comma << json::endl << json::flush;

    std::cout << json::field("construction") << json::brace_open << json::endl << json::flush;

#ifdef BDD_BENCHMARK_STATS
    std::cout << json::field("intermediate results") << json::brace_open << json::endl;
#endif
    typename Adapter::dd_t dd;

    size_t total_time = 0;
    const time_point t1 = now();
    switch(t) {
      case instance_opt::DIAMOND: {dd = create_diamond(adapter, N, scale);  break;}
      case instance_opt::QUADRATIC: {dd = create_quadratic(adapter, N, scale); break;}
      case instance_opt::MEMO: {dd = create_memo(adapter, N, scale); break;}
      case instance_opt::ERROR: {return -1;}
    }
    const time_point t2 = now();

    const time_duration construction_time = duration_ms(t1, t2);
    total_time += construction_time;

    std::cout << json::field("final size (nodes)") << json::value(adapter.nodecount(dd))
              << json::comma << json::endl;
    std::cout << json::field("time (ms)") << json::value(construction_time) << json::endl;
    std::cout << json::brace_close << json::comma << json::endl << json::flush;


    // ========================================================================
    // Performing replace in given instance

    std::cout << json::field("replace") << json::brace_open << json::endl << json::flush;

    // adapter.print_dot(dd, "bT.dot");
    Permutation p = Permutation(varcount, seed, o, segments);
    // p.print_it();

    const time_point t_replace_before = now();
    if (forced_nested) {
      dd = adapter.replace_ns(dd, p);
    } else {
      dd = adapter.replace(dd, p);
    }
    const time_point t_replace_after = now();
    // adapter.print_dot(dd, "T.dot");

    const size_t replace_time = duration_ms(t_replace_before, t_replace_after);
    total_time += replace_time;

    std::cout << json::field("size (nodes)") << adapter.nodecount(dd) << json::comma
              << json::endl;
    std::cout << json::field("time (ms)") << replace_time << json::endl;

    std::cout << json::brace_close << json::comma << json::endl;

    // =============================================================================================

    std::cout << json::field("total time (ms)") << json::value(init_time + total_time)
              << json::endl;
    std::cout << json::brace_close << json::endl << json::flush;

    return 0;
  });

  return 1;
}
