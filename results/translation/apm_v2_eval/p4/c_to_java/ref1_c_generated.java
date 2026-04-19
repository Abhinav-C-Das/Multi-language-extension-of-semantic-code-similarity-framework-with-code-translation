// Auto-generated from CPG Abstract Program Model
class Ref1 {

    public static int linearSearch(int[] arr, int target) {
        for (int i = 0; (i < arr.length); i++) {
            if ((arr[i] == target)) {
                return i;
            }
        }
        return -1;
    }

    public static void main(String[] args) {
        int[] arr = new int[]{10, 23, 45, 67, 89};
        System.out.println("Index: " + linearSearch(arr, 45));
    }
}
