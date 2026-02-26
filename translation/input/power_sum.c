#include <stdio.h>

int power(int base, int exp) {
  int result = 1;
  for (int i = 0; i < exp; i++) {
    result = result * base;
  }
  return result;
}

int sum_of_powers(int arr[], int n, int exp) {
  int total = 0;
  for (int i = 0; i < n; i++) {
    total += power(arr[i], exp);
  }
  return total;
}

int main() {
  int data[] = {2, 3, 4};
  int result = sum_of_powers(data, 3, 2);
  printf("Sum of squares: %d\n", result);

  result = sum_of_powers(data, 3, 3);
  printf("Sum of cubes: %d\n", result);
  return 0;
}
