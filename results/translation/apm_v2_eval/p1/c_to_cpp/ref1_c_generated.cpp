// Auto-generated from CPG Abstract Program Model
#include <iostream>

int arraySum(int arr[], int n) {
    int sum = 0;
    for (int i = 0; (i < n); i++) {
        sum += arr[i];
    }
    return sum;
}

int main() {
    int arr[] = {5, 10, 15, 20, 25};
    int n = 5;
    std::cout << "Sum = " << arraySum(arr, n) << std::endl;
    return 0;
}
