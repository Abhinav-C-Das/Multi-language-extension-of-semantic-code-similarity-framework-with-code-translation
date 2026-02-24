/**
 * Student 7 — matches ref1 (head recursion)
 */
public class s7_java {
    public static long computeFactorial(int n) {
        if (n <= 1)
            return 1;
        return n * computeFactorial(n - 1);
    }

    public static void main(String[] args) {
        System.out.println("Fact 10: " + computeFactorial(10));
    }
}
