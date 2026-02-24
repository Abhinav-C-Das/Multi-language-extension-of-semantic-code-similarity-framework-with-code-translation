/**
 * Student 1 — matches ref1 (head recursion)
 */
public class s1_java {
    public static long fact(int n) {
        if (n <= 1)
            return 1;
        return n * fact(n - 1);
    }

    public static void main(String[] args) {
        System.out.println("Fact 6: " + fact(6));
    }
}
