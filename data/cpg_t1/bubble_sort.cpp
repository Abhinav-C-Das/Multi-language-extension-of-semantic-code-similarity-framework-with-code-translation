#include <iostream>

void bubble_sort(int arr[], int n) {
  for (int i = 0; i < n - 1; i++) {
    for (int j = 0; j < n - i - 1; j++) {
      if (arr[j] > arr[j + 1]) {
        int temp = arr[j];
        arr[j] = arr[j + 1];
        arr[j + 1] = temp;
      }
    }
  }
}

int main() {
  int data[] = {64, 34, 25, 12, 22, 11, 90};
  int size = 7;
  bubble_sort(data, size);

  std::cout << "Sorted array: ";
  for (int i = 0; i < size; i++) {
    std::cout << data[i] << " ";
  }
  std::cout << std::endl;
  return 0;
}
