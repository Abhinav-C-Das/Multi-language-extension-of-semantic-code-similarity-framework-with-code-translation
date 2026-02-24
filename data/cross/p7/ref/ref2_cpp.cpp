#include <iostream>
using namespace std;

/**
 * Reference 2: Sum to N — Direct Formula
 * CES: direct::DIRECT_FORMULA::COMPUTE
 */
long formulaSum(int n) { return (long)n * (n + 1) / 2; }

int main() {
  cout << "Sum 10: " << formulaSum(10) << endl;
  return 0;
}
