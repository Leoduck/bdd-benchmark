#include "../quadratic_reorder_bdd.cpp"

#include "adapter.h"

int
main(int argc, char** argv)
{
  return run_quadratic<cudd_bdd_adapter>(argc, argv);
}
