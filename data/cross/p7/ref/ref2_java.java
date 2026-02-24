/**
 * Reference 2: Sum to N — Direct Formula
 * CES: direct::DIRECT_FORMULA::COMPUTE
 */
public class ref2_java {
    public static long sumToN(int n) {
        return (long) n * (n + 1) / 2;
    }

    public static void main(String[] args) {
        System.out.println("Sum 10: " + sumToN(10));
    }
}
