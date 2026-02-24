#include <iostream>
using namespace std;

/**
 * Reference 2: Linear Search — Full Scan (Control Gated)
 * CES: loop_ANY::CONTROL_GATED::ASSIGN
 */
int getIndex(int arr[], int n, int key) {
  int foundIdx = -1;
  for (int i = 0; i < n; i++) {
    if (arr[i] == key) {
      foundIdx = i;
    }
  }
  return foundIdx;
}

int main() {
  int data[] = {1, 5, 2, 8, 3};
  cout << "Idx: " << getIndex(data, 5, 8) << endl;
  return 0;
}
