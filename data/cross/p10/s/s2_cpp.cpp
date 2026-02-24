#include <iostream>
using namespace std;

/**
 * Student 2 — matches ref2 (selection)
 */
void sortArr(int arr[], int n) {
  int i, j, m;
  for (i = 0; i < n - 1; i++) {
    m = i;
    for (j = i + 1; j < n; j++)
      if (arr[j] < arr[m])
        m = j;
    int t = arr[m];
    arr[m] = arr[i];
    arr[i] = t;
  }
}
int main() {
  int d[] = {2, 1};
  sortArr(d, 2);
  return 0;
}
