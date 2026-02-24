#include <stdio.h>

/**
 * Reference 2: Balance Tracker — balance = balance - expenses[i]
 * CES: loop_ANY::ACCUMULATIVE::ASSIGN
 */
int trackBalance(int start, int expenses[], int n) {
  int balance = start;
  for (int i = 0; i < n; i++) {
    balance = balance - expenses[i];
  }
  return balance;
}

int main() {
  int costs[] = {50, 30, 20, 45, 15};
  printf("Remaining: %d\n", trackBalance(500, costs, 5));
  return 0;
}
