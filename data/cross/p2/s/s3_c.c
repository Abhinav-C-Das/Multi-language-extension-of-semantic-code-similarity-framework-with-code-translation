#include <stdio.h>

/**
 * Student 3 — matches ref2 (count = count + 1)
 */
int tally(int arr[], int len, int target) {
  int hits = 0;
  for (int i = 0; i < len; i++) {
    if (arr[i] == target) {
      hits = hits + 1;
    }
  }
  return hits;
}

int main() {
  int arr[] = {3, 7, 3, 2, 3, 8, 3, 1};
  printf("Hits: %d\n", tally(arr, 8, 3));
  return 0;
}
