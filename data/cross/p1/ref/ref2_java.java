/**
 * Reference Implementation 2: Array Sum
 * Strategy: While loop with explicit addition (s = s + num)
 * Pattern: Counter-controlled while loop
 */
public class ref2_java {
    public static int calSum(int[] numbers) {
        int s = 0;
        int idx = 0;
        while (idx < numbers.length) {
            s = s + numbers[idx];
            idx++;
        }
        return s;
    }

    public static void main(String[] args) {
        int[] data = {10, 20, 30, 40, 50};
        int result = calSum(data);
        System.out.println("Sum: " + result);
    }
}
