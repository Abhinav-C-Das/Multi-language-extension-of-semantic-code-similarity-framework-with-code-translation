// Auto-generated from CPG Abstract Program Model
class Ref1 {

    public static int isPrime(int n) {
        if ((n <= 1)) {
            return 0;
        }
        for (int i = 2; ((i * i) <= n); i++) {
            if (((n % i) == 0)) {
                return 0;
            }
        }
        return 1;
    }

    public static void main(String[] args) {
        System.out.println("Is 17 prime?" + isPrime(17));
    }
}
