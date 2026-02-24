#include <stdio.h>

/**
 * Reference Implementation 1: Array Product
 * Strategy: Compound multiplication (*=)
 * CES Pattern: loop_ANY::ACCUMULATIVE::MUL
 */
long arrayProduct(int arr[], int n) {
  long product = 1;
  for (int i = 0; i < n; i++) {
    product *= arr[i];
  }
  return product;
}

int main() {
  int data[] = {2, 3, 4, 5};
  printf("Product: %ld\n", arrayProduct(data, 4));
  return 0;
}
