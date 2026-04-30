// Assertions
#include <cassert>

// Data Structures
#include <iostream>
#include <string>

// Other

#include "common/adapter.h"
#include "common/chrono.h"
#include "common/input.h"
#include "common/libbdd_parser.h"

#include "queensbuilder.cpp"
#include "utils.cpp"

////////////////////////////////////////////////////////////////////////////////////////////////////
//                                        INPUT PARSING                                           //
////////////////////////////////////////////////////////////////////////////////////////////////////

unsigned int seed = 987654321u;

class parsing_policy
{
public:
  static constexpr std::string_view name = "Replace random";
  static constexpr std::string_view args = "n:s:";

  static constexpr std::string_view help_text = 
    "        -s SEED               Seed used for this run\n"
    "        -n n         [8]      Size of board";

  static inline bool
  parse_input(const int c, const char* arg)
  {
    switch (c) {
    case 'n': {
      N = std::stoi(arg);
      if (N <= 0) {
        std::cerr << "  Must specify positive board size (-n)\n";
        return true;
      }
      return false;
    }
    case 's': {
      seed = std::stoul(arg);
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

  // =============================================================================================
  // Initialize BDD package
  return run<Adapter>("replace", N * N, [&](Adapter& adapter) {

    std::cout << json::field("construction") << json::brace_open << json::endl << json::flush;

#ifdef BDD_BENCHMARK_STATS
    std::cout << json::field("intermediate results") << json::brace_open << json::endl;
#endif

    size_t total_time = 0;

    const time_point t1        = now();
    typename Adapter::dd_t res = queens_B(adapter);
    const time_point t2        = now();

    const time_duration construction_time = duration_ms(t1, t2);

#ifdef BDD_BENCHMARK_STATS
    std::cout << json::brace_close << json::comma << json::endl;
    std::cout << json::field("total processed (nodes)") << json::value(total_nodes) << json::comma
              << json::endl;
    std::cout << json::field("largest size (nodes)") << json::value(largest_bdd) << json::comma
              << json::endl;
#endif // BDD_BENCHMARK_STATS

    std::cout << json::field("final size (nodes)") << json::value(adapter.nodecount(res))
              << json::comma << json::endl;
    std::cout << json::field("time (ms)") << json::value(construction_time) << json::endl;
    std::cout << json::brace_close << json::comma << json::endl << json::flush;


    // ========================================================================
    // Do some replacing in the queens instance

    std::cout << json::field("replace") << json::brace_open << json::endl << json::flush;


    Permutation p = Permutation(N*N, seed, map_opt::RANDOM);

    const time_point t_replace_before = now();
    res = adapter.replace(res, p);
    const time_point t_replace_after = now();

    const size_t replace_time = duration_ms(t_replace_before, t_replace_after);
    total_time += replace_time;

    std::cout << json::field("size (nodes)") << adapter.nodecount(res) << json::comma
              << json::endl;
    std::cout << json::field("satcount") << adapter.satcount(res) << json::comma << json::endl;
    std::cout << json::field("time (ms)") << replace_time << json::endl;

    std::cout << json::brace_close << json::comma << json::endl;

    // =============================================================================================

    std::cout << json::field("total time (ms)") << json::value(init_time + total_time)
              << json::endl;

    return 0;
  });

  return 1;
}
