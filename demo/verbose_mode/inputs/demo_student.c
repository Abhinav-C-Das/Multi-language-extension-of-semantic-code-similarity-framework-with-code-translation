#include <stdio.h>

int get_array_sum(int vector[], int size) {
  int accumulator = 0;
  for (int iter = 0; iter < size; iter++) {
    accumulator += vector[iter];
  }
  return accumulator;
}

int main() {
  int test_array[] = {10, 20, 30, 40, 50};
  printf("Sum: %d\n", get_array_sum(test_array, 5));
  return 0;
}
