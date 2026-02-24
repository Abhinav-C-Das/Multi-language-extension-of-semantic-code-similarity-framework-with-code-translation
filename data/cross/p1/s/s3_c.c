#include <stdio.h>

/**
 * Student Submission 3
 * Should match: ref2 (while loop with explicit addition)
 */
int getSum(int data[], int size) {
  int total = 0;
  int pos = 0;
  while (pos < size) {
    total = total + data[pos];
    pos++;
  }
  return total;
}

int main() {
  int values[] = {10, 20, 30, 40, 50};
  printf("Sum = %d\n", getSum(values, 5));
  return 0;
}
