// Auto-generated from CPG Abstract Program Model
class Ref1 {

    public static void reverseArray(int[] arr) {
        int left;
        int right;
        left = 0;
        right = (arr.length - 1);
        while ((left < right)) {
            int temp = arr[left];
            arr[left] = arr[right];
            arr[right] = temp;
            left++;
            right--;
        }
    }

    public static void main(String[] args) {
        int[] arr = new int[]{1, 2, 3, 4, 5};
        reverseArray(arr);
        for (int i = 0; (i < 5); i++) {
            System.out.print("" + arr[i] + " ");
        }
    }
}
