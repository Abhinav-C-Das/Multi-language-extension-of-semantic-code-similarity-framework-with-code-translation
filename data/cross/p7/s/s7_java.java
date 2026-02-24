/**
 * Student 7 — matches ref1 (loop)
 */
public class s7_java {
    public static long summation(int top) {
        long s = 0;
        for (int k = 1; k <= top; k++)
            s += k;
        return s;
    }

    public static void main(String[] a) {
        System.out.println(summation(5));
    }
}
