#include <stdio.h>

/**
 * Student 3 — matches ref1 (sum += a[i]*b[i])
 */
int scalarProduct(int x[], int y[], int len) {
  int total = 0;
  for (int i = 0; i < len; i++) {
    total += x[i] * y[i];
  }
  return total;
}

int main() {
  int x[] = {1, 3, 5};
  int y[] = {2, 4, 6};
  printf("SP: %d\n", scalarProduct(x, y, 3));
  return 0;
}
