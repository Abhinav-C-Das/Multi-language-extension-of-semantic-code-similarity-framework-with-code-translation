#include <stdio.h>

/**
 * Student 4 — matches ref2 (recursive)
 */
int rmax(int arr[], int len) {
  if (len == 1)
    return arr[0];
  int prev = rmax(arr, len - 1);
  if (arr[len - 1] > prev)
    return arr[len - 1];
  return prev;
}
int main() {
  int d[] = {1, 2};
  printf("%d\n", rmax(d, 2));
  return 0;
}
