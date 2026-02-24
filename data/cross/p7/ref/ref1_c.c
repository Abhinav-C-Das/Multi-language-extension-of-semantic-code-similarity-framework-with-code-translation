#include <stdio.h>

/**
 * Reference 1: Sum to N — Iterative Loop
 * CES: loop_ANY::ACCUMULATIVE::ADD
 */
long calcSum(int n) {
  long s = 0;
  for (int i = 1; i <= n; i++) {
    s += i;
  }
  return s;
}

int main() {
  printf("Sum 10: %ld\n", calcSum(10));
  return 0;
}
