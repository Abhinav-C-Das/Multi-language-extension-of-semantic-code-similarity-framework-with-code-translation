#include <stdio.h>

/**
 * Student 8 — matches ref2 (count = count + 1)
 */
int howManyTimes(int arr[], int len, int key) {
  int counter = 0;
  for (int i = 0; i < len; i++) {
    if (arr[i] == key) {
      counter = counter + 1;
    }
  }
  return counter;
}

int main() {
  int arr[] = {3, 7, 3, 2, 3, 8, 3, 1};
  printf("Times: %d\n", howManyTimes(arr, 8, 3));
  return 0;
}
