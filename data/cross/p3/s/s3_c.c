#include <stdio.h>

/**
 * Student 3 — matches ref1 (product *= arr[i])
 */
long computeProduct(int arr[], int len) {
  long p = 1;
  for (int i = 0; i < len; i++) {
    p *= arr[i];
  }
  return p;
}

int main() {
  int arr[] = {2, 3, 4, 5};
  printf("Product: %ld\n", computeProduct(arr, 4));
  return 0;
}
