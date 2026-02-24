#include <stdio.h>

/**
 * Reference 2: Find Max — Recursive
 * CES: rec_ANY::SIMPLE_RECURSIVE::CALL
 */
int recMax(int arr[], int n) {
  if (n == 1)
    return arr[0];
  int sm = recMax(arr, n - 1);
  if (arr[n - 1] > sm)
    return arr[n - 1];
  return sm;
}

int main() {
  int d[] = {1, 5, 2};
  printf("Max: %d\n", recMax(d, 3));
  return 0;
}
