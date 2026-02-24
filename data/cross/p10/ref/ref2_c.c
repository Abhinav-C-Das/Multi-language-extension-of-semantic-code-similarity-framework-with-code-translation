#include <stdio.h>

/**
 * Reference 2: Selection Sort — Min Update
 * CES: loop_ANY::MIN_UPDATE::COMPARE
 */
void sSort(int arr[], int n) {
  for (int i = 0; i < n - 1; i++) {
    int minIdx = i;
    for (int j = i + 1; j < n; j++) {
      if (arr[j] < arr[minIdx]) {
        minIdx = j;
      }
    }
    int temp = arr[minIdx];
    arr[minIdx] = arr[i];
    arr[i] = temp;
  }
}

int main() {
  int d[] = {5, 2, 9, 1, 5};
  sSort(d, 5);
  return 0;
}
