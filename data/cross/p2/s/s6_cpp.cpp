#include <iostream>
using namespace std;

/**
 * Student 6 — matches ref2 (count = count + 1)
 */
int countTargets(int arr[], int n, int t) {
  int result = 0;
  for (int i = 0; i < n; i++) {
    if (arr[i] == t) {
      result = result + 1;
    }
  }
  return result;
}

int main() {
  int arr[] = {3, 7, 3, 2, 3, 8, 3, 1};
  cout << "Targets: " << countTargets(arr, 8, 3) << endl;
  return 0;
}
