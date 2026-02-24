#include <stdio.h>

/**
 * Reference 2: Sum to N — Direct Formula
 * CES: direct::DIRECT_FORMULA::COMPUTE
 */
long gaussSum(int n) { return (long)n * (n + 1) / 2; }

int main() {
  printf("Sum 10: %ld\n", gaussSum(10));
  return 0;
}
