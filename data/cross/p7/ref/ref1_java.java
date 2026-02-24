/**
 * Reference 1: Sum to N — Iterative Loop
 * CES: loop_ANY::ACCUMULATIVE::ADD
 */
public class ref1_java {
    public static long sumToN(int n) {
        long sum = 0;
        for (int i = 1; i <= n; i++) {
            sum += i;
        }
        return sum;
    }

    public static void main(String[] args) {
        System.out.println("Sum 10: " + sumToN(10));
    }
}
