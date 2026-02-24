#include <stdio.h>

/**
 * Reference 1: Find Max — Iterative
 * CES: loop_ANY::MAX_UPDATE::COMPARE
 */
int getMax(int arr[], int n) {
  int m = arr[0];
  for (int i = 1; i < n; i++) {
    if (arr[i] > m) {
      m = arr[i];
    }
  }
  return m;
}

int main() {
  int d[] = {1, 5, 2};
  printf("Max: %d\n", getMax(d, 3));
  return 0;
}
