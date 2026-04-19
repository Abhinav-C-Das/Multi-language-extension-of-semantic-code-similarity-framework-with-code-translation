// Auto-generated from CPG Abstract Program Model
#include <stdio.h>

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
    printf("Found at: %d\n", linearSearchRecursive(arr, 20, 0, n));
    return 0;
}
