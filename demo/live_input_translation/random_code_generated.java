// Auto-generated from CPG Abstract Program Model
class Random_code {

    public static int get_array_sum(int[] vector) {
        int accumulator = 0;
        for (int iter = 0; (iter < vector.length); iter++) {
            accumulator += vector[iter];
        }
        return accumulator;
    }

    public static void main(String[] args) {
        int[] test_array = new int[]{10, 20, 30, 40, 50};
        System.out.println("Sum: " + get_array_sum(test_array));
    }
}
