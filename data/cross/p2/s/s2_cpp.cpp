#include <iostream>
using namespace std;

/**
 * Student 2 — matches ref1 (count += 1)
 */
int frequency(int data[], int sz, int key) {
  int cnt = 0;
  for (int i = 0; i < sz; i++) {
    if (data[i] == key) {
      cnt += 1;
    }
  }
  return cnt;
}

int main() {
  int data[] = {3, 7, 3, 2, 3, 8, 3, 1};
  cout << "Freq: " << frequency(data, 8, 3) << endl;
  return 0;
}
