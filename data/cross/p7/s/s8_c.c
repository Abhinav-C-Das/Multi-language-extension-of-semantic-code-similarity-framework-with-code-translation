#include <stdio.h>

/**
 * Student 8 — matches ref2 (formula)
 */
long quickSum(int n) { return (long)n * (n + 1) / 2; }
int main() {
  printf("%ld\n", quickSum(5));
  return 0;
}
