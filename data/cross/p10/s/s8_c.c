#include <stdio.h>

/**
 * Student 8 — matches ref2 (selection)
 */
void sel(int arr[], int n) {
  int i, j, min_idx;
  for (i = 0; i < n - 1; i++) {
    min_idx = i;
    for (j = i + 1; j < n; j++)
      if (arr[j] < arr[min_idx])
        min_idx = j;
    int tmp = arr[min_idx];
    arr[min_idx] = arr[i];
    arr[i] = tmp;
  }
}
int main() {
  int d[] = {2, 1};
  sel(d, 2);
  return 0;
}
