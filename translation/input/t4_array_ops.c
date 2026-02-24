#include <stdio.h>

void reverse_array(int arr[], int size) {
  int start = 0;
  int end = size - 1;
  int temp = 0;

  while (start < end) {
    temp = arr[start];
    arr[start] = arr[end];
    arr[end] = temp;

    start++;
    end--;
  }
}

void print_array(int arr[], int size) {
  for (int i = 0; i < size; i++) {
    printf("%d ", arr[i]);
  }
  printf("\n");
}

int main() {
  int data[] = {10, 20, 30, 40, 50, 60, 70};
  printf("Original: ");
  print_array(data, 7);

  reverse_array(data, 7);

  printf("Reversed: ");
  print_array(data, 7);
  return 0;
}
