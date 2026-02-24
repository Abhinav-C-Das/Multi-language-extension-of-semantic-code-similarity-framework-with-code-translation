#include <stdio.h>

/**
 * Student 4 — matches ref2 (formula)
 */
long directSum(int limit) { return (long)limit * (limit + 1) / 2; }
int main() {
  printf("%ld\n", directSum(5));
  return 0;
}
