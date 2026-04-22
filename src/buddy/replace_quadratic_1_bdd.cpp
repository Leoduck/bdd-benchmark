#include "../quadratic_reorder_1_bdd.cpp"

#include "adapter.h"

int
main(int argc, char** argv)
{
  return run_quadratic<buddy_bdd_adapter>(argc, argv);
}
