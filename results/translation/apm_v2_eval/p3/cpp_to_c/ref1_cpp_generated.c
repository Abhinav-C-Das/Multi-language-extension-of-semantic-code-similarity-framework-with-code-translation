// Auto-generated from CPG Abstract Program Model
#include <stdio.h>

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
    printf("Count of 5: %d\n", countOccurrences(arr, 6, 5));
    return 0;
}
