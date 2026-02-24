#include <stdio.h>

/**
 * Student 8 — matches ref2 (tail recursion)
 */
long tailFact(int n, long result) {
  if (n <= 1)
    return result;
  return tailFact(n - 1, result * n);
}

long doFactorial(int n) { return tailFact(n, 1); }

int main() {
  printf("Fact 7: %ld\n", doFactorial(7));
  return 0;
}
