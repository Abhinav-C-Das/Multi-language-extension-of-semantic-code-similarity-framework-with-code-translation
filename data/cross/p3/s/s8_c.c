#include <stdio.h>

/**
 * Student 8 — matches ref2 (product = product * arr[i])
 */
long productArray(int arr[], int len) {
  long r = 1;
  for (int i = 0; i < len; i++) {
    r = r * arr[i];
  }
  return r;
}

int main() {
  int arr[] = {2, 3, 4, 5};
  printf("Result: %ld\n", productArray(arr, 4));
  return 0;
}
