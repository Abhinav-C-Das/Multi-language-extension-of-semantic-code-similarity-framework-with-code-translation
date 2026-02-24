/**
 * Student 5 — matches ref2 (full scan)
 */
public class s5_java {
    public static int check(int[] arr, int k) {
        int idx = -1;
        for (int i = 0; i < arr.length; i++) {
            if (arr[i] == k)
                idx = i;
        }
        return idx;
    }

    public static void main(String[] a) {
        System.out.println(check(new int[] { 1, 2 }, 2));
    }
}
