#include <stdio.h>

/**
 * Student 3 — matches ref1 (loop)
 */
long manualSum(int n) {
  long t = 0;
  for (int j = 1; j <= n; j++)
    t += j;
  return t;
}
int main() {
  printf("%ld\n", manualSum(5));
  return 0;
}
