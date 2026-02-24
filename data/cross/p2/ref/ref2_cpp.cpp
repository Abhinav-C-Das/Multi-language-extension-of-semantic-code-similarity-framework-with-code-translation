#include <iostream>
using namespace std;

/**
 * Reference Implementation 2: Count Occurrences
 * Strategy: Explicit assignment (= count + 1)
 * CES Pattern: loop_ANY::ACCUMULATIVE::ASSIGN
 */
int countOccurrences(int arr[], int n, int target) {
  int count = 0;
  for (int i = 0; i < n; i++) {
    if (arr[i] == target) {
      count = count + 1;
    }
  }
  return count;
}

int main() {
  int data[] = {3, 7, 3, 2, 3, 8, 3, 1};
  cout << "Count: " << countOccurrences(data, 8, 3) << endl;
  return 0;
}
