// Data Structures
#include <iostream>
#include <string>

#include "common/adapter.h"
#include "common/chrono.h"
#include "common/input.h"
#include "common/json.h"

#include "utils.cpp"


// ========================================================================== //
int N = 3;
int v = 2;

class parsing_policy
{
public:
  static constexpr std::string_view name = "Test";
  static constexpr std::string_view args = "n:v:";

  static constexpr std::string_view help_text = "        -n n         [3]      number of pairs";

  static inline bool
  parse_input(const int c, const char* arg)
  {
    switch (c) {
    case 'n': {
      N = std::stoi(arg);
      if (N <= 0) {
        std::cerr << "  Must specify positive number of pairs (-n)\n";
        return true;
      }
      return false;
    }
    case 'v': {
      v = std::stoi(arg);
      if (v < 0) {
        std::cerr << "  Must specify positive number of pairs (-n)\n";
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
typename Adapter::dd_t
create_input(Adapter& adapter)
{
  const auto top = adapter.build_node(true);
  const auto bot = adapter.build_node(false);

  auto a = top;

  for (int i = N-1; 0 <= i; --i) {
    const int a_var = 2 * i;
    const int b_var = 2 * i + 1;
    auto t1 = adapter.build_node(b_var, bot, a);
    auto t2 = adapter.build_node(b_var, a, bot);
    a = adapter.build_node(a_var, t2, t1);
  }
  return adapter.build();
}

// ========================================================================== //
template <typename Adapter>
int
run_quadratic(int argc, char** argv)
{
  bool should_exit = parse_input<parsing_policy>(argc, argv);
  if (should_exit) { return -1; }

  const int varcount = 2 * N;

  return run<Adapter>("diamond-exists", varcount, [&](Adapter& adapter) {
    const time_point f_before = now();
    typename Adapter::dd_t f = create_input(adapter);
    const time_point f_after = now();

    std::cout << json::field("f") << json::brace_open << json::endl;
    std::cout << json::field("size (nodes)") << json::value(bdd_nodecount(f)) << json::comma << json::endl;
    std::cout << json::field("time (ms)") << json::value(duration_ms(f_before, f_after)) << json::endl;
    std::cout << json::brace_close << json::comma << json::endl << json::flush;

    Permutation p = Permutation(varcount, 1, map_opt::ODD_SPLIT);

    f = adapter.replace(f, p);

    // adapter.print_dot(f, "beforeT.dot");
    const time_point g_before = now();
    f = adapter.exists(f, [=](int x){return x % 2;});
    const time_point g_after = now();
    // adapter.print_dot(f, "T.dot");

    std::cout << json::field("bdd_exists(f)") << json::brace_open << json::endl;
    std::cout << json::field("size (nodes)") << json::value(bdd_nodecount(f)) << json::comma << json::endl;
    std::cout << json::field("time (ms)") << json::value(duration_ms(g_before, g_after)) << json::endl;
    std::cout << json::brace_close << json::comma << json::endl << json::flush;

    return 0;
  });
  return 1;
}
