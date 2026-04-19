// Auto-generated from CPG Abstract Program Model
#include <stdio.h>

int countOdds(int arr[], int n) {
    int count = 0;
    for (int i = 0; (i < n); i++) {
        if (((arr[i] % 2) != 0)) {
            count++;
        }
    }
    return count;
}

int main() {
    int arr[] = {12, 35, 1, 10, 34, 1};
    int result = countOdds(arr, 6);
    printf("Result: %d\n", result);
    return 0;
}
