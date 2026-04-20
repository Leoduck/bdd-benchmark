
// Assertions
#include <cassert>

// Data Structures
#include <string>

// Types
#include <cstdlib>


int N = 8;

// ========================================================================== //
inline int
rows()
{
  return N;
}

inline int
MAX_ROW()
{
  return rows() - 1;
}

inline int
cols()
{
  return N;
}

inline int
MAX_COL()
{
  return cols() - 1;
}

// =============================================================================
inline int
label_of_position(int r, int c)
{
  assert(r >= 0 && c >= 0);
  return (rows() * r) + c;
}

inline std::string
row_to_string(int r)
{
  return std::to_string(r + 1);
}

inline std::string
col_to_string(int c)
{
  return std::string(1, (char)('A' + c));
}

inline std::string
pos_to_string(int r, int c)
{
  return row_to_string(r) + col_to_string(c);
}

// ========================================================================== //
//                            SQUARE CONSTRUCTION                             //
template <typename Adapter>
typename Adapter::dd_t
queens_S(Adapter& adapter, int i, int j)
{
  auto next = adapter.build_node(true);

  for (int row = MAX_ROW(); row >= 0; row--) {
    for (int col = MAX_COL(); col >= 0; col--) {
      const int label = label_of_position(row, col);

      // Queen must be placed here
      if (row == i && col == j) {
        auto low  = adapter.build_node(false);
        auto high = next;
        next      = adapter.build_node(label, low, high);

        continue;
      }

      // Conflicting row, column and diagonal with Queen placement
      const int row_diff = std::abs(row - i);
      const int col_diff = std::abs(col - j);

      if ((i == row && j != col) || (i != row && j == col) || (col_diff == row_diff)) {
        auto low  = next;
        auto high = adapter.build_node(false);
        next      = adapter.build_node(label, low, high);

        continue;
      }

      // No in conflicts
      next = adapter.build_node(label, next, next);
    }
  }

  typename Adapter::dd_t out = adapter.build();
#ifdef BDD_BENCHMARK_STATS
  total_nodes += adapter.nodecount(out);
#endif // BDD_BENCHMARK_STATS
  return out;
}

// ========================================================================== //
//                              ROW CONSTRUCTION                              //
template <typename Adapter>
typename Adapter::dd_t
queens_R(Adapter& adapter, int r)
{
  typename Adapter::dd_t out = queens_S(adapter, r, 0);

#ifdef BDD_BENCHMARK_STATS
  std::cout << json::field("R(" + pos_to_string(r, 0) + ")") << json::value(adapter.nodecount(out))
            << json::comma << json::endl;
#endif // BDD_BENCHMARK_STATS

  for (int c = 1; c < cols(); c++) {
    out |= queens_S(adapter, r, c);

#ifdef BDD_BENCHMARK_STATS
    const size_t nodecount = adapter.nodecount(out);
    largest_bdd            = std::max(largest_bdd, nodecount);
    total_nodes += nodecount;

    std::cout << json::field("R(" + pos_to_string(r, c) + ")") << json::value(nodecount)
              << json::comma << json::endl
              << json::flush;
#endif // BDD_BENCHMARK_STATS
  }
  return out;
}

// ========================================================================== //
//                              ROW ACCUMULATION                              //
template <typename Adapter>
typename Adapter::dd_t
queens_B(Adapter& adapter)
{
  if (rows() == 1 && cols() == 1) { return queens_S(adapter, 0, 0); }

  typename Adapter::dd_t out = queens_R(adapter, 0);
  {
#ifdef BDD_BENCHMARK_STATS
    const size_t nodecount = adapter.nodecount(out);
    largest_bdd            = std::max(largest_bdd, nodecount);
    total_nodes += nodecount;

    std::cout << json::field("B(" + row_to_string(0) + ")") << json::value(nodecount) << json::comma
              << json::endl
              << json::endl;
#endif // BDD_BENCHMARK_STATS
  }

  for (int r = 1; r < rows(); r++) {
    out &= queens_R(adapter, r);

#ifdef BDD_BENCHMARK_STATS
    const size_t nodecount = adapter.nodecount(out);
    largest_bdd            = std::max(largest_bdd, nodecount);
    total_nodes += nodecount;

    std::cout << json::field("B(" + row_to_string(r) + ")") << json::value(nodecount);
    if (r != MAX_ROW()) { std::cout << json::comma << json::endl; }
    std::cout << json::endl << json::flush;
#endif // BDD_BENCHMARK_STATS
  }
  return out;
}

////////////////////////////////////////////////////////////////////////////////
/// \brief   Number of solutions for the Queens Problem
///
/// \details Number taken from https://en.wikipedia.org/wiki/Eight_queens_puzzle
////////////////////////////////////////////////////////////////////////////////
const size_t expected[28] = {
  0,                 //  0x0
  1,                 //  1x1
  0,                 //  2x2
  0,                 //  3x3
  2,                 //  4x4
  10,                //  5x5
  4,                 //  6x6
  40,                //  7x7
  92,                //  8x8
  352,               //  9x9
  724,               // 10x10
  2680,              // 11x11
  14200,             // 12x12
  73712,             // 13x13
  365596,            // 14x14
  2279184,           // 15x15
  14772512,          // 16x16
  95815104,          // 17x17
  666090624,         // 18x18
  4968057848,        // 19x19
  39029188884,       // 20x20
  314666222712,      // 21x21
  2691008701644,     // 22x22
  24233937684440,    // 23x23
  227514171973736,   // 24x24
  2207893435808352,  // 25x25
  22317699616364044, // 26x26
  234907967154122528 // 27x27
};

