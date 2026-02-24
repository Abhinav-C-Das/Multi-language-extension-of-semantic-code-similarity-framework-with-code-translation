#include <iostream>
using namespace std;

/**
 * Student 2 — matches ref2 (formula)
 */
long fastSum(int x) { return (long)x * (x + 1) / 2; }
int main() {
  cout << fastSum(5) << endl;
  return 0;
}
