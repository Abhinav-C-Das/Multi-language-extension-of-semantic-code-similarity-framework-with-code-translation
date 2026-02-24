#include <stdio.h>

/**
 * Student 4 — matches ref1 (count += 1)
 */
int countMatches(int nums[], int sz, int val) {
  int c = 0;
  for (int i = 0; i < sz; i++) {
    if (nums[i] == val) {
      c += 1;
    }
  }
  return c;
}

int main() {
  int nums[] = {3, 7, 3, 2, 3, 8, 3, 1};
  printf("Matches: %d\n", countMatches(nums, 8, 3));
  return 0;
}
