/**
 * Reference Implementation 2: Array Product
 * Strategy: Explicit assignment (= product * arr[i])
 * CES Pattern: loop_ANY::ACCUMULATIVE::ASSIGN
 */
public class ref2_java {
    public static long arrayProduct(int[] arr) {
        long product = 1;
        for (int i = 0; i < arr.length; i++) {
            product = product * arr[i];
        }
        return product;
    }

    public static void main(String[] args) {
        int[] data = { 2, 3, 4, 5 };
        System.out.println("Product: " + arrayProduct(data));
    }
}
