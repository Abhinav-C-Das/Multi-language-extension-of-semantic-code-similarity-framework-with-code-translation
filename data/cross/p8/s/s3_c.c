#include <stdio.h>

/**
 * Student 3 — matches ref1 (early exit)
 */
int locate(int arr[], int n, int x) {
  for (int i = 0; i < n; i++) {
    if (arr[i] == x)
      return i;
  }
  return -1;
}
int main() {
  int d[] = {1, 2};
  printf("%d\n", locate(d, 2, 2));
  return 0;
}
