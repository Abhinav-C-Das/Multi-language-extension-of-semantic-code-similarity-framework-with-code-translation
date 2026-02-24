#include <iostream>
using namespace std;

/**
 * Student 9 — matches ref1 (bubble)
 */
void bbl(int a[], int n) {
  for (int i = 0; i < n - 1; i++) {
    for (int j = 0; j < n - i - 1; j++) {
      if (a[j] > a[j + 1]) {
        int swap = a[j];
        a[j] = a[j + 1];
        a[j + 1] = swap;
      }
    }
  }
}
int main() {
  int d[] = {2, 1};
  bbl(d, 2);
  return 0;
}
