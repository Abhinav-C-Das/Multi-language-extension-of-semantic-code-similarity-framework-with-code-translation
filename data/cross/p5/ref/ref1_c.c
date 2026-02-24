#include <stdio.h>

/**
 * Reference 1: Balance Tracker — balance -= expenses[i]
 * CES: loop_ANY::ACCUMULATIVE::SUB
 */
int trackBalance(int start, int expenses[], int n) {
  int balance = start;
  for (int i = 0; i < n; i++) {
    balance -= expenses[i];
  }
  return balance;
}

int main() {
  int costs[] = {50, 30, 20, 45, 15};
  printf("Remaining: %d\n", trackBalance(500, costs, 5));
  return 0;
}
