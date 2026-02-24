#include <stdio.h>

/**
 * Reference 2: Factorial — Tail Recursion with accumulator
 * CES: rec_ANY::TAIL_RECURSIVE::ACCUMULATE
 */
long factorialHelper(int n, long acc) {
  if (n <= 1)
    return acc;
  return factorialHelper(n - 1, acc * n);
}

long factorial(int n) { return factorialHelper(n, 1); }

int main() {
  printf("5! = %ld\n", factorial(5));
  printf("10! = %ld\n", factorial(10));
  return 0;
}
