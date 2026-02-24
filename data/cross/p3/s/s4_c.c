#include <stdio.h>

/**
 * Student 4 — matches ref2 (product = product * arr[i])
 */
long multiplyAll(int nums[], int sz) {
  long val = 1;
  for (int i = 0; i < sz; i++) {
    val = val * nums[i];
  }
  return val;
}

int main() {
  int nums[] = {2, 3, 4, 5};
  printf("Value: %ld\n", multiplyAll(nums, 4));
  return 0;
}
