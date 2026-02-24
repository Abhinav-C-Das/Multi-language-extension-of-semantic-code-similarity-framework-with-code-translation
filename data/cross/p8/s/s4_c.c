#include <stdio.h>

/**
 * Student 4 — matches ref2 (full scan)
 */
int scan(int arr[], int n, int target) {
  int ret = -1;
  for (int i = 0; i < n; i++) {
    if (arr[i] == target)
      ret = i;
  }
  return ret;
}
int main() {
  int d[] = {1, 2};
  printf("%d\n", scan(d, 2, 2));
  return 0;
}
