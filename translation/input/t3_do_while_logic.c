#include <stdio.h>

void filter_numbers(int limit) {
  int current = 0;

  do {
    current++;

    if (current > limit) {
      break;
    }

    if (current % 2 == 0) {
      continue;
    }

    if (!(current < 5) && (current < 15)) {
      printf("Eligible Odd: %d\n", current);
    }

  } while (current < 20);
}

int main() {
  filter_numbers(18);
  return 0;
}
