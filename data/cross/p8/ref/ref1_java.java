/**
 * Reference 1: Linear Search — Early Exit
 * CES: loop_ANY::SEARCH_WITH_RETURN::EARLY_EXIT
 */
public class ref1_java {
    public static int linearSearch(int[] arr, int target) {
        for (int i = 0; i < arr.length; i++) {
            if (arr[i] == target) {
                return i;
            }
        }
        return -1;
    }

    public static void main(String[] args) {
        int[] data = { 1, 5, 2, 8, 3 };
        System.out.println("Idx: " + linearSearch(data, 8));
    }
}
