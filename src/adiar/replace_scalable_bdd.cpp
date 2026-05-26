#include "../replace.cpp"

#include "adapter.h"

int
main(int argc, char** argv)
{
  return run_replace<adiar_bdd_adapter>(argc, argv);
}
