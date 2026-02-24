#include <stdio.h>

int sumArray(int arr[], int n) {
  int total = 0;
  for (int i = 0; i < n; i++) {
    total += arr[i];
  }
  return total;
}

int main() {
  int data[] = {10, 20, 30, 40, 50};
  printf("Sum: %d\n", sumArray(data, 5));
  return 0;
}
