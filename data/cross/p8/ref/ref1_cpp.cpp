#include <iostream>
using namespace std;

/**
 * Reference 1: Linear Search — Early Exit
 * CES: loop_ANY::SEARCH_WITH_RETURN::EARLY_EXIT
 */
int searchArr(int arr[], int n, int val) {
  for (int i = 0; i < n; i++) {
    if (arr[i] == val) {
      return i;
    }
  }
  return -1;
}

int main() {
  int data[] = {1, 5, 2, 8, 3};
  cout << "Idx: " << searchArr(data, 5, 8) << endl;
  return 0;
}
