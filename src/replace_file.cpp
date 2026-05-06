// Assertions
#include <cassert>

// Data Structures
#include <iostream>
#include <string>
#include <vector>

// Other
#include <stdexcept>

#include "common/adapter.h"
#include "common/chrono.h"
#include "common/input.h"
#include "common/libbdd_parser.h"
#include "queensbuilder.cpp"

////////////////////////////////////////////////////////////////////////////////////////////////////
//                                        INPUT PARSING                                           //
////////////////////////////////////////////////////////////////////////////////////////////////////

std::vector<std::string> inputs_path;


class parsing_policy
{
public:
  static constexpr std::string_view name = "Replace";
  static constexpr std::string_view args = "f:";

  static constexpr std::string_view help_text =
    "        -f PATH               Path to '._dd' files \n";

  static inline bool
  parse_input(const int c, const char* arg)
  {
    switch (c) {
    case 'f': {
      if (!std::filesystem::exists(arg)) {
        std::cerr << "File '" << arg << "' does not exist\n";
        return true;
      }
      inputs_path.push_back(arg);
      return false;
    }
    default: return true;
    }
  }
};

template <typename Adapter>
int run_replace(int argc, char** argv) {
  const bool should_exit = parse_input<parsing_policy>(argc, argv);
  if (should_exit) { return -1; }

  lib_bdd::bdd f = lib_bdd::deserialize(inputs_path.at(0));
  lib_bdd::var_map vm = lib_bdd::remap_vars({f});

  // =============================================================================================
  // Initialize BDD package
  return run<Adapter>("replace", vm.size(), [&](Adapter& adapter) {
    std::cout << json::field("inputs") << json::array_open << json::endl;

    std::cout << json::indent << json::brace_open << json::endl;
    const lib_bdd::stats_t stats = lib_bdd::stats(f);

    std::cout << json::field("path") << json::value(inputs_path.at(0)) << json::comma
    << json::endl;
    lib_bdd::print_json(stats, std::cout);
    std::cout << json::comma << json::endl;

    std::cout << json::brace_close;
    std::cout << json::comma;
    std::cout << json::endl;
    std::cout << json::array_close << json::comma << json::endl << json::endl;

    // =============================================================================================
    // Reconstruct DDs
    typename Adapter::dd_t inputs_dd;

    size_t total_time = 0;

    std::cout << json::field("rebuild") << json::array_open << json::endl << json::flush;


    const time_point t_rebuild_before = now();
    inputs_dd = reconstruct(adapter, std::move(f), vm);
    const time_point t_rebuild_after = now();

    const size_t load_time = duration_ms(t_rebuild_before, t_rebuild_after);
    total_time += load_time;

    std::cout << json::indent << json::brace_open << json::endl;
    std::cout << json::field("path") << json::value(inputs_path.at(0)) << json::comma
	    << json::endl;
    std::cout << json::field("size (nodes)") << json::value(adapter.nodecount(inputs_dd))
	    << json::comma << json::endl;
    std::cout << json::field("satcount") << json::value(adapter.satcount(inputs_dd))
	    << json::comma << json::endl;
    std::cout << json::field("time (ms)")
	    << json::value(duration_ms(t_rebuild_before, t_rebuild_after)) << json::endl;

    std::cout << json::brace_close;
    std::cout << json::comma;
    std::cout << json::endl;

    // Free up memory
    f.clear();
    f.shrink_to_fit();

    std::cout << json::array_close << json::comma << json::endl;

    // =============================================================================================
    // Replaces DDs together
    typename Adapter::dd_t result = inputs_dd;

    std::cout << json::field("replace") << json::brace_open << json::endl << json::flush;


    adapter.print_dot(result, "beforeTESTTESTTEST.dot");

    const time_point t_apply_before = now();
    result = adapter.replace(inputs_dd, [&](int x){if (x == 1) {return 0;} if (x== 0) {return 1;} else {return x;}});

    adapter.print_dot(result, "TESTTESTTEST.dot");
    const time_point t_apply_after = now();

    const size_t apply_time = duration_ms(t_apply_before, t_apply_after);
    total_time += apply_time;

    std::cout << json::field("size (nodes)") << adapter.nodecount(result) << json::comma
              << json::endl;
    std::cout << json::field("satcount") << adapter.satcount(result) << json::comma << json::endl;
    std::cout << json::field("time (ms)") << apply_time << json::endl;

    std::cout << json::brace_close << json::comma << json::endl;

    // =============================================================================================

    std::cout << json::field("total time (ms)") << json::value(init_time + total_time)
              << json::endl;

    return 0;
  });

  return 1;
}
