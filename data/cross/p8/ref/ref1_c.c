#include <stdio.h>

/**
 * Reference 1: Linear Search — Early Exit
 * CES: loop_ANY::SEARCH_WITH_RETURN::EARLY_EXIT
 */
int findVal(int arr[], int n, int target) {
  for (int i = 0; i < n; i++) {
    if (arr[i] == target) {
      return i;
    }
  }
  return -1;
}

int main() {
  int data[] = {1, 5, 2, 8, 3};
  printf("Idx: %d\n", findVal(data, 5, 8));
  return 0;
}
