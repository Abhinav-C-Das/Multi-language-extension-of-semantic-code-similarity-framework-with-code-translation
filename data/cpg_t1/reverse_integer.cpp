#include <iostream>

int reverse_integer(int n) {
  int reversed = 0, remainder;
  while (n != 0) {
    remainder = n % 10;
    reversed = reversed * 10 + remainder;
    n /= 10;
  }
  return reversed;
}

int main() {
  int num = 12345;
  int rev = reverse_integer(num);
  std::cout << "Original: " << num << "\nReversed: " << rev << std::endl;
  return 0;
}
