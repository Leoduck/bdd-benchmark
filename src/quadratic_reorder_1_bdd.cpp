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
  const auto bot = adapter.bot();
  const auto top = adapter.top();

  auto a = top;
  auto b = top;

  for (int i = N-1; 0 <= i; --i) {
    const int a_var = 2 * i + 1;
    a = adapter.ite(adapter.ithvar(a_var), bot, a);

    const int b_var = 2 * i;
    b = adapter.ite(adapter.ithvar(b_var), b, a);
  }

  return b;
}

// ========================================================================== //
// template <typename Adapter>
// typename Adapter::dd_t
// reverse_order(Adapter& adapter, typename Adapter::dd_t f)
// {
//   // TODO: generalise...
//   bddPair* mapping = bdd_newpair();
//
//   std::vector<int> mapping_old;
//   mapping_old.reserve(2*N);
//   std::vector<int> mapping_new;
//   mapping_new.reserve(2*N);
//
//   for (int i = 0; i < N; ++i) {
//     mapping_old.push_back(2*i);
//     mapping_new.push_back(2*N-(2*i)-1);
//
//     mapping_old.push_back(2*i+1);
//     mapping_new.push_back(2*N-(2*i+1)-1);
//   }
//
//   bdd_setpairs(mapping, mapping_old.data(), mapping_new.data(), 2*N);
//
//   return bdd_replace(f, mapping);
// }

// ========================================================================== //
template <typename Adapter>
int
run_quadratic(int argc, char** argv)
{
  bool should_exit = parse_input<parsing_policy>(argc, argv);
  if (should_exit) { return -1; }

  const int varcount = 2 * N;

  return run<Adapter>("quadratic-reorder", varcount, [&](Adapter& adapter) {
    const time_point f_before = now();
    typename Adapter::dd_t f = create_input(adapter);
    const time_point f_after = now();

    std::cout << json::field("f") << json::brace_open << json::endl;
    std::cout << json::field("size (nodes)") << json::value(bdd_nodecount(f)) << json::comma << json::endl;
    std::cout << json::field("time (ms)") << json::value(duration_ms(f_before, f_after)) << json::endl;
    std::cout << json::brace_close << json::comma << json::endl << json::flush;

    Permutation p = Permutation(varcount, 1, map_opt::REVERSE);

    const time_point g_before = now();
    f = adapter.replace_2(f, p);
    const time_point g_after = now();

    std::cout << json::field("bdd_replace(f)") << json::brace_open << json::endl;
    std::cout << json::field("size (nodes)") << json::value(bdd_nodecount(f)) << json::comma << json::endl;
    std::cout << json::field("time (ms)") << json::value(duration_ms(g_before, g_after)) << json::endl;
    std::cout << json::brace_close << json::comma << json::endl << json::flush;

    return 0;
  });
  return 1;
}
