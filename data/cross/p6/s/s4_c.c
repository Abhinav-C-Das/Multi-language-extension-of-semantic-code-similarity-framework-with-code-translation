#include <stdio.h>

/**
 * Student 4 — matches ref2 (tail recursion)
 */
long factTail(int n, long acc) {
  if (n <= 1)
    return acc;
  return factTail(n - 1, acc * n);
}

long factWrapper(int n) { return factTail(n, 1); }

int main() {
  printf("Fact 9: %ld\n", factWrapper(9));
  return 0;
}
