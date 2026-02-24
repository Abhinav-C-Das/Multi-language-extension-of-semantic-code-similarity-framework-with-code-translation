/**
 * Student 5 — matches ref2 (tail recursion)
 */
public class s5_java {
    public static long factorial(int n, long acc) {
        if (n <= 1)
            return acc;
        return factorial(n - 1, acc * n);
    }

    public static void main(String[] args) {
        System.out.println("Fact 5: " + factorial(5, 1));
    }
}
