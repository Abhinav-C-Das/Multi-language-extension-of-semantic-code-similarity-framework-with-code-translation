#include <iostream>
using namespace std;

/**
 * Reference 1: Sum to N — Iterative Loop
 * CES: loop_ANY::ACCUMULATIVE::ADD
 */
long getSum(int n) {
  long total = 0;
  for (int i = 1; i <= n; i++) {
    total += i;
  }
  return total;
}

int main() {
  cout << "Sum 10: " << getSum(10) << endl;
  return 0;
}
