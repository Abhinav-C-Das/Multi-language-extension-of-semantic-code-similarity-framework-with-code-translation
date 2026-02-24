#include <iostream>
using namespace std;

/**
 * Student 9 — matches ref1 (count += 1)
 */
int getCount(int v[], int n, int target) {
  int found = 0;
  for (int i = 0; i < n; i++) {
    if (v[i] == target) {
      found += 1;
    }
  }
  return found;
}

int main() {
  int v[] = {3, 7, 3, 2, 3, 8, 3, 1};
  cout << "Count: " << getCount(v, 8, 3) << endl;
  return 0;
}
