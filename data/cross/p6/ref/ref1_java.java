/**
 * Reference 1: Factorial — Head Recursion
 * CES: rec_ANY::HEAD_RECURSIVE::ADD
 * Computation happens ON RETURN: return n * factorial(n-1)
 */
public class ref1_java {
    public static long factorial(int n) {
        if (n <= 1)
            return 1;
        return n * factorial(n - 1);
    }

    public static void main(String[] args) {
        System.out.println("5! = " + factorial(5));
        System.out.println("10! = " + factorial(10));
    }
}
