/**
 * Reference 1: Bubble Sort — Conditional Swap
 * CES: loop_ANY::CONDITIONAL_SWAP::ASSIGN
 */
public class ref1_java {
    public static void bubbleSort(int[] arr) {
        int n = arr.length;
        for (int i = 0; i < n - 1; i++) {
            for (int j = 0; j < n - i - 1; j++) {
                if (arr[j] > arr[j + 1]) {
                    int temp = arr[j];
                    arr[j] = arr[j + 1];
                    arr[j + 1] = temp;
                }
            }
        }
    }

    public static void main(String[] args) {
        bubbleSort(new int[] { 5, 2, 9, 1, 5 });
    }
}
