// Auto-generated from CPG Abstract Program Model
class Ref1 {

    public static int findMax(int[] arr) {
        int max = arr[0];
        for (int i = 1; (i < arr.length); i++) {
            if ((arr[i] > max)) {
                max = arr[i];
            }
        }
        return max;
    }

    public static void main(String[] args) {
        int[] arr = new int[]{12, 45, 23, 67, 34, 89, 21};
        System.out.println("Max = " + findMax(arr));
    }
}
