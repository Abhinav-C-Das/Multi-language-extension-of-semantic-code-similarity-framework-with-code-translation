#include <iostream>
using namespace std;

/**
 * Student 6 — matches ref1 (loop)
 */
long addUp(int max) {
  long val = 0;
  for (int i = 1; i <= max; i++)
    val += i;
  return val;
}
int main() {
  cout << addUp(5) << endl;
  return 0;
}
