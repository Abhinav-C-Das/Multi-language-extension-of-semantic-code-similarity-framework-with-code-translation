#include <iostream>
using namespace std;

/**
 * Reference 1: Dot Product — sum += a[i] * b[i]
 * CES: loop_ANY::ACCUMULATIVE::ADD
 */
int dotProduct(int a[], int b[], int n) {
  int sum = 0;
  for (int i = 0; i < n; i++) {
    sum += a[i] * b[i];
  }
  return sum;
}

int main() {
  int x[] = {1, 3, 5};
  int y[] = {2, 4, 6};
  cout << "Dot: " << dotProduct(x, y, 3) << endl;
  return 0;
}
