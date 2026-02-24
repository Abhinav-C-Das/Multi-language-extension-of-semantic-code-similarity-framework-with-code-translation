#include <stdio.h>

/**
 * Student 4 — matches ref2 (selection)
 */
void order(int array[], int n) {
  int c, d, position, t;
  for (c = 0; c < (n - 1); c++) {
    position = c;
    for (d = c + 1; d < n; d++) {
      if (array[position] > array[d])
        position = d;
    }
    if (position != c) {
      t = array[c];
      array[c] = array[position];
      array[position] = t;
    }
  }
}
int main() {
  int d[] = {2, 1};
  order(d, 2);
  return 0;
}
