/**
 * Reference 2: Dot Product — sum = sum + a[i] * b[i]
 * CES: loop_ANY::ACCUMULATIVE::ASSIGN
 */
public class ref2_java {
    public static int dotProduct(int[] a, int[] b) {
        int sum = 0;
        for (int i = 0; i < a.length; i++) {
            sum = sum + a[i] * b[i];
        }
        return sum;
    }

    public static void main(String[] args) {
        int[] x = { 1, 3, 5 };
        int[] y = { 2, 4, 6 };
        System.out.println("Dot: " + dotProduct(x, y));
    }
}
