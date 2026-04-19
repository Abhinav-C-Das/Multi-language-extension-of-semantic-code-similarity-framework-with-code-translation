// Auto-generated from CPG Abstract Program Model
#include <iostream>

int fibonacci(int n) {
    if ((n <= 1)) {
        return n;
    }
    int a;
    int b;
    a = 0;
    b = 1;
    for (int i = 2; (i <= n); i++) {
        int temp = (a + b);
        a = b;
        b = temp;
    }
    return b;
}

int main() {
    std::cout << "Fib(7) =" << fibonacci(7) << std::endl;
    return 0;
}
