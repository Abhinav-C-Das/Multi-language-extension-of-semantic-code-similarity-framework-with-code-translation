#include <stdio.h>

/**
 * Student Submission 4
 * Should match: ref1 (indexed for loop with compound assignment)
 */
int arrayTotal(int a[], int length) {
  int sum = 0;
  for (int i = 0; i < length; i++) {
    sum += a[i];
  }
  return sum;
}

int main() {
  int myArr[] = {10, 20, 30, 40, 50};
  printf("Answer: %d\n", arrayTotal(myArr, 5));
  return 0;
}
