#include <stdio.h>

/**
 * Reference 2: Linear Search — Full Scan (Control Gated)
 * CES: loop_ANY::CONTROL_GATED::ASSIGN
 */
int searchFull(int arr[], int n, int t) {
  int res = -1;
  for (int i = 0; i < n; i++) {
    if (arr[i] == t) {
      res = i;
    }
  }
  return res;
}

int main() {
  int data[] = {1, 5, 2, 8, 3};
  printf("Idx: %d\n", searchFull(data, 5, 8));
  return 0;
}
