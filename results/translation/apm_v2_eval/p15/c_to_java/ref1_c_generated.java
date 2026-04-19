// Auto-generated from CPG Abstract Program Model
class Ref1 {

    public static int findMinimum(int[] arr) {
        int min = arr[0];
        for (int i = 1; (i < arr.length); i++) {
            if ((arr[i] < min)) {
                min = arr[i];
            }
        }
        return min;
    }

    public static void main(String[] args) {
        int[] arr = new int[]{34, 15, 88, 2, 10};
        int result = findMinimum(arr);
        System.out.println("Result: " + result);
    }
}
