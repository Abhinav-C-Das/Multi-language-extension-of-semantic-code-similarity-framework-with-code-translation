#include <stdio.h>

/**
 * Student 3 — matches ref1 (iterative)
 */
int findLarge(int arr[], int n) {
  int big = arr[0];
  for (int k = 1; k < n; k++) {
    if (arr[k] > big)
      big = arr[k];
  }
  return big;
}
int main() {
  int d[] = {1, 2};
  printf("%d\n", findLarge(d, 2));
  return 0;
}
