// Data Structures
#include <iostream>
#include <string>

#include "common/adapter.h"
#include "common/chrono.h"
#include "common/input.h"
#include "common/json.h"

#include "common/utils.cpp"


// ========================================================================== //
int N = 3;

class parsing_policy
{
public:
  static constexpr std::string_view name = "Test";
  static constexpr std::string_view args = "n:";

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
    default: return true;
    }
  }
};

// ========================================================================== //
template <typename Adapter>
typename Adapter::dd_t
create_input(Adapter& adapter)
{
  const auto bot = adapter.build_node(false);
  const auto top = adapter.build_node(true);

  auto b = adapter.build_node(N*2 + 1, bot, top);
  auto a = adapter.build_node(N*2 + 1, top, bot);
    for (int i = (N * 2-1); 0 <= i; i -= 2) {
      auto t1 = adapter.build_node(i+1, b, top);
      auto t2 = adapter.build_node(i+1, a, bot);
      auto t3 = adapter.build_node(i+1, a, top);
      a = adapter.build_node(i, t1, t2);
      b = adapter.build_node(i, t1, t3);
    }
    b = adapter.build_node(0, b, a);
  return adapter.build();
}

template <typename Adapter>
int
run_memotest(int argc, char** argv)
{
  bool should_exit = parse_input<parsing_policy>(argc, argv);
  if (should_exit) { return -1; }

  const int varcount = 2 * N + 2;

  return run<Adapter>("memoization_replace", varcount, [&](Adapter& adapter) {
    const time_point f_before = now();
    typename Adapter::dd_t f = create_input(adapter);
    const time_point f_after = now();

    std::cout << json::field("f") << json::brace_open << json::endl;
    std::cout << json::field("size (nodes)") << json::value(adapter.nodecount(f)) << json::comma << json::endl;
    std::cout << json::field("time (ms)") << json::value(duration_ms(f_before, f_after)) << json::endl;
    std::cout << json::brace_close << json::comma << json::endl << json::flush;

    Permutation p = Permutation(N, 1, map_opt::MEMO_SPEC);
    // p.print_it();

    // adapter.print_dot(f, "beforeTESTTESTTEST.dot");
    const time_point g_before = now();
    f = adapter.replace(f, p);
    const time_point g_after = now();
    // adapter.print_dot(f, "TESTTESTTEST.dot");


    std::cout << json::field("bdd_replace(f)") << json::brace_open << json::endl;
    std::cout << json::field("size (nodes)") << json::value(adapter.nodecount(f)) << json::comma << json::endl;
    std::cout << json::field("time (ms)") << json::value(duration_ms(g_before, g_after)) << json::endl;
    std::cout << json::brace_close << json::comma << json::endl << json::flush;

    return 0;
  });
  return 1;
}
