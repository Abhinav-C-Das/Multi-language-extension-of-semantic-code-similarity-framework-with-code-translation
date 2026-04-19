// Auto-generated from CPG Abstract Program Model
class Ref1 {

    public static int removeDuplicates(int[] arr) {
        if (((arr.length == 0) || (arr.length == 1))) {
            return arr.length;
        }
        int j = 0;
        for (int i = 0; (i < (arr.length - 1)); i++) {
            if ((arr[i] != arr[(i + 1)])) {
                arr[j++] = arr[i];
            }
        }
        arr[j++] = arr[(arr.length - 1)];
        return j;
    }

    public static void main(String[] args) {
        int[] arr = new int[]{1, 2, 2, 3, 4, 4, 4, 5};
        int n = removeDuplicates(arr);
        System.out.println("Unique Count = " + n);
    }
}
