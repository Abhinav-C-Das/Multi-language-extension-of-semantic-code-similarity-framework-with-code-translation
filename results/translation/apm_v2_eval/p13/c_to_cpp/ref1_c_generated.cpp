// Auto-generated from CPG Abstract Program Model
#include <iostream>

int binarySearch(int arr[], int n, int target) {
    int left = 0;
    int right = (n - 1);
    while ((left <= right)) {
        int mid = (left + ((right - left) / 2));
        if ((arr[mid] == target)) {
            return mid;
        }
        if ((arr[mid] < target)) {
            left = (mid + 1);
        } else {
            right = (mid - 1);
        }
    }
    return -1;
}

int main() {
    int arr[] = {2, 5, 8, 12, 16, 23, 38, 45, 56, 67, 78};
    int n = 11;
    int target = 23;
    int result = binarySearch(arr, n, target);
    std::cout << "Index:" << result << std::endl;
    return 0;
}
