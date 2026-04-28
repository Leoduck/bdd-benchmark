#include "../picotrav_replace.cpp"

#include "adapter.h"

int
main(int argc, char** argv)
{
  return run_picotrav<adiar_bdd_adapter>(argc, argv);
}
