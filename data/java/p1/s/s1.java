/**
 * Student Submission 1
 * Should match: ref1 (indexed for loop with compound assignment)
 */
public class s1 {
    public static int simpleSum(int[] arr) {
        int res = 0;
        for (int j = 0; j < arr.length; j++) {
            res += arr[j];
        }
        return res;
    }

    public static void main(String[] args) {
        int[] test = { 10, 20, 30, 40, 50 };
        System.out.println("Result: " + simpleSum(test));
    }
}
