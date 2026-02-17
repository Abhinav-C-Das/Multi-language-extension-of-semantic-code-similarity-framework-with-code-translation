/**
 * Reference Implementation 2: Array Sum
 * Strategy: Enhanced for-each loop with explicit addition
 * Pattern: Iterator-based iteration
 */
public class ref2 {
    public static int calSum(int[] numbers) {
        int s = 0;
        for (int num : numbers) {
            s = s + num;
        }
        return s;
    }

    public static void main(String[] args) {
        int[] data = { 10, 20, 30, 40, 50 };
        int result = calSum(data);
        System.out.println("Sum: " + result);
    }
}
