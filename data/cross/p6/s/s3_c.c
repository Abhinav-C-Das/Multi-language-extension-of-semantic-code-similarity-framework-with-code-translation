#include <stdio.h>

/**
 * Student 3 — matches ref1 (head recursion)
 */
long calcFactorial(int n) {
  if (n <= 1)
    return 1;
  return n * calcFactorial(n - 1);
}

int main() {
  printf("Fact 8: %ld\n", calcFactorial(8));
  return 0;
}
