#include <iostream>
using namespace std;

/**
 * Reference 2: Selection Sort — Min Update
 * CES: loop_ANY::MIN_UPDATE::COMPARE
 */
void selection(int arr[], int n) {
  for (int i = 0; i < n - 1; i++) {
    int minIdx = i;
    for (int j = i + 1; j < n; j++) {
      if (arr[j] < arr[minIdx]) {
        minIdx = j;
      }
    }
    int temp = arr[minIdx];
    arr[minIdx] = arr[i];
    arr[i] = temp;
  }
}

int main() {
  int d[] = {5, 2, 9, 1, 5};
  selection(d, 5);
  return 0;
}
