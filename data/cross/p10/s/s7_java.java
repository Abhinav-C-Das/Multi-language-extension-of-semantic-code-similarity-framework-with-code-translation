/**
 * Student 7 — matches ref1 (bubble)
 */
public class s7_java {
    public static void bub(int[] a) {
        boolean swapped = true;
        int j = 0;
        int tmp;
        while (swapped) {
            swapped = false;
            j++;
            for (int i = 0; i < a.length - j; i++) {
                if (a[i] > a[i + 1]) {
                    tmp = a[i];
                    a[i] = a[i + 1];
                    a[i + 1] = tmp;
                    swapped = true;
                }
            }
        }
    }

    public static void main(String[] x) {
        bub(new int[] { 2, 1 });
    }
}
