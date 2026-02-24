#include <iostream>
using namespace std;

/**
 * Student 9 — matches ref1 (loop)
 */
long loopSum(int n) {
  long ans = 0;
  for (int i = 1; i <= n; i++)
    ans += i;
  return ans;
}
int main() {
  cout << loopSum(5) << endl;
  return 0;
}
