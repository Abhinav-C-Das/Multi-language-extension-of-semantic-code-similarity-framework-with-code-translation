// Auto-generated from CPG Abstract Program Model
#include <iostream>

int findMinimum(int arr[], int n) {
    int min = arr[0];
    for (int i = 1; (i < n); i++) {
        if ((arr[i] < min)) {
            min = arr[i];
        }
    }
    return min;
}

int main() {
    int arr[] = {34, 15, 88, 2, 10};
    int result = findMinimum(arr, 5);
    std::cout << "Result: " << result << std::endl;
    return 0;
}
