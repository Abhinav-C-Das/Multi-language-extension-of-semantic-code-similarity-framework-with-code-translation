#include <iostream>
using namespace std;

/**
 * Student 6 — matches ref1 (bubble)
 */
void mySort(int a[], int s) {
  for (int i = 0; i < s; i++) {
    for (int j = i + 1; j < s; j++) {
      if (a[i] > a[j]) {
        int temp = a[i];
        a[i] = a[j];
        a[j] = temp;
      }
    }
  }
}
int main() {
  int d[] = {2, 1};
  mySort(d, 2);
  return 0;
}
