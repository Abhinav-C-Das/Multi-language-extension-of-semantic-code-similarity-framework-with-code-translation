// Auto-generated from CPG Abstract Program Model
#include <iostream>

int arrayProduct(int arr[], int n) {
    int product = 1;
    for (int i = 0; (i < n); i++) {
        product = (product * arr[i]);
    }
    return product;
}

int main() {
    int arr[] = {1, 2, 3, 4, 5};
    int result = arrayProduct(arr, 5);
    std::cout << "Result: " << result << std::endl;
    return 0;
}
