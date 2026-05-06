#include "../exists_reorder.cpp"

#include "adapter.h"

int
main(int argc, char** argv)
{
  return run_quadratic<adiar_bdd_adapter>(argc, argv);
}
