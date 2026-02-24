#include <stdio.h>

/**
 * Reference 1: Factorial — Head Recursion
 * CES: rec_ANY::HEAD_RECURSIVE::ADD
 */
long factorial(int n) {
  if (n <= 1)
    return 1;
  return n * factorial(n - 1);
}

int main() {
  printf("5! = %ld\n", factorial(5));
  printf("10! = %ld\n", factorial(10));
  return 0;
}
