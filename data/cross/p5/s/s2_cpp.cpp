#include <iostream>
using namespace std;

/**
 * Student 2 — matches ref2 (balance = balance - expenses[i])
 */
int calcRemaining(int init, int costs[], int n) {
  int rem = init;
  for (int i = 0; i < n; i++) {
    rem = rem - costs[i];
  }
  return rem;
}

int main() {
  int costs[] = {50, 30, 20, 45, 15};
  cout << "Rem: " << calcRemaining(500, costs, 5) << endl;
  return 0;
}
