#include <stdio.h>

int sum_array(int arr[], int size) {
  int total = 0;
  for (int i = 0; i < size; i++) {
    total += arr[i];
  }
  return total;
}

int main() {
  int numbers[] = {10, 20, 30, 40, 50};
  int size = 5;
  int result = sum_array(numbers, size);
  printf("Sum of array elements: %d\n", result);
  return 0;
}
