#include <stdio.h>

/**
 * Reference 1: Bubble Sort — Conditional Swap
 * CES: loop_ANY::CONDITIONAL_SWAP::ASSIGN
 */
void bSort(int arr[], int n) {
  for (int i = 0; i < n - 1; i++) {
    for (int j = 0; j < n - i - 1; j++) {
      if (arr[j] > arr[j + 1]) {
        int temp = arr[j];
        arr[j] = arr[j + 1];
        arr[j + 1] = temp;
      }
    }
  }
}

int main() {
  int d[] = {5, 2, 9, 1, 5};
  bSort(d, 5);
  return 0;
}
