#include <iostream>
using namespace std;

/**
 * Student 6 — matches ref1 (balance -= expenses[i])
 */
int subtractCosts(int budget, int exp[], int n) {
  int b = budget;
  for (int i = 0; i < n; i++) {
    b -= exp[i];
  }
  return b;
}

int main() {
  int exp[] = {50, 30, 20, 45, 15};
  cout << "Budget: " << subtractCosts(500, exp, 5) << endl;
  return 0;
}
