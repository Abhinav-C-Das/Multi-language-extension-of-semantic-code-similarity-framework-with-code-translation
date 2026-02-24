/**
 * Reference 2: Factorial — Tail Recursion with accumulator
 * CES: rec_ANY::TAIL_RECURSIVE::ACCUMULATE
 * Parameter 'acc' triggers CES tail-recursion detection
 */
public class ref2_java {
    public static long factorial(int n, long acc) {
        if (n <= 1)
            return acc;
        return factorial(n - 1, acc * n);
    }

    public static long factorial(int n) {
        return factorial(n, 1);
    }

    public static void main(String[] args) {
        System.out.println("5! = " + factorial(5));
        System.out.println("10! = " + factorial(10));
    }
}
