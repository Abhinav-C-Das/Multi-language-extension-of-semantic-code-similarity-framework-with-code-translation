#include <stdio.h>

/**
 * Student 4 — matches ref2 (sum = sum + a[i]*b[i])
 */
int vecMult(int a[], int b[], int n) {
  int dot = 0;
  for (int i = 0; i < n; i++) {
    dot = dot + a[i] * b[i];
  }
  return dot;
}

int main() {
  int a[] = {1, 3, 5};
  int b[] = {2, 4, 6};
  printf("VM: %d\n", vecMult(a, b, 3));
  return 0;
}
