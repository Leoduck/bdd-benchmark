#include "../memo_replace.cpp"

#include "adapter.h"

int
main(int argc, char** argv)
{
  return run_memotest<buddy_bdd_adapter>(argc, argv);
}
