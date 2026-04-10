// Assertions
#include <cassert>

// Data Structures
#include <sstream>
#include <string>

// Types
#include <cstdlib>

#include "common/adapter.h"
#include "common/array.h"
#include "common/chrono.h"
#include "common/input.h"
#include "common/json.h"

#include "queensbuilder.cpp"

#ifdef BDD_BENCHMARK_STATS
size_t largest_bdd = 0;
size_t total_nodes = 0;
#endif // BDD_BENCHMARK_STATS

// ========================================================================== //

class parsing_policy
{
public:
  static constexpr std::string_view name = "Queens";
  static constexpr std::string_view args = "n:";

  static constexpr std::string_view help_text = "        -n n         [8]      Size of board";

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
    default: return true;
    }
  }
};

// ========================================================================== //
template <typename Adapter>
int
run_queens(int argc, char** argv)
{
  bool should_exit = parse_input<parsing_policy>(argc, argv);
  if (should_exit) { return -1; }

  // =========================================================================
  // Initialise package manager
  return run<Adapter>("queens", N * N, [&](Adapter& adapter) {
    uint64_t solutions;

    std::cout << json::field("N") << json::value(N) << json::comma << json::endl;
    std::cout << json::endl << json::flush;

    // ========================================================================
    // Compute the bdd that represents the entire board
    std::cout << json::field("apply") << json::brace_open << json::endl << json::flush;

#ifdef BDD_BENCHMARK_STATS
    std::cout << json::field("intermediate results") << json::brace_open << json::endl;
#endif

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
    // Count number of solutions
    std::cout << json::field("satcount") << json::brace_open << json::endl << json::flush;

    const time_point t3 = now();
    solutions           = adapter.satcount(res);
    const time_point t4 = now();

    const time_duration counting_time = duration_ms(t3, t4);

    std::cout << json::field("result") << json::value(solutions) << json::comma << json::endl;
    std::cout << json::field("time (ms)") << json::value(counting_time) << json::endl;
    std::cout << json::brace_close << json::comma << json::endl << json::flush;

    // ========================================================================
    std::cout << json::field("total time (ms)")
              << json::value(init_time + construction_time + counting_time) << json::endl
              << json::flush;

    if (rows() == cols() && cols() < size(expected) && solutions != expected[cols()]) { return -1; }
    return 0;
  });
}
