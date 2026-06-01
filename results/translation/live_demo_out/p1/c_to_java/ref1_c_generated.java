// Auto-generated from CPG Abstract Program Model
class Ref1 {

    public static int arraySum(int[] arr) {
        int sum = 0;
        for (int i = 0; (i < arr.length); i++) {
            sum += arr[i];
        }
        return sum;
    }

    public static void main(String[] args) {
        int[] arr = new int[]{5, 10, 15, 20, 25};
        int n = 5;
        System.out.println("Sum = " + arraySum(arr));
    }
}
