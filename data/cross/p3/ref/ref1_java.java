/**
 * Reference Implementation 1: Array Product
 * Strategy: Compound multiplication (*=)
 * CES Pattern: loop_ANY::ACCUMULATIVE::MUL
 */
public class ref1_java {
    public static long arrayProduct(int[] arr) {
        long product = 1;
        for (int i = 0; i < arr.length; i++) {
            product *= arr[i];
        }
        return product;
    }

    public static void main(String[] args) {
        int[] data = { 2, 3, 4, 5 };
        System.out.println("Product: " + arrayProduct(data));
    }
}
