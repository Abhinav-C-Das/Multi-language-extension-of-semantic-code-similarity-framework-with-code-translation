// Auto-generated from CPG Abstract Program Model
class Ref1 {

    public static int sumEvens(int[] arr) {
        int sum = 0;
        for (int i = 0; (i < arr.length); i++) {
            if (((arr[i] % 2) == 0)) {
                sum += arr[i];
            }
        }
        return sum;
    }

    public static void main(String[] args) {
        int[] arr = new int[]{1, 2, 3, 4, 5, 6};
        int result = sumEvens(arr);
        System.out.println("Result: " + result);
    }
}
