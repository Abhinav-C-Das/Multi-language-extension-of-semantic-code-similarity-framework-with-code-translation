// Auto-generated from CPG Abstract Program Model
class Ref1 {

    public static int arrayProduct(int[] arr) {
        int product = 1;
        for (int i = 0; (i < arr.length); i++) {
            product = (product * arr[i]);
        }
        return product;
    }

    public static void main(String[] args) {
        int[] arr = new int[]{1, 2, 3, 4, 5};
        int result = arrayProduct(arr);
        System.out.println("Result: " + result);
    }
}
