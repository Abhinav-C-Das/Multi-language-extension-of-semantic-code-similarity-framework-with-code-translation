#include <stdio.h>

/**
 * Reference Implementation 2: Array Sum
 * Strategy: While loop with explicit addition (s = s + num)
 * Pattern: Counter-controlled while loop
 */
int calSum(int numbers[], int n) {
  int s = 0;
  int idx = 0;
  while (idx < n) {
    s = s + numbers[idx];
    idx++;
  }
  return s;
}

int main() {
  int data[] = {10, 20, 30, 40, 50};
  int result = calSum(data, 5);
  printf("Sum: %d\n", result);
  return 0;
}
