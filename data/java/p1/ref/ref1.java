/**
 * Reference Implementation 1: Array Sum
 * Strategy: Indexed for loop with compound assignment (+=)
 * Pattern: Traditional imperative iteration
 */
public class ref1 {
    public static int sumArray(int[] arr) {
        int total = 0;
        for (int i = 0; i < arr.length; i++) {
            total += arr[i];
        }
        return total;
    }

    public static void main(String[] args) {
        int[] numbers = { 10, 20, 30, 40, 50 };
        int result = sumArray(numbers);
        System.out.println("Sum: " + result);
    }
}
