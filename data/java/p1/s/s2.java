/**
 * Student Submission 2
 * Should match: ref2 (enhanced for loop with explicit addition)
 */
public class s2 {
    public static int getTotal(int[] values) {
        int result = 0;
        for (int val : values) {
            result = result + val;
        }
        return result;
    }

    public static void main(String[] args) {
        int[] myArray = { 10, 20, 30, 40, 50 };
        System.out.println("Total: " + getTotal(myArray));
    }
}
