/**
 * Reference 2: Linear Search — Full Scan (Control Gated)
 * CES: loop_ANY::CONTROL_GATED::ASSIGN
 */
public class ref2_java {
    public static int linearSearch(int[] arr, int target) {
        int result = -1;
        for (int i = 0; i < arr.length; i++) {
            if (arr[i] == target) {
                result = i;
            }
        }
        return result;
    }

    public static void main(String[] args) {
        int[] data = { 1, 5, 2, 8, 3 };
        System.out.println("Idx: " + linearSearch(data, 8));
    }
}
