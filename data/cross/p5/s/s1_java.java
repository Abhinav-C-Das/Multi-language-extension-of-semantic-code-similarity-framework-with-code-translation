/**
 * Student 1 — matches ref1 (balance -= expenses[i])
 */
public class s1_java {
    public static int spendTracker(int budget, int[] spendings) {
        int left = budget;
        for (int i = 0; i < spendings.length; i++) {
            left -= spendings[i];
        }
        return left;
    }

    public static void main(String[] args) {
        int[] s = { 50, 30, 20, 45, 15 };
        System.out.println("Left: " + spendTracker(500, s));
    }
}
