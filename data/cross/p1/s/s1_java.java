/**
 * Student Submission 1
 * Should match: ref1 (indexed for loop with compound assignment)
 */
public class s1_java {
    public static int computeSum(int[] values) {
        int answer = 0;
        for (int k = 0; k < values.length; k++) {
            answer += values[k];
        }
        return answer;
    }

    public static void main(String[] args) {
        int[] test = { 10, 20, 30, 40, 50 };
        System.out.println("Result: " + computeSum(test));
    }
}
