// Auto-generated from CPG Abstract Program Model
#include <iostream>

int linearSearchRecursive(int arr[], int target, int index, int n) {
    if ((index >= n)) {
        return -1;
    }
    if ((arr[index] == target)) {
        return index;
    }
    return linearSearchRecursive(arr, target, (index + 1), n);
}

int main() {
    int arr[] = {5, 10, 15, 20, 25};
    int n = 5;
    std::cout << "Found at: " << linearSearchRecursive(arr, 20, 0, n) << std::endl;
    return 0;
}
