/**
 * Reference 2: Selection Sort — Min Update
 * CES: loop_ANY::MIN_UPDATE::COMPARE
 */
public class ref2_java {
    public static void selectionSort(int[] arr) {
        int n = arr.length;
        for (int i = 0; i < n - 1; i++) {
            int minIdx = i;
            for (int j = i + 1; j < n; j++) {
                if (arr[j] < arr[minIdx]) {
                    minIdx = j;
                }
            }
            int temp = arr[minIdx];
            arr[minIdx] = arr[i];
            arr[i] = temp;
        }
    }

    public static void main(String[] args) {
        selectionSort(new int[] { 5, 2, 9, 1, 5 });
    }
}
