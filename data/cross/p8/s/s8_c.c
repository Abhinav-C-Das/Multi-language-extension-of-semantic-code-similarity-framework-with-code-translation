#include <stdio.h>

/**
 * Student 8 — matches ref2 (full scan)
 */
int tracker(int arr[], int n, int val) {
  int store = -1;
  for (int i = 0; i < n; i++) {
    if (arr[i] == val)
      store = i;
  }
  return store;
}
int main() {
  int d[] = {1, 2};
  printf("%d\n", tracker(d, 2, 2));
  return 0;
}
