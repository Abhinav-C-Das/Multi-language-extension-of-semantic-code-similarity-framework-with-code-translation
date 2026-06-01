// Auto-generated from CPG Abstract Program Model
#include <iostream>

int countOccurrences(int arr[], int n, int target) {
    int count = 0;
    for (int i = 0; (i < n); i++) {
        if ((arr[i] == target)) {
            count++;
        }
    }
    return count;
}

int main() {
    int arr[] = {5, 2, 5, 8, 5, 3};
    std::cout << "Count of 5: " << countOccurrences(arr, 6, 5) << std::endl;
    return 0;
}
