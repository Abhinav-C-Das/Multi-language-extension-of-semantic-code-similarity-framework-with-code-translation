#include <stdio.h>

/**
 * Student 3 — matches ref1 (bubble)
 */
void doSort(int arr[], int n) {
  for (int c = 0; c < n - 1; c++) {
    for (int d = 0; d < n - c - 1; d++) {
      if (arr[d] > arr[d + 1]) {
        int swap = arr[d];
        arr[d] = arr[d + 1];
        arr[d + 1] = swap;
      }
    }
  }
}
int main() {
  int d[] = {2, 1};
  doSort(d, 2);
  return 0;
}
