// Auto-generated from CPG Abstract Program Model
class Ref1 {

    public static int countPositives(int[] arr) {
        int count = 0;
        for (int i = 0; (i < arr.length); i++) {
            if ((arr[i] > 0)) {
                count++;
            }
        }
        return count;
    }

    public static void main(String[] args) {
        int[] arr = new int[]{-1, 2, -3, 4, 5, -6};
        int result = countPositives(arr);
        System.out.println("Result: " + result);
    }
}
