// Auto-generated from CPG Abstract Program Model
class Ref1 {

    public static int countOdds(int[] arr) {
        int count = 0;
        for (int i = 0; (i < arr.length); i++) {
            if (((arr[i] % 2) != 0)) {
                count++;
            }
        }
        return count;
    }

    public static void main(String[] args) {
        int[] arr = new int[]{12, 35, 1, 10, 34, 1};
        int result = countOdds(arr);
        System.out.println("Result: " + result);
    }
}
