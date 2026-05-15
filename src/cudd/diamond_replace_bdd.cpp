#include "../diamond_replace.cpp"

#include "adapter.h"

int
main(int argc, char** argv)
{
  return run_diamond<cudd_bdd_adapter>(argc, argv);
}
