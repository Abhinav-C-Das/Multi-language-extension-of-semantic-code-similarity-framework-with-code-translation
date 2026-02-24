#include <iostream>

void print_fibonacci(int n) {
  int t1 = 0, t2 = 1, nextTerm = 0;

  std::cout << "Fibonacci Series: " << t1 << ", " << t2 << ", ";

  nextTerm = t1 + t2;

  while (nextTerm <= n) {
    std::cout << nextTerm << ", ";
    t1 = t2;
    t2 = nextTerm;
    nextTerm = t1 + t2;
  }
  std::cout << std::endl;
}

int main() {
  int limit = 50;
  print_fibonacci(limit);
  return 0;
}
