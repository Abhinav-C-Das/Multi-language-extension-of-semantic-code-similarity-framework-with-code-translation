#include <stdio.h>

/**
 * Student 8 — matches ref1 (sum += a[i]*b[i])
 */
int dotCalc(int a[], int b[], int len) {
  int d = 0;
  for (int i = 0; i < len; i++) {
    d += a[i] * b[i];
  }
  return d;
}

int main() {
  int a[] = {1, 3, 5};
  int b[] = {2, 4, 6};
  printf("DC: %d\n", dotCalc(a, b, 3));
  return 0;
}
