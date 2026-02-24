#include <stdio.h>

/**
 * Student 8 — matches ref2 (recursive)
 */
int recursiveTop(int a[], int n) {
  if (n == 1)
    return a[0];
  int x = recursiveTop(a, n - 1);
  if (x > a[n - 1])
    return x;
  return a[n - 1];
}
int main() {
  int d[] = {1, 2};
  printf("%d\n", recursiveTop(d, 2));
  return 0;
}
