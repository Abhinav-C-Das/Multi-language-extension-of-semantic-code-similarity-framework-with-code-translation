#include <stdio.h>

/**
 * Student Submission 8
 * Should match: ref2 (while loop with explicit addition)
 */
int sumUp(int items[], int count) {
  int result = 0;
  int j = 0;
  while (j < count) {
    result = result + items[j];
    j++;
  }
  return result;
}

int main() {
  int nums[] = {10, 20, 30, 40, 50};
  printf("Total: %d\n", sumUp(nums, 5));
  return 0;
}
